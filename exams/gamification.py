"""Session feedback and unlock progress display helpers."""

from django.urls import reverse
from django.utils import timezone

MOCK_EXAM_UNLOCK_MIN_RATE = 80
RANDOM_UNLOCK_MIN_RATE = 20
DAILY_MISSION_GOAL_OPTIONS = (3, 5, 10)
DEFAULT_DAILY_MISSION_GOAL = 3
DAILY_MISSION_GOAL_SESSION_KEY = 'daily_mission_goal'
MISSION_CATEGORY_ORDER = (
    'grammar_fill',
    'conversation_fill',
    'word_order',
    'reading_comprehension',
    'writing',
    'listening_illustration',
    'listening_conversation',
    'listening_passage',
)
MISSION_TYPE_LABELS = {
    'grammar_fill': '文法・語彙問題',
    'conversation_fill': '会話補充問題',
    'word_order': '語順選択問題',
    'reading_comprehension': '長文読解問題',
    'writing': 'ライティング問題',
    'listening_illustration': 'リスニング第1部',
    'listening_conversation': 'リスニング第2部',
    'listening_passage': 'リスニング第3部',
}
MISSION_SHORT_LABELS = {
    'grammar_fill': '文法・語彙',
    'conversation_fill': '会話補充',
    'word_order': '語順選択',
    'reading_comprehension': '長文読解',
    'writing': 'ライティング',
    'listening_illustration': 'リスニング第1部',
    'listening_conversation': 'リスニング第2部',
    'listening_passage': 'リスニング第3部',
}


def enrich_foundation_progress(category_progress):
    """Add mock-exam remaining rate to each foundation category row."""
    enriched = []
    for item in category_progress:
        rate = item['progress_rate']
        counts_toward_mock = item.get('counts_toward_mock', True)
        enriched.append({
            **item,
            'remaining_to_mock': (
                max(0.0, MOCK_EXAM_UNLOCK_MIN_RATE - rate)
                if counts_toward_mock
                else None
            ),
            'meets_random_threshold': rate >= RANDOM_UNLOCK_MIN_RATE,
            'counts_toward_mock': counts_toward_mock,
        })
    return enriched


def build_adventure_summary(unlock_status):
    """UI-friendly summary for the exam list adventure progress card."""
    random_status = unlock_status['random']
    mock_status = unlock_status['mock_exam']
    foundation = unlock_status.get('foundation_progress', [])
    remaining = mock_status.get('remaining_categories') or []

    mock_cleared = sum(
        1 for item in foundation if item['progress_rate'] >= MOCK_EXAM_UNLOCK_MIN_RATE
    )
    nearest_remaining = None
    if remaining:
        nearest_remaining = min(remaining, key=lambda item: item['remaining_rate'])

    return {
        'random_unlocked': random_status['is_unlocked'],
        'random_ready_count': random_status['ready_count'],
        'random_required_count': random_status['required_count'],
        'random_required_rate': random_status['required_rate'],
        'mock_unlocked': mock_status['is_unlocked'],
        'mock_cleared_count': mock_cleared,
        'mock_total_count': len(foundation),
        'mock_required_rate': mock_status['required_rate'],
        'remaining_categories': remaining,
        'nearest_remaining': nearest_remaining,
    }


def store_pre_submit_unlock_snapshot(request, unlock_status, level):
    """Remember unlock flags before a submit batch updates progress."""
    request.session[f'pre_submit_unlock_{level}'] = {
        'random': unlock_status['random']['is_unlocked'],
        'mock_exam': unlock_status['mock_exam']['is_unlocked'],
    }
    request.session.modified = True


def pop_pre_submit_unlock_snapshot(request, level):
    """Return and clear the pre-submit unlock snapshot for a level."""
    return request.session.pop(f'pre_submit_unlock_{level}', None)


def normalize_daily_mission_goal(goal):
    """Return a valid daily mission goal (3, 5, or 10)."""
    try:
        goal = int(goal)
    except (TypeError, ValueError):
        return DEFAULT_DAILY_MISSION_GOAL
    if goal in DAILY_MISSION_GOAL_OPTIONS:
        return goal
    return DEFAULT_DAILY_MISSION_GOAL


