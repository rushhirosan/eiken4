"""Session feedback, habits, badges, and unlock progress display helpers."""

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

MOCK_EXAM_UNLOCK_MIN_RATE = 80
RANDOM_UNLOCK_MIN_RATE = 20
DAILY_MISSION_GOAL_OPTIONS = (3, 5, 10)
DEFAULT_DAILY_MISSION_GOAL = 3
DAILY_MISSION_GOAL_SESSION_KEY = 'daily_mission_goal'
SESSION_ACHIEVEMENT_MAX = 3
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
LISTENING_QUESTION_TYPES = (
    'listening_illustration',
    'listening_conversation',
    'listening_passage',
)
WEEK_ACTIVE_DAYS_REQUIRED = 5
WEEK_ACTIVE_WINDOW_DAYS = 7
BADGE_DEFINITIONS = {
    'first_mock': {
        'label': 'はじめての模擬',
        'icon': '🏁',
        'description': '模擬試験に初めて挑戦した',
    },
    'first_random': {
        'label': 'ランダム10問デビュー',
        'icon': '🎲',
        'description': 'ランダム10問を初めて完了した',
    },
    'first_reading': {
        'label': '読解デビュー',
        'icon': '📖',
        'description': '長文読解に初めて挑戦した',
    },
    'first_writing': {
        'label': 'ライティングデビュー',
        'icon': '✍️',
        'description': 'ライティングを初めて提出した',
    },
    'listening_all': {
        'label': 'リスニングぜんぶ',
        'icon': '🎧',
        'description': 'リスニング第1〜3部すべてに触れた',
    },
    'total_50': {
        'label': '50問の仲間入り',
        'icon': '⭐',
        'description': '累計50問に到達した',
    },
    'total_100': {
        'label': '100問の仲間入り',
        'icon': '🌟',
        'description': '累計100問に到達した',
    },
    'week_active': {
        'label': '1週間チャレンジ',
        'icon': '📅',
        'description': '7日間で5日以上学習した',
    },
}
# 級固有バッジ（未指定は全級で表示）
BADGE_LEVELS = {
    'first_writing': ('3',),
}


def badge_ids_for_level(level):
    """Return badge ids visible for the given exam level."""
    level_str = str(level)
    return [
        badge_id
        for badge_id in BADGE_DEFINITIONS
        if BADGE_LEVELS.get(badge_id) is None or level_str in BADGE_LEVELS[badge_id]
    ]
# 回答結果の達成バナー文言（小学生・中学生向け。正答率より「続けた・見直す」を優先）
ACHIEVEMENT_COPY = {
    'writing_done': '提出おつかれさま！模範解答と見比べてみよう',
    'score_perfect': 'ぜんぶ正解！とてもよくできたね',
    'score_high': 'よくできた！解説であと一歩を確認しよう',
    'score_mid': 'ちゃんと取り組めたね。間違えたところを見直そう',
    'score_low': 'おつかれさま。解説を読んで、もう一度チャレンジしてみよう',
    'today_start': '今日の学習スタート、ナイス！',
    'unlock_random': 'ランダム10問が解放された！挑戦してみよう',
    'unlock_mock': '模擬試験が解放された！いつでも挑戦できるよ',
    'mission_complete': '今日のミッション達成！おつかれさま',
}
MOCK_NEAR_REMAINING_MAX = 80
MOCK_REMAINING_COPY_NEAR = 15
MOCK_REMAINING_COPY_MID = 40


def format_mock_remaining_message(remaining_rate, display_name):
    """Return tiered encouragement copy for mock-exam progress on answer results."""
    remaining = round(float(remaining_rate))
    suffix = f"模擬試験まであと{remaining}%（{display_name}）"
    if remaining <= MOCK_REMAINING_COPY_NEAR:
        return f"あと少し！{suffix}"
    if remaining <= MOCK_REMAINING_COPY_MID:
        return f"この調子！{suffix}"
    return suffix


