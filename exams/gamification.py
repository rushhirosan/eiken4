"""Session feedback and unlock progress display helpers."""

from django.db.models import Sum
from django.utils import timezone

MOCK_EXAM_UNLOCK_MIN_RATE = 80
RANDOM_UNLOCK_MIN_RATE = 20


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


def _count_today_attempts_for_level(user, level):
    from .models import DailyProgress

    today = timezone.localdate()
    total = DailyProgress.objects.filter(
        user=user,
        level=str(level),
        date=today,
    ).aggregate(total=Sum('questions_attempted'))['total']
    return total or 0


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
