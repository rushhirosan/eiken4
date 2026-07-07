#!/usr/bin/env python3
"""
5級の正解を英検協会公式解答PDF（F日程）と照合する。

公式PDF: https://www.eiken.or.jp/eiken/result/pdf/{YYYYMM}F5kyu.pdf
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import fitz

_REPO = Path(__file__).resolve().parents[1]
_LEVEL5 = _REPO / 'data' / 'questions' / 'level5'

ROUND_CODES = ('202502', '202503', '202601')
OFFICIAL_PDF = _REPO / 'data' / 'pdf_import' / 'level5_kakomon'


@dataclass
class Mismatch:
    section: str
    app_label: str
    round_code: str
    exam_no: int
    repo_choice: int
    official_choice: int


def fetch_official_answers(code: str) -> tuple[dict[int, int], dict[int, int]]:
    path = OFFICIAL_PDF / f'{code}F5kyu_answers.pdf'
    text = ''.join(page.get_text() for page in fitz.open(path))
    rw: dict[int, int] = {}
    for mo in re.finditer(r'\((\d+)\)\s*(\d)', text):
        n, a = int(mo.group(1)), int(mo.group(2))
        if 1 <= n <= 25:
            rw[n] = a
    listening: dict[int, int] = {}
    m = re.search(r'5級リスニング\s*(.*)', text, re.DOTALL)
    if m:
        for mo in re.finditer(r'No\.\s*(\d+)\s+(\d)', m.group(1)[:3000]):
            listening[int(mo.group(1))] = int(mo.group(2))
    return rw, listening


def verify_grammar(round_idx: int, official_rw: dict[int, int]) -> list[Mismatch]:
    text = (_LEVEL5 / 'grammar_fill_questions.txt').read_text(encoding='utf-8')
    mismatches: list[Mismatch] = []
    q_start = round_idx * 15 + 1
    q_end = q_start + 14
    for mo in re.finditer(r'問題(\d+):.*?【正解\1】\s*(\d+)\.', text, re.DOTALL):
        qnum = int(mo.group(1))
        if not (q_start <= qnum <= q_end):
            continue
        repo = int(mo.group(2))
        exam_no = qnum - q_start + 1
        official = official_rw.get(exam_no)
        if official is not None and repo != official:
            mismatches.append(Mismatch('grammar_fill', f'問題{qnum}', ROUND_CODES[round_idx], exam_no, repo, official))
    return mismatches


def verify_conversation(round_idx: int, official_rw: dict[int, int]) -> list[Mismatch]:
    text = (_LEVEL5 / 'conversation_questions.txt').read_text(encoding='utf-8')
    mismatches: list[Mismatch] = []
    q_start = round_idx * 5 + 1
    q_end = q_start + 4
    for mo in re.finditer(r'問題(\d+):.*?【正解\1】\s*(\d+)\.', text, re.DOTALL):
        qnum = int(mo.group(1))
        if not (q_start <= qnum <= q_end):
            continue
        repo = int(mo.group(2))
        exam_no = 15 + (qnum - q_start + 1)
        official = official_rw.get(exam_no)
        if official is not None and repo != official:
            mismatches.append(Mismatch('conversation_fill', f'問題{qnum}', ROUND_CODES[round_idx], exam_no, repo, official))
    return mismatches


def verify_wordorder(round_idx: int, official_rw: dict[int, int]) -> list[Mismatch]:
    text = (_LEVEL5 / 'wordorder_questions.txt').read_text(encoding='utf-8')
    mismatches: list[Mismatch] = []
    q_start = round_idx * 5 + 1
    q_end = q_start + 4
    for mo in re.finditer(r'問題(\d+):.*?【正解\1】\s*(\d+)\.', text, re.DOTALL):
        qnum = int(mo.group(1))
        if not (q_start <= qnum <= q_end):
            continue
        repo = int(mo.group(2))
        exam_no = 20 + (qnum - q_start + 1)
        official = official_rw.get(exam_no)
        if official is not None and repo != official:
            mismatches.append(Mismatch('word_order', f'問題{qnum}', ROUND_CODES[round_idx], exam_no, repo, official))
    return mismatches


def verify_listening_part(
    filename: str,
    section: str,
    round_idx: int,
    per_round: int,
    exam_no_start: int,
    official_listen: dict[int, int],
) -> list[Mismatch]:
    text = (_LEVEL5 / filename).read_text(encoding='utf-8')
    mismatches: list[Mismatch] = []
    q_start = round_idx * per_round + 1
    q_end = q_start + per_round - 1
    for mo in re.finditer(r'【正解(\d+)】\s*(\d+)\.', text):
        qnum = int(mo.group(1))
        if not (q_start <= qnum <= q_end):
            continue
        repo = int(mo.group(2))
        exam_no = exam_no_start + (qnum - q_start)
        official = official_listen.get(exam_no)
        if official is not None and repo != official:
            mismatches.append(Mismatch(section, f'No.{qnum}', ROUND_CODES[round_idx], exam_no, repo, official))
    return mismatches


def main() -> int:
    all_mismatches: list[Mismatch] = []
    for round_idx, code in enumerate(ROUND_CODES):
        rw, listen = fetch_official_answers(code)
        all_mismatches.extend(verify_grammar(round_idx, rw))
        all_mismatches.extend(verify_conversation(round_idx, rw))
        all_mismatches.extend(verify_wordorder(round_idx, rw))
        all_mismatches.extend(
            verify_listening_part(
                'listening_illustration_questions.txt',
                'listening_illustration_p1',
                round_idx,
                10,
                1,
                listen,
            )
        )
        all_mismatches.extend(
            verify_listening_part(
                'listening_conversation_questions.txt',
                'listening_conversation',
                round_idx,
                5,
                11,
                listen,
            )
        )
        # Part3 は通し番号 31-60（round_idx*10 + 30 + offset）
        part3_start = 31 + round_idx * 10
        part3_end = part3_start + 9
        text = (_LEVEL5 / 'listening_illustration_questions.txt').read_text(encoding='utf-8')
        for mo in re.finditer(r'【正解(\d+)】\s*(\d+)\.', text):
            qnum = int(mo.group(1))
            if not (part3_start <= qnum <= part3_end):
                continue
            repo = int(mo.group(2))
            exam_no = 16 + (qnum - part3_start)
            official = listen.get(exam_no)
            if official is not None and repo != official:
                all_mismatches.append(
                    Mismatch(
                        'listening_illustration_p3',
                        f'No.{qnum}',
                        code,
                        exam_no,
                        repo,
                        official,
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