def select_mock_remaining_category(remaining_categories, question_type):
    """Prefer the category just practiced; otherwise pick the nearest to mock unlock."""
    if not remaining_categories:
        return None
    for item in remaining_categories:
        if item.get('question_type') == question_type:
            return item
    return min(remaining_categories, key=lambda item: item['remaining_rate'])


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


def _daily_mission_goal_session_key(level):
    """Session key for daily mission goal scoped to an exam level."""
    return f'{DAILY_MISSION_GOAL_SESSION_KEY}_{str(level)}'


def get_daily_mission_goal(request, level='4'):
    """Read the user's daily question goal for the given exam level."""
    key = _daily_mission_goal_session_key(level)
    if key in request.session:
        return normalize_daily_mission_goal(request.session[key])
    # Legacy single key (pre-level-scoping) applies to 4級 only.
    if str(level) == '4' and DAILY_MISSION_GOAL_SESSION_KEY in request.session:
        return normalize_daily_mission_goal(request.session[DAILY_MISSION_GOAL_SESSION_KEY])
    return DEFAULT_DAILY_MISSION_GOAL


def set_daily_mission_goal(request, goal, level='4'):
    """Persist the daily question goal for the given exam level."""
    normalized = normalize_daily_mission_goal(goal)
    request.session[_daily_mission_goal_session_key(level)] = normalized
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


