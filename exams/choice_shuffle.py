"""Display-order shuffling for multiple-choice questions.

Choices are reordered per question for the user's session. Answer grading uses
choice primary keys, so shuffling does not affect scoring. Reading comprehension
and listening illustration are excluded: explanations reference fixed choice
numbers, and illustration choices (1/2/3) refer to fixed positions in the image.

Listening conversation/passage explanations also use fixed choice numbers in the
source text; after shuffle those numbers are remapped to the display order so
learners can match 「選択肢の文言」 with the on-screen 1–4 labels.
"""

from __future__ import annotations

import random
import re
from typing import Iterable, List, Optional, Sequence, TypeVar

CHOICE_SHUFFLE_QUESTION_TYPES = frozenset({
    'grammar_fill',
    'conversation_fill',
    'listening_conversation',
    'listening_passage',
})

# Canonical choice numbers in explanations (DB ``order``) → display labels.
# Matches: 1「…」, 2が正解, 2・4の家 (both sides of ・). Skips multi-digit (e.g. No.41).
_EXPLANATION_CHOICE_NUM_RE = re.compile(
    r'(?<!\d)([1-4])(?=「|が正解|・)|(?<=・)([1-4])(?!\d)'
)

ChoiceT = TypeVar('ChoiceT')


def build_order_to_display_map(display_choices: Sequence[ChoiceT]) -> dict[int, int]:
    """Map Choice.order (explanation number) → 1-based display position."""
    mapping: dict[int, int] = {}
    for display_index, choice in enumerate(display_choices, start=1):
        canonical = getattr(choice, 'order', None)
        if canonical is None:
            continue
        try:
            mapping[int(canonical)] = display_index
        except (TypeError, ValueError):
            continue
    return mapping


def remap_explanation_choice_numbers(
    explanation: Optional[str],
    display_choices: Sequence[ChoiceT],
) -> str:
    """Rewrite 1–4 choice refs in explanation to match shuffled display order."""
    text = (explanation or '').strip()
    if not text or not display_choices:
        return explanation or ''

    order_to_display = build_order_to_display_map(display_choices)
    if not order_to_display:
        return text
    if all(order_to_display.get(n) == n for n in order_to_display):
        return text

    def _replace(match: re.Match) -> str:
        canonical = int(match.group(1) or match.group(2))
        return str(order_to_display.get(canonical, canonical))

    return _EXPLANATION_CHOICE_NUM_RE.sub(_replace, text)


def should_shuffle_choices(question_type: Optional[str]) -> bool:
    return question_type in CHOICE_SHUFFLE_QUESTION_TYPES


def choice_order_session_key(level) -> str:
    return f'choice_display_order_{level}'


def _normalize_choices(choices: Iterable[ChoiceT]) -> List[ChoiceT]:
    return list(choices)


def _choice_ids(choices: Sequence[ChoiceT]) -> List[int]:
    return [choice.id for choice in choices]


def get_stored_choice_order(request, level, question_id) -> Optional[List[int]]:
    if request is None:
        return None
    store = request.session.get(choice_order_session_key(level), {})
    return store.get(str(question_id))


def _store_choice_order(request, level, question_id, choice_ids: Sequence[int]) -> None:
    key = choice_order_session_key(level)
    store = request.session.setdefault(key, {})
    store[str(question_id)] = list(choice_ids)
    request.session.modified = True


def order_choice_list_by_ids(choices: Sequence[ChoiceT], choice_ids: Sequence[int]) -> List[ChoiceT]:
    by_id = {choice.id: choice for choice in choices}
    ordered = [by_id[choice_id] for choice_id in choice_ids if choice_id in by_id]
    if len(ordered) != len(choices):
        missing = [choice for choice in choices if choice.id not in choice_ids]
        ordered.extend(missing)
    return ordered


def order_choices_for_display(
    request,
    level,
    question_type: Optional[str],
    question_id,
    choices: Iterable[ChoiceT],
    *,
    create_if_missing: bool = True,
) -> List[ChoiceT]:
    """Return choices in session-stable display order (shuffled when enabled)."""
    normalized = _normalize_choices(choices)
    if not normalized or not should_shuffle_choices(question_type):
        return normalized

    stored = get_stored_choice_order(request, level, question_id)
    current_ids = _choice_ids(normalized)
    if stored is not None and set(stored) == set(current_ids):
        return order_choice_list_by_ids(normalized, stored)

    if not create_if_missing:
        return normalized

    shuffled_ids = current_ids[:]
    random.shuffle(shuffled_ids)
    _store_choice_order(request, level, question_id, shuffled_ids)
    return order_choice_list_by_ids(normalized, shuffled_ids)


def resolve_item_question_type(item, default_question_type: Optional[str] = None) -> Optional[str]:
    question = item.get('question')
    question_type = (
        item.get('category')
        or item.get('question_type')
        or default_question_type
    )
    if question_type:
        return question_type
    if question is not None and hasattr(question, 'question_type'):
        return getattr(question, 'question_type', None)
    if question is not None and question.__class__.__name__ == 'ListeningQuestion':
        return 'listening_illustration'
    return None


def apply_choice_shuffle_to_items(
    request,
    level,
    items: Sequence[dict],
    *,
    default_question_type: Optional[str] = None,
    create_if_missing: bool = True,
) -> List[dict]:
    """Mutate question item dicts in place, shuffling their ``choices`` lists."""
    for item in items:
        if 'choices' not in item:
            continue
        raw_choices = item['choices']
        if raw_choices is None:
            continue
        if hasattr(raw_choices, 'order_by'):
            raw_choices = list(raw_choices.order_by('order', 'id'))
        else:
            raw_choices = list(raw_choices)
        question = item.get('question')
        if question is None:
            continue
        question_type = resolve_item_question_type(item, default_question_type)
        item['choices'] = order_choices_for_display(
            request,
            level,
            question_type,
            question.id,
            raw_choices,
            create_if_missing=create_if_missing,
        )
        if item.get('explanation'):
            item['explanation'] = remap_explanation_choice_numbers(
                item['explanation'],
                item['choices'],
            )
    return list(items)


def apply_choice_shuffle_to_passages(
    request,
    level,
    passages_with_questions: Sequence[dict],
    *,
    create_if_missing: bool = True,
) -> List[dict]:
    """Shuffle choices inside mock-exam style passage groupings (skips reading)."""
    for passage_item in passages_with_questions:
        questions = passage_item.get('questions') or []
        apply_choice_shuffle_to_items(
            request,
            level,
            questions,
            default_question_type='reading_comprehension',
            create_if_missing=create_if_missing,
        )
    return list(passages_with_questions)
