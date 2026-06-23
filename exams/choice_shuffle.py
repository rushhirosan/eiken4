"""Display-order shuffling for multiple-choice questions.

Choices are reordered per question for the user's session. Answer grading uses
choice primary keys (or choice text for listening illustration), so shuffling
does not affect scoring. Reading comprehension is excluded because explanations
reference fixed choice numbers.
"""

from __future__ import annotations

import random
from typing import Iterable, List, Optional, Sequence, TypeVar

CHOICE_SHUFFLE_QUESTION_TYPES = frozenset({
    'grammar_fill',
    'conversation_fill',
    'listening_illustration',
    'listening_conversation',
    'listening_passage',
})

ChoiceT = TypeVar('ChoiceT')


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