def _append_habit_session_achievements(
    messages,
    *,
    user,
    level,
    daily_goal=None,
    session_count=0,
    streak_incremented=False,
    streak_count=0,
):
    """Add daily-mission and streak lines after a submitted session."""
    if daily_goal and user and session_count > 0:
        today_total = _count_today_attempts_for_level(user, level)
        before_total = today_total - session_count
        goal = normalize_daily_mission_goal(daily_goal)
        if before_total < goal <= today_total:
            messages.append({
                'text': ACHIEVEMENT_COPY['mission_complete'],
                'variant': 'success',
            })

    if streak_incremented and streak_count >= 1:
        messages.append({
            'text': f'🔥 {streak_count}日連続！いい調子',
            'variant': 'success',
        })


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
    daily_goal=None,
    streak_incremented=False,
    streak_count=0,
):
    """
    Build up to three short achievement lines for the answer results page.
    Each item: {text, variant} where variant is bootstrap alert suffix.
    """
    messages = []

    if question_type == 'writing':
        if total_count > 0:
            messages.append({
                'text': ACHIEVEMENT_COPY['writing_done'],
                'variant': 'info',
            })
    elif total_count > 0:
        accuracy = correct_count / total_count
        if correct_count == total_count:
            messages.append({
                'text': ACHIEVEMENT_COPY['score_perfect'],
                'variant': 'success',
            })
        elif accuracy >= 0.8:
            messages.append({
                'text': ACHIEVEMENT_COPY['score_high'],
                'variant': 'success',
            })
        elif accuracy >= 0.5:
            messages.append({
                'text': ACHIEVEMENT_COPY['score_mid'],
                'variant': 'info',
            })
        else:
            messages.append({
                'text': ACHIEVEMENT_COPY['score_low'],
                'variant': 'info',
            })

    if pre_unlock:
        if not pre_unlock.get('random') and unlock_status['random']['is_unlocked']:
            messages.append({
                'text': ACHIEVEMENT_COPY['unlock_random'],
                'variant': 'success',
            })
        if not pre_unlock.get('mock_exam') and unlock_status['mock_exam']['is_unlocked']:
            messages.append({
                'text': ACHIEVEMENT_COPY['unlock_mock'],
                'variant': 'success',
            })

    _append_habit_session_achievements(
        messages,
        user=user,
        level=level,
        daily_goal=daily_goal,
        session_count=session_count,
        streak_incremented=streak_incremented,
        streak_count=streak_count,
    )

    today_total = _count_today_attempts_for_level(user, level)
    if session_count > 0 and today_total <= session_count:
        messages.append({
            'text': ACHIEVEMENT_COPY['today_start'],
            'variant': 'info',
        })

    if len(messages) < SESSION_ACHIEVEMENT_MAX and not unlock_status['mock_exam']['is_unlocked']:
        remaining = unlock_status['mock_exam'].get('remaining_categories') or []
        if remaining:
            focus = select_mock_remaining_category(remaining, question_type)
            if focus and focus['remaining_rate'] <= MOCK_NEAR_REMAINING_MAX:
                messages.append({
                    'text': format_mock_remaining_message(
                        focus['remaining_rate'],
                        focus['display_name'],
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
        if len(deduped) >= SESSION_ACHIEVEMENT_MAX:
            break
    return deduped


def _week_start(value):
    """Return Monday of the week containing value."""
    return value - timedelta(days=value.weekday())


def _freeze_available(streak, today):
    """Whether the one-day grace can still be used this week."""
    if streak.freeze_week_start is None:
        return True
    return streak.freeze_week_start < _week_start(today)


def _get_or_create_streak(user):
    from .models import UserStreak

    streak, _ = UserStreak.objects.get_or_create(
        user=user,
        defaults={
            'current_streak': 0,
            'longest_streak': 0,
        },
    )
    return streak


def record_streak_activity(user):
    """Update streak after a completed study session.

    Returns (streak, incremented_today) where incremented_today is True when
    this session newly counts toward today's streak.
    """
    if user is None or not getattr(user, 'is_authenticated', False):
        return None, False

    today = timezone.localdate()
    streak = _get_or_create_streak(user)

    if streak.last_active_date == today:
        return streak, False

    if streak.last_active_date is None:
        streak.current_streak = 1
    else:
        gap = (today - streak.last_active_date).days
        if gap == 1:
            streak.current_streak += 1
        elif gap == 2 and _freeze_available(streak, today):
            streak.current_streak += 1
            streak.freeze_week_start = _week_start(today)
        else:
            streak.current_streak = 1

    streak.last_active_date = today
    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak
    streak.save(update_fields=[
        'current_streak',
        'longest_streak',
        'last_active_date',
        'freeze_week_start',
    ])
    return streak, True


def build_streak_summary(user):
    """Read-only streak display data for the exam list."""
    if user is None or not getattr(user, 'is_authenticated', False):
        return None

    streak = _get_or_create_streak(user)
    today = timezone.localdate()

    if streak.last_active_date is None:
        return {
            'current_streak': 0,
            'longest_streak': 0,
            'studied_today': False,
            'hint': None,
        }

    days_since = (today - streak.last_active_date).days
    studied_today = days_since == 0
    effective_streak = streak.current_streak

    if days_since == 0:
        hint = None
    elif days_since == 1:
        hint = '今日1問で続けよう'
        effective_streak = streak.current_streak
    elif days_since == 2 and _freeze_available(streak, today):
        hint = '今日1問で続けよう'
        effective_streak = streak.current_streak
    else:
        effective_streak = 0
        hint = '今日1問でまたスタート'

    return {
        'current_streak': effective_streak,
        'longest_streak': streak.longest_streak,
        'studied_today': studied_today,
        'hint': hint,
    }


def _count_total_attempts(user):
    if user is None:
        return 0

    from questions.models import ListeningUserAnswer

    from .models import ReadingUserAnswer, UserAnswer, WritingUserAnswer

    return sum([
        UserAnswer.objects.filter(user=user).count(),
        WritingUserAnswer.objects.filter(user=user).count(),
        ReadingUserAnswer.objects.filter(user=user).count(),
        ListeningUserAnswer.objects.filter(user=user).count(),
    ])


def _collect_activity_dates(user, *, since=None):
    if user is None:
        return set()

    from questions.models import ListeningUserAnswer

    from .models import ReadingUserAnswer, UserAnswer, WritingUserAnswer

    dates = set()
    filters = {'user': user}
    if since is not None:
        filters['answered_at__date__gte'] = since

    for model in (
        UserAnswer,
        WritingUserAnswer,
        ReadingUserAnswer,
        ListeningUserAnswer,
    ):
        dates.update(model.objects.filter(**filters).dates('answered_at', 'day'))
    return dates


def _badge_row(badge_id, *, earned=False, earned_at=None):
    definition = BADGE_DEFINITIONS[badge_id]
    return {
        'id': badge_id,
        'label': definition['label'],
        'icon': definition['icon'],
        'description': definition['description'],
        'earned': earned,
        'earned_at': earned_at,
    }


def build_badge_collection(user, level=None):
    """All badge slots with earned state for the modal."""
    badge_ids = badge_ids_for_level(level) if level is not None else list(BADGE_DEFINITIONS)
    if user is None or not getattr(user, 'is_authenticated', False):
        return {
            'earned_count': 0,
            'total_count': len(badge_ids),
            'items': [],
        }

    from .models import UserBadge

    earned_map = {
        badge.badge_id: badge.earned_at
        for badge in UserBadge.objects.filter(user=user)
    }
    items = [
        _badge_row(
            badge_id,
            earned=badge_id in earned_map,
            earned_at=earned_map.get(badge_id),
        )
        for badge_id in badge_ids
    ]
    earned_count = sum(1 for item in items if item['earned'])
    return {
        'earned_count': earned_count,
        'total_count': len(badge_ids),
        'items': items,
    }


def award_new_badges(user, *, question_type):
    """Evaluate and persist newly earned badges. Returns display rows."""
    if user is None or not getattr(user, 'is_authenticated', False):
        return []

    from .models import UserBadge, UserProgress

    earned_ids = set(
        UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
    )
    newly_earned = []

    def try_award(badge_id):
        if badge_id in earned_ids or badge_id not in BADGE_DEFINITIONS:
            return
        UserBadge.objects.create(user=user, badge_id=badge_id)
        earned_ids.add(badge_id)
        newly_earned.append(badge_id)

    if question_type == 'mock_exam':
        try_award('first_mock')
    if question_type == 'random':
        try_award('first_random')
    if question_type == 'reading_comprehension':
        try_award('first_reading')
    if question_type == 'writing':
        try_award('first_writing')

    attempted_types = set(
        UserProgress.objects.filter(
            user=user,
            total_attempts__gt=0,
        ).values_list('question_type', flat=True)
    )
    if all(question_type in attempted_types for question_type in LISTENING_QUESTION_TYPES):
        try_award('listening_all')

    total_attempts = _count_total_attempts(user)
    if total_attempts >= 50:
        try_award('total_50')
    if total_attempts >= 100:
        try_award('total_100')

    since = timezone.localdate() - timedelta(days=WEEK_ACTIVE_WINDOW_DAYS - 1)
    if len(_collect_activity_dates(user, since=since)) >= WEEK_ACTIVE_DAYS_REQUIRED:
        try_award('week_active')

    return [_badge_row(badge_id, earned=True) for badge_id in newly_earned]


def build_habit_summary(user, level=None):
    """Compact streak + badge count for the exam list header."""
    streak = build_streak_summary(user)
    badges = build_badge_collection(user, level=level)
    if streak is None:
        return None
    return {
        'streak': streak,
        'badges': badges,
    }


def process_gamification_after_session(user, *, question_type):
    """Update streak and award badges after a submitted session."""
    _, streak_incremented = record_streak_activity(user)
    new_badges = award_new_badges(user, question_type=question_type)
    habit_summary = build_habit_summary(user)
    streak_count = 0
    if habit_summary and habit_summary.get('streak'):
        streak_count = habit_summary['streak']['current_streak']
    return {
        'new_badges': new_badges,
        'habit_summary': habit_summary,
        'streak_incremented': streak_incremented,
        'streak_count': streak_count,
    }