def get_daily_mission_goal(request):
    """Read the user's daily question goal from the session."""
    raw = request.session.get(DAILY_MISSION_GOAL_SESSION_KEY, DEFAULT_DAILY_MISSION_GOAL)
    return normalize_daily_mission_goal(raw)


def set_daily_mission_goal(request, goal):
    """Persist the daily question goal in the session."""
    normalized = normalize_daily_mission_goal(goal)
    request.session[DAILY_MISSION_GOAL_SESSION_KEY] = normalized
    request.session.modified = True
    return normalized


def _count_today_attempts_for_type(user, level, question_type):
    """Count today's answer records for one question type at a level."""
    if user is None:
        return 0

    from questions.models import ListeningUserAnswer

    from .models import ReadingUserAnswer, UserAnswer, WritingUserAnswer

    today = timezone.localdate()
    level_str = str(level)
    filters = {'user': user, 'answered_at__date': today}

    if question_type == 'listening_illustration':
        return ListeningUserAnswer.objects.filter(
            question__level=level_str,
            **filters,
        ).count()
    if question_type == 'reading_comprehension':
        return ReadingUserAnswer.objects.filter(
            reading_question__passage__level=level_str,
            **filters,
        ).count()
    if question_type == 'writing':
        return WritingUserAnswer.objects.filter(
            question__level=level_str,
            **filters,
        ).count()
    return UserAnswer.objects.filter(
        question__level=level_str,
        question__question_type=question_type,
        **filters,
    ).count()


def _question_list_url(level, question_type, num_questions):
    base = reverse('exams:question_list_by_level', kwargs={'level': str(level)})
    return f'{base}?type={question_type}&num_questions={num_questions}'


def build_daily_missions(*, user, level, unlock_status, foundation_progress_by_type, daily_goal):
    """
    Build up to three daily mission rows for the exam list card.
    Returns {daily_goal, daily_goal_options, items, all_complete}.
    """
    daily_goal = normalize_daily_mission_goal(daily_goal)
    today_total = _count_today_attempts_for_level(user, level)
    items = []

    items.append({
        'kind': 'daily_total',
        'label': f'今日{daily_goal}問解く',
        'progress_text': f'{min(today_total, daily_goal)}/{daily_goal}',
        'completed': today_total >= daily_goal,
        'url': None,
    })

    nearest_type = None
    mock_unlocked = unlock_status['mock_exam']['is_unlocked']
    if not mock_unlocked:
        remaining = unlock_status['mock_exam'].get('remaining_categories') or []
        if remaining:
            nearest = min(remaining, key=lambda item: item['remaining_rate'])
            nearest_type = nearest['question_type']
            progress_rate = nearest['progress_rate']
            short_name = MISSION_TYPE_LABELS.get(
                nearest_type,
                nearest.get('display_name', nearest_type),
            )
            remaining_to_mock = nearest.get('remaining_rate', MOCK_EXAM_UNLOCK_MIN_RATE - progress_rate)
            session_size = min(daily_goal, 10)
            items.append({
                'kind': 'nearest_mock',
                'label': f'{short_name}を進めよう',
                'progress_text': (
                    f'取り組み {progress_rate:.0f}% · 模擬まであと{remaining_to_mock:.0f}%'
                ),
                'completed': progress_rate >= MOCK_EXAM_UNLOCK_MIN_RATE,
                'url': _question_list_url(
                    level,
                    nearest_type,
                    session_size,
                ),
                'question_type': nearest_type,
            })

    available_types = [
        question_type
        for question_type in MISSION_CATEGORY_ORDER
        if question_type in foundation_progress_by_type
    ]
    for question_type in available_types:
        if question_type == nearest_type:
            continue
        if _count_today_attempts_for_type(user, level, question_type) > 0:
            continue
        short_name = MISSION_SHORT_LABELS.get(
            question_type,
            MISSION_TYPE_LABELS.get(
                question_type,
                foundation_progress_by_type[question_type].get('display_name', question_type),
            ),
        )
        num_questions = 1 if question_type == 'reading_comprehension' else 3
        items.append({
            'kind': 'untouched_today',
            'label': f'{short_name}を{num_questions}問',
            'progress_text': f'0/{num_questions}',
            'completed': False,
            'url': _question_list_url(level, question_type, num_questions),
            'question_type': question_type,
        })
        break

    visible_items = items[:3]
    all_complete = bool(visible_items) and all(item['completed'] for item in visible_items)

    return {
        'daily_goal': daily_goal,
        'daily_goal_options': list(DAILY_MISSION_GOAL_OPTIONS),
        'items': visible_items,
        'all_complete': all_complete,
    }


