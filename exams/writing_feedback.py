"""Rule-based self-check feedback for Eiken writing submissions (Phase 1)."""

from __future__ import annotations

import re
from typing import Any

WORD_TOKEN_RE = re.compile(r"[A-Za-z']+")
WORD_RANGE_RE = re.compile(
    r'語数の目安[^\d]*(\d+)\s*[～〜\-]\s*(\d+)',
)
SENTENCE_SPLIT_RE = re.compile(r'[.!?]+')

# メール返信の定型（語数カウントから除く）
_EMAIL_BOILERPLATE_RES = (
    re.compile(r'^\s*Hi,?\s*James!?\s*$', re.IGNORECASE),
    re.compile(r"^\s*Thank you for your e-?mail\.?\s*$", re.IGNORECASE),
    re.compile(r'^\s*Best wishes,?\s*$', re.IGNORECASE),
)

SHORT_RATIO = 0.7
LONG_RATIO = 1.3


def parse_writing_rubric(question_text: str) -> dict[str, Any] | None:
    """Extract rubric metadata from a writing question prompt."""
    if not question_text:
        return None

    range_match = WORD_RANGE_RE.search(question_text)
    if not range_match:
        return None

    word_min = int(range_match.group(1))
    word_max = int(range_match.group(2))
    if word_min > word_max:
        word_min, word_max = word_max, word_min

    normalized = question_text.replace(' ', '')
    if '2つの質問' in normalized or 'James' in question_text:
        kind = 'email_reply'
        return {
            'kind': kind,
            'word_min': word_min,
            'word_max': word_max,
            'count_body_only': True,
        }

    if '2つの英文' in normalized or 'QUESTION' in question_text:
        return {
            'kind': 'opinion',
            'word_min': word_min,
            'word_max': word_max,
            'sentence_min': 2,
            'sentence_max': 2,
            'count_body_only': False,
        }

    return {
        'kind': 'unknown',
        'word_min': word_min,
        'word_max': word_max,
        'count_body_only': False,
    }


def get_writing_rubric(question) -> dict[str, Any] | None:
    """Return stored rubric or parse from question text."""
    stored = getattr(question, 'writing_rubric', None)
    if stored:
        return stored
    return parse_writing_rubric(question.question_text or '')


def count_english_words(text: str) -> int:
    return len(WORD_TOKEN_RE.findall(text or ''))


def count_sentences(text: str) -> int:
    """Rough sentence count for learner English (split on . ! ?)."""
    if not (text or '').strip():
        return 0
    parts = [part.strip() for part in SENTENCE_SPLIT_RE.split(text) if part.strip()]
    return len(parts)


def extract_email_body(text: str) -> str:
    """Keep lines between boilerplate greeting and Best wishes."""
    body_lines: list[str] = []
    past_thank_you = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if past_thank_you:
                body_lines.append('')
            continue
        if any(pattern.match(stripped) for pattern in _EMAIL_BOILERPLATE_RES):
            if re.match(r"^\s*Thank you for your e-?mail", stripped, re.IGNORECASE):
                past_thank_you = True
            if re.match(r'^\s*Best wishes', stripped, re.IGNORECASE):
                break
            continue
        if past_thank_you:
            body_lines.append(stripped)
    if body_lines:
        return '\n'.join(body_lines).strip()
    # Fallback: entire text minus obvious boilerplate lines
    kept = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if any(pattern.match(stripped) for pattern in _EMAIL_BOILERPLATE_RES):
            continue
        kept.append(stripped)
    return '\n'.join(kept).strip()


def text_for_word_count(response_text: str, rubric: dict[str, Any]) -> str:
    if rubric.get('count_body_only'):
        body = extract_email_body(response_text)
        return body if body else response_text
    return response_text


