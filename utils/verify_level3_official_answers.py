#!/usr/bin/env python3
"""
3級の正解を英検協会公式解答PDF（F日程）と照合する。

公式PDF: https://www.eiken.or.jp/eiken/result/pdf/{YYYYMM}F3kyu.pdf
例: 202501F3kyu.pdf, 202502F3kyu.pdf, 202503F3kyu.pdf

※ D日程（金曜）の PDF は使わない。grade_3 ページの過去問は F 日程解答と対応する。
"""
from __future__ import annotations

import re
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import fitz

_REPO = Path(__file__).resolve().parents[1]
_LEVEL3 = _REPO / 'data' / 'questions' / 'level3'

ROUND_CODES = ('202501', '202502', '202503')
OFFICIAL_PDF_URL = 'https://www.eiken.or.jp/eiken/result/pdf/{code}F3kyu.pdf'


@dataclass
class Mismatch:
    section: str
    app_label: str
    round_code: str
    exam_no: int
    repo_choice: int
    official_choice: int


def fetch_official_answers(code: str) -> tuple[dict[int, int], dict[int, int]]:
    url = OFFICIAL_PDF_URL.format(code=code)
    data = urllib.request.urlopen(url, timeout=60).read()
    doc = fitz.open(stream=data, filetype='pdf')
    text = ''.join(page.get_text() for page in doc)

    rw: dict[int, int] = {}
    for mo in re.finditer(r'\((\d+)\)\s+(\d)', text):
        n, a = int(mo.group(1)), int(mo.group(2))
        if 1 <= n <= 30:
            rw[n] = a

    listening: dict[int, int] = {}
    m = re.search(r'3級リスニング\s*(.*)', text, re.DOTALL)
    if m:
        section = m.group(1)[:3000]
        for mo in re.finditer(r'No\.\s*(\d+)\s+(\d)', section):
            listening[int(mo.group(1))] = int(mo.group(2))
    return rw, listening


def parse_choice_number(correct_block: str) -> int | None:
    mo = re.search(r'【正解[^\]]*】\s*(\d+)\.', correct_block)
    return int(mo.group(1)) if mo else None


def split_blocks(content: str, header_pattern: str) -> list[tuple[str, str]]:
    parts = re.split(rf'(?={header_pattern})', content)
    blocks: list[tuple[str, str]] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        mo = re.match(header_pattern, part)
        if not mo:
            continue
        label = mo.group(1)
        blocks.append((label, part))
    return blocks


def verify_grammar(round_idx: int, official_rw: dict[int, int]) -> list[Mismatch]:
    text = (_LEVEL3 / 'grammar_fill_questions.txt').read_text(encoding='utf-8')
    mismatches: list[Mismatch] = []
    q_start = round_idx * 15 + 1
    q_end = q_start + 14
    for mo in re.finditer(
        r'問題(\d+):.*?【正解\1】\s*(\d+)\.', text, re.DOTALL
    ):
        qnum = int(mo.group(1))
        if not (q_start <= qnum <= q_end):
            continue
        repo = int(mo.group(2))
        exam_no = qnum - q_start + 1
        official = official_rw.get(exam_no)
        if official is None:
            continue
        if repo != official:
            mismatches.append(
                Mismatch(
                    'grammar_fill',
                    f'問題{qnum}',
                    ROUND_CODES[round_idx],
                    exam_no,
                    repo,
                    official,
                )
            )
    return mismatches


def verify_conversation(round_idx: int, official_rw: dict[int, int]) -> list[Mismatch]:
    text = (_LEVEL3 / 'conversation_questions.txt').read_text(encoding='utf-8')
    mismatches: list[Mismatch] = []
    q_start = round_idx * 5 + 1
    q_end = q_start + 4
    for mo in re.finditer(
        r'問題(\d+):.*?【正解\1】\s*(\d+)\.', text, re.DOTALL
    ):
        qnum = int(mo.group(1))
        if not (q_start <= qnum <= q_end):
            continue
        repo = int(mo.group(2))
        exam_no = 15 + (qnum - q_start + 1)
        official = official_rw.get(exam_no)
        if official is None:
            continue
        if repo != official:
            mismatches.append(
                Mismatch(
                    'conversation_fill',
                    f'問題{qnum}',
                    ROUND_CODES[round_idx],
                    exam_no,
                    repo,
                    official,
                )
            )
    return mismatches


