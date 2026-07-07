#!/usr/bin/env python3
"""問題テキストの正解番号分布を表示する（偏りチェック用）。"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_LEVEL5 = _REPO / 'data' / 'questions' / 'level5'

FILES = (
    'grammar_fill_questions.txt',
    'conversation_questions.txt',
    'wordorder_questions.txt',
    'listening_illustration_questions.txt',
    'listening_conversation_questions.txt',
)


def histogram(path: Path) -> Counter:
    text = path.read_text(encoding='utf-8')
    counts: Counter = Counter()
    for mo in re.finditer(r'【正解(\d+)】\s*\n(\d+)\.', text):
        counts[int(mo.group(2))] += 1
    return counts


def main() -> int:
    for name in FILES:
        path = _LEVEL5 / name
        if not path.exists():
            print(f'MISSING: {path}')
            continue
        counts = histogram(path)
        total = sum(counts.values())
        print(f'\n{name} ({total} questions)')
        for choice in sorted(counts):
            bar = '#' * counts[choice]
            pct = round(counts[choice] / total * 100, 1) if total else 0
            print(f'  {choice}: {counts[choice]:3d} ({pct:4.1f}%) {bar}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
