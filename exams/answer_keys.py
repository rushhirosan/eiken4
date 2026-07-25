"""Typed answer form field names to avoid PK collisions across question tables.

``exams.Question``, ``questions.ListeningQuestion``, and ``questions.ReadingQuestion``
each have independent autoincrement PKs. Bare ``answer_<id>`` keys collide when a
page mixes models (random / mock) or when submit prefers ListeningQuestion by id.
"""

from __future__ import annotations

import re
from typing import Iterable, List, Optional, Tuple

KIND_QUESTION = 'q'
KIND_LISTENING = 'lq'
KIND_READING = 'rq'

TYPED_ANSWER_KEY_RE = re.compile(r'^answer_(q|lq|rq)_(\d+)$')
LEGACY_ANSWER_KEY_RE = re.compile(r'^answer_(\d+)$')


def answer_field_name(kind: str, question_id: int) -> str:
    if kind not in (KIND_QUESTION, KIND_LISTENING, KIND_READING):
        raise ValueError(f'unknown answer kind: {kind!r}')
    return f'answer_{kind}_{int(question_id)}'


def choice_dom_id(kind: str, choice_id: int) -> str:
    """HTML id for a choice input; avoids cross-table choice PK collisions."""
    if kind not in (KIND_QUESTION, KIND_LISTENING, KIND_READING):
        raise ValueError(f'unknown answer kind: {kind!r}')
    return f'choice_{kind}_{int(choice_id)}'


def kind_for_model_instance(obj) -> str:
    name = obj.__class__.__name__
    if name == 'ListeningQuestion':
        return KIND_LISTENING
    if name == 'ReadingQuestion':
        return KIND_READING
    return KIND_QUESTION


def encode_session_ref(kind: str, question_id: int) -> str:
    return f'{kind}:{int(question_id)}'


def decode_session_ref(ref) -> Optional[Tuple[str, int]]:
    """Decode a session entry; supports legacy bare int/str ids (ambiguous)."""
    if isinstance(ref, dict):
        kind = ref.get('kind')
        qid = ref.get('id')
        if kind in (KIND_QUESTION, KIND_LISTENING, KIND_READING) and qid is not None:
            return kind, int(qid)
        return None
    if isinstance(ref, int):
        return None  # legacy bare id — ambiguous, caller must not guess
    if isinstance(ref, str):
        if ':' in ref:
            kind, _, rest = ref.partition(':')
            if kind in (KIND_QUESTION, KIND_LISTENING, KIND_READING) and rest.isdigit():
                return kind, int(rest)
        if ref.isdigit():
            return None
    return None


def iter_submitted_answers(
    post,
    *,
    default_kind: Optional[str] = None,
) -> List[Tuple[str, int, str]]:
    """Return ``(kind, question_id, value)`` for each non-empty answer_* field.

    Typed keys (``answer_q_12``) always win. Legacy ``answer_12`` is accepted only
    when ``default_kind`` is set (single-model forms).
    """
    results: List[Tuple[str, int, str]] = []
    for key in post.keys():
        if not key.startswith('answer_'):
            continue
        value = post.get(key)
        if value is None or not str(value).strip():
            continue
        typed = TYPED_ANSWER_KEY_RE.match(key)
        if typed:
            results.append((typed.group(1), int(typed.group(2)), str(value)))
            continue
        if default_kind:
            legacy = LEGACY_ANSWER_KEY_RE.match(key)
            if legacy:
                results.append((default_kind, int(legacy.group(1)), str(value)))
    return results


def ids_for_kind(submissions: Iterable[Tuple[str, int, str]], kind: str) -> List[int]:
    return [qid for k, qid, _ in submissions if k == kind]