def verify_reading(round_idx: int, official_rw: dict[int, int]) -> list[Mismatch]:
    text = (_LEVEL3 / 'reading_comprehesion_questions.txt').read_text(encoding='utf-8')
    mismatches: list[Mismatch] = []
    labels = re.findall(r'問題(\d+[a-e]):', text)
    # 各回10問: 大問1〜3（a〜e 含む）が 21〜30
    round_labels = labels[round_idx * 10 : (round_idx + 1) * 10]
    for i, label in enumerate(round_labels):
        exam_no = 21 + i
        block_mo = re.search(
            rf'問題{re.escape(label)}:.*?【正解{re.escape(label)}】\s*(\d+)\.',
            text,
            re.DOTALL,
        )
        if not block_mo:
            continue
        repo = int(block_mo.group(1))
        official = official_rw.get(exam_no)
        if official is None:
            continue
        if repo != official:
            mismatches.append(
                Mismatch(
                    'reading_comprehension',
                    f'問題{label}',
                    ROUND_CODES[round_idx],
                    exam_no,
                    repo,
                    official,
                )
            )
    return mismatches


def verify_listening_part(
    filename: str,
    section: str,
    round_idx: int,
    exam_no_start: int,
    official_listen: dict[int, int],
) -> list[Mismatch]:
    text = (_LEVEL3 / filename).read_text(encoding='utf-8')
    mismatches: list[Mismatch] = []
    q_start = round_idx * 10 + 1
    q_end = q_start + 9
    for mo in re.finditer(
        r'Question No\.(\d+):.*?【正解\1】\s*(\d+)\.', text, re.DOTALL
    ):
        qnum = int(mo.group(1))
        if not (q_start <= qnum <= q_end):
            continue
        repo = int(mo.group(2))
        exam_no = exam_no_start + (qnum - q_start)
        official = official_listen.get(exam_no)
        if official is None:
            continue
        if repo != official:
            mismatches.append(
                Mismatch(
                    section,
                    f'Question No.{qnum}',
                    ROUND_CODES[round_idx],
                    exam_no,
                    repo,
                    official,
                )
            )
    return mismatches


def main() -> int:
    all_mismatches: list[Mismatch] = []
    for round_idx, code in enumerate(ROUND_CODES):
        rw, listen = fetch_official_answers(code)
        all_mismatches.extend(verify_grammar(round_idx, rw))
        all_mismatches.extend(verify_conversation(round_idx, rw))
        all_mismatches.extend(verify_reading(round_idx, rw))
        all_mismatches.extend(
            verify_listening_part(
                'listening_illustration_questions.txt',
                'listening_illustration',
                round_idx,
                1,
                listen,
            )
        )
        all_mismatches.extend(
            verify_listening_part(
                'listening_conversation_questions.txt',
                'listening_conversation',
                round_idx,
                11,
                listen,
            )
        )
        all_mismatches.extend(
            verify_listening_part(
                'listening_passage_questions.txt',
                'listening_passage',
                round_idx,
                21,
                listen,
            )
        )

    if not all_mismatches:
        print('OK: すべて公式 F 版解答と一致しました。')
        return 0

    print(f'不一致: {len(all_mismatches)} 件\n')
    for m in all_mismatches:
        print(
            f'  [{m.section}] {m.app_label} '
            f'({m.round_code} 本番Q{m.exam_no}): '
            f'リポジトリ={m.repo_choice} 公式={m.official_choice}'
        )
    return 1


if __name__ == '__main__':
    sys.exit(main())