def _word_count_message(word_count: int, word_min: int, word_max: int) -> dict[str, str]:
    soft_min = int(word_min * SHORT_RATIO)
    soft_max = int(word_max * LONG_RATIO)
    range_label = f'{word_min}〜{word_max}語'

    if word_count < soft_min:
        return {
            'level': 'warn',
            'message': (
                f'語数: {word_count}語（目安 {range_label}）'
                ' — かなり短いようです。内容が足りているか確認しましょう。'
            ),
        }
    if word_count < word_min:
        return {
            'level': 'warn',
            'message': (
                f'語数: {word_count}語（目安 {range_label}）'
                ' — やや短めです。'
            ),
        }
    if word_count > soft_max:
        return {
            'level': 'warn',
            'message': (
                f'語数: {word_count}語（目安 {range_label}）'
                ' — かなり長いようです。要点を絞れるか確認しましょう。'
            ),
        }
    if word_count > word_max:
        return {
            'level': 'warn',
            'message': (
                f'語数: {word_count}語（目安 {range_label}）'
                ' — やや長めです。'
            ),
        }
    return {
        'level': 'ok',
        'message': f'語数: {word_count}語（目安 {range_label}）',
    }


def _sentence_count_message(sentence_count: int, sentence_min: int, sentence_max: int) -> dict[str, str]:
    if sentence_count < sentence_min:
        return {
            'level': 'warn',
            'message': (
                f'文数: {sentence_count}文（目安 {sentence_min}文）'
                ' — 文が足りない可能性があります。'
            ),
        }
    if sentence_count > sentence_max:
        return {
            'level': 'warn',
            'message': (
                f'文数: {sentence_count}文（目安 {sentence_max}文程度）'
                ' — 文が多いようです。'
            ),
        }
    return {
        'level': 'ok',
        'message': f'文数: {sentence_count}文（目安 {sentence_min}文）',
    }


def analyze_writing_response(response_text: str, rubric: dict[str, Any] | None) -> dict[str, Any]:
    """
    Build Phase-1 feedback payload for a writing submission.

    Returns {"items": [{"level": "ok"|"warn"|"info", "message": str}, ...], "stats": {...}}.
    """
    text = (response_text or '').strip()
    items: list[dict[str, str]] = []

    if not text:
        return {
            'items': [{'level': 'warn', 'message': '英文が入力されていません。'}],
            'stats': {'word_count': 0, 'sentence_count': 0},
        }

    total_words = count_english_words(text)
    if total_words < 3:
        items.append({
            'level': 'warn',
            'message': '英文らしい単語がほとんど見つかりません。英語で書けているか確認しましょう。',
        })
    else:
        items.append({
            'level': 'ok',
            'message': '英文が入力されています。',
        })

    if not rubric:
        items.append({
            'level': 'info',
            'message': 'この問題の語数目安を自動判定できませんでした。問題文の指示を確認してください。',
        })
        return {
            'items': items,
            'stats': {
                'word_count': total_words,
                'sentence_count': count_sentences(text),
            },
        }

    counted_text = text_for_word_count(text, rubric)
    word_count = count_english_words(counted_text)
    word_min = int(rubric['word_min'])
    word_max = int(rubric['word_max'])

    if rubric.get('count_body_only') and rubric.get('kind') == 'email_reply':
        items.append({
            'level': 'info',
            'message': (
                f'語数は挨拶（Hi, James! など）を除いた本文で {word_count}語です'
                f'（目安 {word_min}〜{word_max}語）。'
            ),
        })
        items.append(_word_count_message(word_count, word_min, word_max))
    else:
        items.append(_word_count_message(word_count, word_min, word_max))

    sentence_min = rubric.get('sentence_min')
    sentence_max = rubric.get('sentence_max')
    if sentence_min is not None and sentence_max is not None:
        sentence_count = count_sentences(counted_text)
        items.append(_sentence_count_message(sentence_count, int(sentence_min), int(sentence_max)))
        stats = {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'kind': rubric.get('kind'),
        }
    else:
        stats = {
            'word_count': word_count,
            'sentence_count': count_sentences(counted_text),
            'kind': rubric.get('kind'),
        }

    items.append({
        'level': 'info',
        'message': '自動チェックは目安です。参考解答と見比べて自己チェックしてください。',
    })

    return {'items': items, 'stats': stats}
