"""Progress-safe explanation sync from data/questions txt into existing DB rows.

Never deletes Question / ListeningQuestion / ReadingQuestion rows.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Callable

from exams.models import Question
from questions.level_paths import questions_file_abspath
from questions.models import ListeningQuestion, ReadingPassage, ReadingQuestion

# writing の参考解答は explanation カラムに入る
_LINE_FULLWIDTH_BRACKETS = re.compile(r'^【[^】]*】\s*$')
_LINE_KYOKAI_DISCLAIMER = re.compile(
    r'^※協会発表の解答例（一次試験）より[。.]?\s*$',
)

PASSAGE_IDENTIFIER_MAP = {
    1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h',
    9: 'i', 10: 'j', 11: 'k', 12: 'l', 13: 'm', 14: 'n', 15: 'o',
}


@dataclass(frozen=True)
class CategorySpec:
    key: str
    label: str
    filename: str | None = None  # None for listening aggregate


CATEGORIES: dict[str, CategorySpec] = {
    'grammar_fill': CategorySpec('grammar_fill', '文法・語彙', 'grammar_fill_questions.txt'),
    'conversation_fill': CategorySpec(
        'conversation_fill', '会話補充', 'conversation_questions.txt'
    ),
    'word_order': CategorySpec('word_order', '語順整序', 'wordorder_questions.txt'),
    'reading_comprehension': CategorySpec(
        'reading_comprehension', '読解', 'reading_comprehesion_questions.txt'
    ),
    'writing': CategorySpec('writing', 'ライティング', 'writing_questions.txt'),
    'listening_illustration': CategorySpec(
        'listening_illustration', 'リスニング第1部（イラスト）',
        'listening_illustration_questions.txt',
    ),
    'listening_conversation': CategorySpec(
        'listening_conversation', 'リスニング第2部（会話）',
        'listening_conversation_questions.txt',
    ),
    'listening_passage': CategorySpec(
        'listening_passage', 'リスニング第3部（文）',
        'listening_passage_questions.txt',
    ),
    'listening': CategorySpec('listening', 'リスニング（全パート）'),
    'all': CategorySpec('all', '全カテゴリ'),
}

ATOMIC_CATEGORIES = [
    'grammar_fill',
    'conversation_fill',
    'word_order',
    'reading_comprehension',
    'writing',
    'listening_illustration',
    'listening_conversation',
    'listening_passage',
]


def expand_categories(category: str) -> list[str]:
    if category == 'all':
        return list(ATOMIC_CATEGORIES)
    if category == 'listening':
        return [
            'listening_illustration',
            'listening_conversation',
            'listening_passage',
        ]
    if category not in CATEGORIES:
        raise ValueError(f'unknown category: {category}')
    return [category]


def split_no_blocks(content: str) -> list[str]:
    """Split listening-style files that start each question with No.N:"""
    blocks: list[str] = []
    current: list[str] = []
    for line in content.split('\n'):
        if line.strip().startswith('No.'):
            if current:
                blocks.append('\n'.join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append('\n'.join(current))
    return blocks


def extract_no_explanation(block: str) -> tuple[int | None, str]:
    number_match = re.search(r'No\.(\d+):', block)
    if not number_match:
        return None, ''
    number = int(number_match.group(1))
    explanation_match = re.search(
        r'【解説\d+】\s*(.*?)(?=\n---|$)', block, re.DOTALL
    )
    explanation = explanation_match.group(1).strip() if explanation_match else ''
    return number, explanation


def extract_mondai_explanation(block: str) -> tuple[int | None, str]:
    number_match = re.search(r'問題(\d+)', block)
    if not number_match:
        return None, ''
    number = int(number_match.group(1))
    explanation_match = re.search(
        r'【解説\d+】\s*(.*?)(?=\n---|$)', block, re.DOTALL
    )
    explanation = explanation_match.group(1).strip() if explanation_match else ''
    return number, explanation


def _strip_writing_noise_lines(text: str) -> str:
    out: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if _LINE_FULLWIDTH_BRACKETS.match(s) or _LINE_KYOKAI_DISCLAIMER.match(s):
            continue
        out.append(line)
    return '\n'.join(out).strip()


def _strip_block_leader_metadata(block: str) -> str:
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if _LINE_FULLWIDTH_BRACKETS.match(s) or _LINE_KYOKAI_DISCLAIMER.match(s):
            i += 1
            continue
        break
    return '\n'.join(lines[i:]).strip()


def _read_file(level: str, filename: str) -> str:
    path = questions_file_abspath(level, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, encoding='utf-8') as f:
        return f.read()


def _update_exam_by_question_number(
    *,
    level: str,
    question_type: str,
    filename: str,
    extract: Callable[[str], tuple[int | None, str]],
    dry_run: bool,
    log: Callable[[str], None],
    warn: Callable[[str], None],
    number_min: int = 1,
    number_max: int = 999,
) -> int:
    content = _read_file(level, filename)
    updated = 0
    for block in content.split('---'):
        if not block.strip():
            continue
        number, explanation = extract(block)
        if number is None or not explanation:
            continue
        if number < number_min or number > number_max:
            continue
        qs = Question.objects.filter(
            level=level,
            question_type=question_type,
            question_number=number,
        )
        count = qs.count()
        if count == 0:
            warn(f'{question_type} 問題{number}: DBに該当なし')
            continue
        if not dry_run:
            qs.update(explanation=explanation)
        updated += count
        log(f'{question_type} 問題{number}: {count} row(s)')
    return updated


def update_grammar_fill(level: str, dry_run: bool, log, warn) -> int:
    return _update_exam_by_question_number(
        level=level,
        question_type='grammar_fill',
        filename='grammar_fill_questions.txt',
        extract=extract_mondai_explanation,
        dry_run=dry_run,
        log=log,
        warn=warn,
        number_max=165,
    )


def update_conversation_fill(level: str, dry_run: bool, log, warn) -> int:
    return _update_exam_by_question_number(
        level=level,
        question_type='conversation_fill',
        filename='conversation_questions.txt',
        extract=extract_mondai_explanation,
        dry_run=dry_run,
        log=log,
        warn=warn,
        number_max=55,
    )


def update_word_order(level: str, dry_run: bool, log, warn) -> int:
    return _update_exam_by_question_number(
        level=level,
        question_type='word_order',
        filename='wordorder_questions.txt',
        extract=extract_mondai_explanation,
        dry_run=dry_run,
        log=log,
        warn=warn,
    )


def update_writing(level: str, dry_run: bool, log, warn) -> int:
    """Update writing reference answers stored in Question.explanation."""
    try:
        content = _read_file(level, 'writing_questions.txt')
    except FileNotFoundError:
        warn(f'writing: ファイルなし（level={level}）')
        return 0

    updated = 0
    for block in content.split('---'):
        block = _strip_block_leader_metadata(block.strip())
        if not block:
            continue
        m_num = re.search(r'問題(\d+):', block)
        if not m_num:
            continue
        number = int(m_num.group(1))
        if number < 1 or number > 99:
            continue
        ref_match = re.search(
            r'【参考解答】\s*(.*?)(?=\n※協会|\Z)',
            block,
            re.DOTALL,
        )
        explanation = _strip_writing_noise_lines(
            ref_match.group(1).strip() if ref_match else ''
        )
        if not explanation:
            warn(f'writing 問題{number}: 参考解答なし')
            continue
        qs = Question.objects.filter(
            level=level,
            question_type='writing',
            question_number=number,
        )
        count = qs.count()
        if count == 0:
            warn(f'writing 問題{number}: DBに該当なし')
            continue
        if not dry_run:
            qs.update(explanation=explanation)
        updated += count
        log(f'writing 問題{number}: {count} row(s)')
    return updated


def update_reading_comprehension(level: str, dry_run: bool, log, warn) -> int:
    content = _read_file(level, 'reading_comprehesion_questions.txt')
    updated = 0
    for passage_block in content.split('---'):
        if not passage_block.strip():
            continue
        passage_number_match = re.search(r'本文(\d+)', passage_block)
        if not passage_number_match:
            continue
        passage_number = int(passage_number_match.group(1))
        if passage_number < 1 or passage_number > 15:
            continue
        identifier = PASSAGE_IDENTIFIER_MAP.get(passage_number)
        if not identifier:
            continue
        passage = ReadingPassage.objects.filter(
            level=level, identifier=identifier
        ).first()
        if not passage:
            warn(f'reading 本文{passage_number}: DBに該当なし')
            continue

        matches = list(
            re.finditer(
                r'【解説\d+[a-z]】\s*(.*?)(?=\n問題\d+[a-z]:|\n---|$)',
                passage_block,
                re.DOTALL,
            )
        )
        for i, m in enumerate(matches, 1):
            explanation = m.group(1).strip()
            if not explanation:
                continue
            qs = ReadingQuestion.objects.filter(
                passage=passage, question_number=i
            )
            count = qs.count()
            if count == 0:
                warn(
                    f'reading 本文{passage_number} 問{i}: DBに該当なし'
                )
                continue
            if not dry_run:
                qs.update(explanation=explanation)
            updated += count
            log(f'reading 本文{passage_number} 問{i}: {count} row(s)')
    return updated


def update_listening_illustration(level: str, dry_run: bool, log, warn) -> int:
    content = _read_file(level, 'listening_illustration_questions.txt')
    updated = 0
    for block in split_no_blocks(content):
        number, explanation = extract_no_explanation(block)
        if number is None or not explanation:
            continue
        qs = ListeningQuestion.objects.filter(
            level=level,
            image__endswith=f'listening_illustration_image{number}.png',
        )
        count = qs.count()
        if count == 0:
            warn(f'listening_illustration No.{number}: DBに該当なし')
            continue
        if not dry_run:
            qs.update(explanation=explanation)
        updated += count
        log(f'listening_illustration No.{number}: {count} row(s)')
    return updated


def update_listening_conversation(level: str, dry_run: bool, log, warn) -> int:
    content = _read_file(level, 'listening_conversation_questions.txt')
    updated = 0
    for block in split_no_blocks(content):
        number, explanation = extract_no_explanation(block)
        if number is None or not explanation:
            continue
        qs = Question.objects.filter(
            level=level,
            question_type='listening_conversation',
            question_number=number,
        )
        count = qs.count()
        if count == 0:
            warn(f'listening_conversation No.{number}: DBに該当なし')
            continue
        if not dry_run:
            qs.update(explanation=explanation)
        updated += count
        log(f'listening_conversation No.{number}: {count} row(s)')
    return updated


def update_listening_passage(level: str, dry_run: bool, log, warn) -> int:
    try:
        content = _read_file(level, 'listening_passage_questions.txt')
    except FileNotFoundError:
        warn(f'listening_passage: ファイルなし（level={level}）')
        return 0
    updated = 0
    for block in split_no_blocks(content):
        number, explanation = extract_no_explanation(block)
        if number is None or not explanation:
            continue
        qs = Question.objects.filter(
            level=level,
            question_type='listening_passage',
            question_number=number,
        )
        count = qs.count()
        if count == 0:
            warn(f'listening_passage No.{number}: DBに該当なし')
            continue
        if not dry_run:
            qs.update(explanation=explanation)
        updated += count
        log(f'listening_passage No.{number}: {count} row(s)')
    return updated


UPDATERS: dict[str, Callable] = {
    'grammar_fill': update_grammar_fill,
    'conversation_fill': update_conversation_fill,
    'word_order': update_word_order,
    'reading_comprehension': update_reading_comprehension,
    'writing': update_writing,
    'listening_illustration': update_listening_illustration,
    'listening_conversation': update_listening_conversation,
    'listening_passage': update_listening_passage,
}


def sync_explanations(
    *,
    level: str,
    category: str,
    dry_run: bool,
    log: Callable[[str], None],
    warn: Callable[[str], None],
) -> dict[str, int]:
    results: dict[str, int] = {}
    for key in expand_categories(category):
        updater = UPDATERS[key]
        try:
            results[key] = updater(level, dry_run, log, warn)
        except FileNotFoundError as exc:
            warn(f'{key}: ファイルなし ({exc})')
            results[key] = 0
    return results
