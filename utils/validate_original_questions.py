#!/usr/bin/env python3
"""data/questions/original/ の問題テキストを機械検証する（Phase 2）。

例:
  python utils/validate_original_questions.py
  python utils/validate_original_questions.py --level 4 --category grammar_fill
  python utils/validate_original_questions.py --fail-on-warn
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eiken_project.settings')

import django

django.setup()

from exams.models import Question
from questions.level_paths import (
    db_audio_path,
    db_image_path_part1,
    listening_illustration_audio_part,
)
from questions.study_points import extract_study_points

ORIGINAL_ROOT = _REPO / 'data' / 'questions' / 'original'
STATIC_ROOT = _REPO / 'static'

CATEGORY_FILES: dict[str, str] = {
    'grammar_fill': 'grammar_fill_questions.txt',
    'conversation_fill': 'conversation_questions.txt',
    'wordorder': 'wordorder_questions.txt',
    'reading_comprehension': 'reading_comprehesion_questions.txt',
    'listening_illustration': 'listening_illustration_questions.txt',
    'listening_conversation': 'listening_conversation_questions.txt',
    'listening_passage': 'listening_passage_questions.txt',
    'speaking': 'speaking_questions.txt',
    'writing': 'writing_questions.txt',
}

LEVEL_CATEGORIES: dict[str, tuple[str, ...]] = {
    '5': (
        'grammar_fill',
        'conversation_fill',
        'wordorder',
        'listening_illustration',
        'listening_conversation',
        'speaking',
    ),
    '4': (
        'grammar_fill',
        'conversation_fill',
        'wordorder',
        'reading_comprehension',
        'listening_illustration',
        'listening_conversation',
        'listening_passage',
        'speaking',
    ),
    '3': (
        'grammar_fill',
        'conversation_fill',
        'wordorder',
        'reading_comprehension',
        'listening_illustration',
        'listening_conversation',
        'listening_passage',
        'speaking',
        'writing',
    ),
}

VALID_STUDY_CATEGORIES = set(Question.STUDY_POINT_BADGE_CLASSES.keys())
BIAS_WARN_RATIO = 0.45
BIAS_MIN_QUESTIONS = 10

_RE_QUESTION = re.compile(r'^問題(\d+[a-z]?):', re.MULTILINE)
_RE_CHOICES = re.compile(r'^選択肢(\d+[a-z]?):', re.MULTILINE)
_RE_CORRECT = re.compile(r'【正解(\d+[a-z]?)】\s*\n(\d+)\.\s*(.+)', re.MULTILINE)
_RE_EXPLANATION = re.compile(r'【解説(\d+[a-z]?)】', re.MULTILINE)
_RE_POINT = re.compile(r'【ポイント(\d+[a-z]?)】', re.MULTILINE)
_RE_LISTENING_NO = re.compile(r'^No\.(\d+):', re.MULTILINE)
_RE_CHOICE_LINE = re.compile(r'^(\d+)\.\s*(.+)$')


@dataclass
class Issue:
    level: str
    category: str
    ref: str
    message: str
    severity: str = 'error'  # error | warn


def _static_path(db_relative: str) -> Path:
    """audio/level4/... → static/audio/level4/..."""
    return STATIC_ROOT / db_relative


def _parse_blocks(text: str) -> list[str]:
    return [b.strip() for b in text.split('---') if b.strip()]


def _choice_lines(block: str, choices_label: str) -> list[tuple[int, str]]:
    m = re.search(rf'選択肢{re.escape(choices_label)}:\s*(.*?)(?=\n【正解|\Z)', block, re.DOTALL)
    if not m:
        return []
    out: list[tuple[int, str]] = []
    for line in m.group(1).split('\n'):
        line = line.strip()
        mo = _RE_CHOICE_LINE.match(line)
        if mo:
            out.append((int(mo.group(1)), mo.group(2).strip()))
    return out


def _check_study_point(block: str, suffix: str, issues: list[Issue], level: str, category: str, ref: str) -> None:
    if f'【ポイント{suffix}】' not in block:
        return
    parsed = extract_study_points(block, suffix=re.escape(suffix))
    if not parsed:
        issues.append(Issue(level, category, ref, f'【ポイント{suffix}】をパースできません'))
        return
    if not parsed.get('category'):
        issues.append(Issue(level, category, ref, f'【ポイント{suffix}】に種別: がありません'))
    elif parsed['category'] not in VALID_STUDY_CATEGORIES:
        issues.append(
            Issue(
                level,
                category,
                ref,
                f'【ポイント{suffix}】の種別が不正: {parsed["category"]!r} '
                f'(許可: {sorted(VALID_STUDY_CATEGORIES)})',
            )
        )
    if not parsed.get('title'):
        issues.append(Issue(level, category, ref, f'【ポイント{suffix}】に見出し: がありません'))
    if not parsed.get('keys'):
        issues.append(Issue(level, category, ref, f'【ポイント{suffix}】に・行がありません'))


def _validate_choice_question_block(
    block: str,
    *,
    level: str,
    category: str,
    ref: str,
    issues: list[Issue],
    expected_choices: int = 4,
    answer_positions: list[int] | None = None,
) -> None:
    qm = _RE_QUESTION.search(block)
    if not qm:
        issues.append(Issue(level, category, ref, '問題N: がありません'))
        return
    suffix = qm.group(1)

    if not _RE_EXPLANATION.search(block):
        issues.append(Issue(level, category, ref, f'【解説{suffix}】がありません'))

    cm = _RE_CORRECT.search(block)
    if not cm:
        issues.append(Issue(level, category, ref, f'【正解{suffix}】がありません'))
        return
    if cm.group(1) != suffix:
        issues.append(Issue(level, category, ref, '問題番号と【正解】の番号が一致しません'))

    ans_num = int(cm.group(2))
    ans_text = cm.group(3).strip().split('\n')[0].strip()
    choices = _choice_lines(block, suffix)
    if len(choices) != expected_choices:
        issues.append(
            Issue(level, category, ref, f'選択肢が {len(choices)} 個（期待 {expected_choices}）')
        )
    choice_map = dict(choices)
    if ans_num not in choice_map:
        issues.append(Issue(level, category, ref, f'正解番号 {ans_num} が選択肢にありません'))
    elif choice_map[ans_num] != ans_text:
        issues.append(
            Issue(
                level,
                category,
                ref,
                f'正解テキスト不一致: 【正解】={ans_text!r} 選択肢{ans_num}={choice_map.get(ans_num)!r}',
            )
        )
    if answer_positions is not None:
        answer_positions.append(ans_num)

    _check_study_point(block, suffix, issues, level, category, ref)


def _validate_listening_block(
    block: str,
    *,
    level: str,
    category: str,
    issues: list[Issue],
    answer_positions: list[int] | None = None,
    expected_choices: int = 3,
) -> None:
    nm = _RE_LISTENING_NO.search(block)
    if not nm:
        issues.append(Issue(level, category, 'block', 'No.N: がありません'))
        return
    num = int(nm.group(1))
    ref = f'No.{num}'

    if not re.search(r'【解説\d*】', block):
        issues.append(Issue(level, category, ref, '【解説】がありません'))

    cm = re.search(r'【正解\d*】\s*\n(\d+)\.', block)
    if not cm:
        issues.append(Issue(level, category, ref, '【正解】がありません'))
        return
    ans_num = int(cm.group(1))
    if answer_positions is not None:
        answer_positions.append(ans_num)

    choices: list[tuple[int, str]] = []
    in_question = False
    for line in block.split('\n'):
        stripped = line.strip()
        if stripped.startswith('Question No.'):
            in_question = True
            continue
        if in_question and stripped.startswith('【'):
            break
        if in_question:
            mo = _RE_CHOICE_LINE.match(stripped)
            if mo:
                choices.append((int(mo.group(1)), mo.group(2).strip()))

    if len(choices) != expected_choices:
        issues.append(
            Issue(level, category, ref, f'選択肢が {len(choices)} 個（期待 {expected_choices}）')
        )
    if ans_num < 1 or ans_num > len(choices):
        issues.append(Issue(level, category, ref, f'正解番号 {ans_num} が範囲外'))

    if category == 'listening_illustration':
        image_rel = db_image_path_part1(level, f'listening_illustration_image{num}.png')
        audio_part = listening_illustration_audio_part(level, num)
        audio_rel = db_audio_path(level, audio_part, f'listening_illustration_question{num}.mp3')
        for label, rel in (('画像', image_rel), ('音声', audio_rel)):
            if not _static_path(rel).exists():
                issues.append(Issue(level, category, ref, f'{label}ファイルが存在しません: static/{rel}'))
    elif category == 'listening_conversation':
        audio_rel = db_audio_path(level, 'part2', f'listening_conversation_question{num}.mp3')
        if not _static_path(audio_rel).exists():
            issues.append(Issue(level, category, ref, f'音声ファイルが存在しません: static/{audio_rel}'))
    elif category == 'listening_passage':
        audio_rel = db_audio_path(level, 'part3', f'listening_passage_question{num}.mp3')
        if not _static_path(audio_rel).exists():
            issues.append(Issue(level, category, ref, f'音声ファイルが存在しません: static/{audio_rel}'))


def _validate_reading_file(text: str, *, level: str, issues: list[Issue], answer_positions: list[int]) -> None:
    category = 'reading_comprehension'
    passages = _parse_blocks(text)
    if not passages:
        issues.append(Issue(level, category, 'file', '本文ブロックがありません'))
        return

    for passage in passages:
        if not re.search(r'^本文\d+', passage, re.MULTILINE):
            issues.append(Issue(level, category, 'passage', '本文N: がありません'))
            continue
        body_m = re.search(r'^本文(\d+)', passage, re.MULTILINE)
        body_num = body_m.group(1) if body_m else '?'

        sub_blocks = re.split(r'(?=^問題\d+[a-z]?:)', passage, flags=re.MULTILINE)
        sub_blocks = [b.strip() for b in sub_blocks if b.strip() and _RE_QUESTION.search(b)]
        if not sub_blocks:
            issues.append(Issue(level, category, f'本文{body_num}', '問題がありません'))
            continue

        for sub in sub_blocks:
            qm = _RE_QUESTION.search(sub)
            suffix = qm.group(1) if qm else '?'
            ref = f'本文{body_num} 問題{suffix}'
            _validate_choice_question_block(
                sub,
                level=level,
                category=category,
                ref=ref,
                issues=issues,
                answer_positions=answer_positions,
            )


def _validate_speaking_file(text: str, *, level: str, issues: list[Issue]) -> None:
    category = 'speaking'
    for block in _parse_blocks(text):
        qm = _RE_QUESTION.search(block)
        ref = f'問題{qm.group(1)}' if qm else 'block'
        for marker in ('【Title】', '【Passage】', '【Questions】', '【参考解答】'):
            if marker not in block:
                issues.append(Issue(level, category, ref, f'{marker} がありません'))


def _validate_writing_file(text: str, *, level: str, issues: list[Issue]) -> None:
    category = 'writing'
    for block in _parse_blocks(text):
        qm = _RE_QUESTION.search(block)
        ref = f'問題{qm.group(1)}' if qm else 'block'
        if '【参考解答】' not in block:
            issues.append(Issue(level, category, ref, '【参考解答】 がありません'))
            continue
        suffix = qm.group(1) if qm else ''
        if suffix:
            _check_study_point(block, suffix, issues, level, category, ref)


def _check_answer_bias(
    level: str,
    category: str,
    positions: list[int],
    issues: list[Issue],
) -> None:
    if len(positions) < BIAS_MIN_QUESTIONS:
        return
    counts = Counter(positions)
    total = len(positions)
    for pos, count in counts.items():
        ratio = count / total
        if ratio >= BIAS_WARN_RATIO:
            issues.append(
                Issue(
                    level,
                    category,
                    'distribution',
                    f'正解 {pos} が {count}/{total} ({ratio:.0%}) — 偏りが大きい',
                    severity='warn',
                )
            )


def validate_file(level: str, category: str, path: Path) -> list[Issue]:
    issues: list[Issue] = []
    cat = category
    if not path.exists():
        issues.append(Issue(level, cat, 'file', f'ファイルがありません: {path}'))
        return issues

    text = path.read_text(encoding='utf-8')
    if not text.strip():
        issues.append(Issue(level, cat, 'file', 'ファイルが空です'))
        return issues

    answer_positions: list[int] = []

    if category in ('grammar_fill', 'conversation_fill'):
        blocks = _parse_blocks(text)
        if not blocks:
            issues.append(Issue(level, cat, 'file', '問題ブロックがありません'))
        for block in blocks:
            qm = _RE_QUESTION.search(block)
            ref = f'問題{qm.group(1)}' if qm else 'block'
            _validate_choice_question_block(
                block,
                level=level,
                category=cat,
                ref=ref,
                issues=issues,
                answer_positions=answer_positions,
            )

    elif category == 'wordorder':
        # 枠・チップ検算は validate_wordorder_questions.py に委譲
        blocks = _parse_blocks(text)
        for block in blocks:
            qm = re.search(r'問題(\d+):', block)
            ref = f'問題{qm.group(1)}' if qm else 'block'
            if not re.search(r'【正解\d+】', block):
                issues.append(Issue(level, cat, ref, '【正解】がありません'))
            if not re.search(r'【解説\d+】', block):
                issues.append(Issue(level, cat, ref, '【解説】がありません'))
            cm = re.search(r'【正解\d+】\s*\n(\d+)\.', block)
            if cm and answer_positions is not None:
                answer_positions.append(int(cm.group(1)))

    elif category == 'reading_comprehension':
        _validate_reading_file(text, level=level, issues=issues, answer_positions=answer_positions)

    elif category in (
        'listening_illustration',
        'listening_conversation',
        'listening_passage',
    ):
        # listening_illustration は No. でブロック分割（--- なしのこともある）
        blocks: list[str] = []
        current: list[str] = []
        for line in text.split('\n'):
            if line.strip().startswith('No.') and current:
                blocks.append('\n'.join(current).strip())
                current = [line]
            else:
                current.append(line)
        if current:
            blocks.append('\n'.join(current).strip())
        blocks = [b for b in blocks if b.strip()]
        expected = 3 if category == 'listening_illustration' else 4
        for block in blocks:
            _validate_listening_block(
                block,
                level=level,
                category=cat,
                issues=issues,
                answer_positions=answer_positions,
                expected_choices=expected,
            )

    elif category == 'speaking':
        _validate_speaking_file(text, level=level, issues=issues)

    elif category == 'writing':
        _validate_writing_file(text, level=level, issues=issues)

    else:
        issues.append(Issue(level, cat, 'file', f'未対応カテゴリ: {category}'))

    if answer_positions:
        _check_answer_bias(level, cat, answer_positions, issues)

    return issues


def iter_targets(
    levels: list[str] | None,
    categories: list[str] | None,
) -> list[tuple[str, str, Path]]:
    out: list[tuple[str, str, Path]] = []
    for level in levels or sorted(LEVEL_CATEGORIES.keys()):
        for category in categories or LEVEL_CATEGORIES[level]:
            if category not in CATEGORY_FILES:
                continue
            path = ORIGINAL_ROOT / f'level{level}' / CATEGORY_FILES[category]
            out.append((level, category, path))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--level', action='append', choices=['5', '4', '3'])
    parser.add_argument(
        '--category',
        action='append',
        dest='categories',
        choices=list(CATEGORY_FILES.keys()),
    )
    parser.add_argument(
        '--fail-on-warn',
        action='store_true',
        help='警告も exit 1 にする',
    )
    args = parser.parse_args(argv)

    all_issues: list[Issue] = []
    for level, category, path in iter_targets(args.level, args.categories):
        file_issues = validate_file(level, category, path)
        all_issues.extend(file_issues)
        rel = path.relative_to(_REPO) if path.is_relative_to(_REPO) else path
        errors = [i for i in file_issues if i.severity == 'error']
        warns = [i for i in file_issues if i.severity == 'warn']
        if not file_issues:
            print(f'OK: {rel}')
        elif not errors:
            print(f'OK (warn {len(warns)}): {rel}')
        else:
            print(f'FAIL ({len(errors)} error, {len(warns)} warn): {rel}', file=sys.stderr)

    errors = [i for i in all_issues if i.severity == 'error']
    warns = [i for i in all_issues if i.severity == 'warn']

    for issue in all_issues:
        prefix = 'WARN' if issue.severity == 'warn' else 'ERROR'
        dest = sys.stderr if issue.severity == 'error' else sys.stdout
        print(
            f'  {prefix} level{issue.level}/{issue.category} [{issue.ref}]: {issue.message}',
            file=dest,
        )

    if errors:
        print(f'\nFAIL: {len(errors)} error(s), {len(warns)} warning(s)', file=sys.stderr)
        return 1
    if warns and args.fail_on_warn:
        print(f'\nFAIL: {len(warns)} warning(s) (--fail-on-warn)', file=sys.stderr)
        return 1

    print(f'\nOK: original 検証完了（{len(warns)} warning(s)）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