def _count_today_attempts_for_level(user, level):
    """Count answer records for today at this level (includes the current session)."""
    if user is None:
        return 0

    from questions.models import ListeningUserAnswer

    from .models import ReadingUserAnswer, UserAnswer, WritingUserAnswer

    today = timezone.localdate()
    level_str = str(level)
    filters = {'user': user, 'answered_at__date': today}

    counts = [
        UserAnswer.objects.filter(question__level=level_str, **filters).count(),
        WritingUserAnswer.objects.filter(question__level=level_str, **filters).count(),
        ReadingUserAnswer.objects.filter(
            reading_question__passage__level=level_str,
            **filters,
        ).count(),
        ListeningUserAnswer.objects.filter(question__level=level_str, **filters).count(),
    ]
    return sum(counts)


def build_session_achievements(
    *,
    user,
    level,
    question_type,
    correct_count,
    total_count,
    unlock_status,
    pre_unlock=None,
    session_count=0,
):
    """
    Build up to two short achievement lines for the answer results page.
    Each item: {text, variant} where variant is bootstrap alert suffix.
    """
    messages = []

    if question_type == 'writing':
        if total_count > 0:
            messages.append({
                'text': '提出おつかれさま！参考解答と比べて確認しよう',
                'variant': 'info',
            })
        return messages[:2]

    if total_count <= 0:
        return messages

    if correct_count == total_count:
        messages.append({
            'text': 'パーフェクト！ぜんぶ正解だよ',
            'variant': 'success',
        })
    elif correct_count / total_count >= 0.8:
        messages.append({
            'text': 'よくがんばった！あと一歩',
            'variant': 'success',
        })
    elif correct_count / total_count >= 0.5:
        messages.append({
            'text': 'いい調子！間違えたところを見直そう',
            'variant': 'info',
        })

    today_total = _count_today_attempts_for_level(user, level)
    if session_count > 0 and today_total <= session_count:
        messages.append({
            'text': '今日のスタート、ナイス！',
            'variant': 'info',
        })

    if pre_unlock:
        if not pre_unlock.get('random') and unlock_status['random']['is_unlocked']:
            messages.append({
                'text': 'ランダム10問が解放された！',
                'variant': 'success',
            })
        if not pre_unlock.get('mock_exam') and unlock_status['mock_exam']['is_unlocked']:
            messages.append({
                'text': '模擬試験が解放された！挑戦してみよう',
                'variant': 'success',
            })

    if len(messages) < 2 and not unlock_status['mock_exam']['is_unlocked']:
        remaining = unlock_status['mock_exam'].get('remaining_categories') or []
        if remaining:
            nearest = min(remaining, key=lambda item: item['remaining_rate'])
            if nearest['remaining_rate'] <= 40:
                messages.append({
                    'text': (
                        f"模擬試験まであと{nearest['remaining_rate']:.0f}%"
                        f"（{nearest['display_name']}）"
                    ),
                    'variant': 'info',
                })

    deduped = []
    seen_texts = set()
    for msg in messages:
        if msg['text'] in seen_texts:
            continue
        seen_texts.add(msg['text'])
        deduped.append(msg)
        if len(deduped) >= 2:
            break
    return deduped
