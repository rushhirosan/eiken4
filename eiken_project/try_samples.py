"""ログイン前お試し問題（級別サンプル）の取得。

本編 /exams/ は触らず、級ごとに文法・リスニング・（4/3級は）長文を公開する。
問題 ID は環境ごとに違うため、級・種別で先頭1件を動的に選ぶ。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db.models import Prefetch

from exams.listening_utils import filter_listening_illustrations
from exams.models import Choice, Question
from questions.models import (
    ListeningChoice,
    ListeningQuestion,
    ReadingChoice,
    ReadingPassage,
    ReadingQuestion,
)

TRY_LEVELS = ('5', '4', '3')
READING_TRY_LEVELS = frozenset({'4', '3'})

LEVEL_LABELS = {
    '5': '英検5級',
    '4': '英検4級',
    '3': '英検3級',
}


@dataclass
class TrySample:
    """お試し1問分の表示・採点用データ。"""

    key: str  # form 名: grammar / listening / reading
    kind: str  # exam_choice | listening_choice | reading_choice
    pk: int
    title: str
    question_text: str
    explanation: str
    choices: list[Any]
    audio_path: str = ''
    image_path: str = ''
    passage_text: str = ''
    correct_choice_id: int | None = None


def is_try_level(level: str) -> bool:
    return str(level) in TRY_LEVELS


def level_label(level: str) -> str:
    return LEVEL_LABELS.get(str(level), f'英検{level}級')


def _grammar_sample(level: str) -> TrySample | None:
    question = (
        Question.objects.filter(level=str(level), question_type='grammar_fill')
        .prefetch_related(
            Prefetch('choices', queryset=Choice.objects.order_by('order', 'id'))
        )
        .order_by('question_number', 'id')
        .first()
    )
    if question is None:
        return None
    choices = list(question.choices.all())
    if not choices:
        return None
    correct = next((c for c in choices if c.is_correct), None)
    return TrySample(
        key='grammar',
        kind='exam_choice',
        pk=question.pk,
        title='文法・語彙（お試し）',
        question_text=question.question_text or '',
        explanation=question.explanation or '',
        choices=choices,
        correct_choice_id=correct.pk if correct else None,
    )


def _listening_illustration_sample(level: str) -> TrySample | None:
    qs = ListeningQuestion.objects.filter(level=str(level)).order_by('id')
    if str(level) == '5':
        candidates = filter_listening_illustrations(qs, part=1)
    else:
        candidates = list(qs)
    if not candidates:
        return None
    question = candidates[0]
    choices = list(
        ListeningChoice.objects.filter(question=question).order_by('order', 'id')
    )
    if not choices:
        return None
    correct = next((c for c in choices if c.is_correct), None)
    if correct is None:
        raw = str(question.correct_answer or '').strip()
        if raw.isdigit():
            correct = next((c for c in choices if c.order == int(raw)), None)
    return TrySample(
        key='listening',
        kind='listening_choice',
        pk=question.pk,
        title='リスニング（お試し）',
        question_text=question.question_text or '音声を聞いて、正しいものを選んでください。',
        explanation=getattr(question, 'explanation', '') or '',
        choices=choices,
        audio_path=(question.audio or '').strip(),
        image_path=(question.image or '').strip(),
        correct_choice_id=correct.pk if correct else None,
    )


def _listening_conversation_sample(level: str) -> TrySample | None:
    question = (
        Question.objects.filter(level=str(level), question_type='listening_conversation')
        .prefetch_related(
            Prefetch('choices', queryset=Choice.objects.order_by('order', 'id'))
        )
        .order_by('question_number', 'id')
        .first()
    )
    if question is None:
        return None
    choices = list(question.choices.all())
    if not choices:
        return None
    correct = next((c for c in choices if c.is_correct), None)
    audio = (question.resolved_audio_file() or '').strip()
    return TrySample(
        key='listening',
        kind='exam_choice',
        pk=question.pk,
        title='リスニング（お試し）',
        question_text=(
            question.question_text
            or '音声を聞いて、正しいものを選んでください。'
        ),
        explanation=question.explanation or '',
        choices=choices,
        audio_path=audio,
        correct_choice_id=correct.pk if correct else None,
    )


def _reading_sample(level: str) -> TrySample | None:
    """4級・3級向け。最初の本文 + その先頭設問だけを公開。"""
    if str(level) not in READING_TRY_LEVELS:
        return None
    passage = (
        ReadingPassage.objects.filter(level=str(level))
        .order_by('identifier', 'id')
        .first()
    )
    if passage is None:
        return None
    question = (
        ReadingQuestion.objects.filter(passage=passage)
        .prefetch_related(
            Prefetch('choices', queryset=ReadingChoice.objects.order_by('order', 'id'))
        )
        .order_by('question_number', 'id')
        .first()
    )
    if question is None:
        return None
    choices = list(question.choices.all())
    if not choices:
        return None
    correct = next((c for c in choices if c.is_correct), None)
    return TrySample(
        key='reading',
        kind='reading_choice',
        pk=question.pk,
        title='長文読解（お試し）',
        question_text=question.question_text or '',
        explanation=question.explanation or '',
        choices=choices,
        passage_text=passage.text or '',
        correct_choice_id=correct.pk if correct else None,
    )


def get_try_samples(level: str) -> list[TrySample]:
    """級ごとのお試しセット。足りない種別は省略。"""
    level = str(level)
    samples: list[TrySample] = []
    grammar = _grammar_sample(level)
    if grammar is not None:
        samples.append(grammar)

    listening = _listening_illustration_sample(level)
    if listening is None:
        listening = _listening_conversation_sample(level)
    if listening is not None:
        samples.append(listening)

    reading = _reading_sample(level)
    if reading is not None:
        samples.append(reading)
    return samples


def try_level_availability() -> list[dict]:
    """ハブ用: 各級にサンプルがあるか。"""
    rows = []
    for level in TRY_LEVELS:
        samples = get_try_samples(level)
        rows.append({
            'level': level,
            'label': level_label(level),
            'available': bool(samples),
            'sample_count': len(samples),
            'has_listening': any(s.key == 'listening' for s in samples),
            'has_grammar': any(s.key == 'grammar' for s in samples),
            'has_reading': any(s.key == 'reading' for s in samples),
        })
    return rows
