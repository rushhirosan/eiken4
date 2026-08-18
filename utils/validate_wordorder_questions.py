#!/usr/bin/env python3
"""語順問題テキストの枠・番号チップ・正解ラベルを機械検算する。

5級: ①〜④が [1番目]( )[3番目]( ) の4マスに入る。正解は1番目と3番目。
4級・3級: ①〜⑤が ( )[2番目]( )[4番目]( ) の5マスに入る。正解は2番目と4番目。
固定部分との二重書きが無く、【正解】ラベルが再構成と一致することを確認する。

例:
  python utils/validate_wordorder_questions.py
  python utils/validate_wordorder_questions.py data/questions/original/level5/wordorder_questions.txt
  python utils/validate_wordorder_questions.py --level 4 --original
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]

# チップは改行または選択肢行の手前まで。各スロットは空白を含んでよい。
_CIRCLED4 = re.compile(
    r'①\s*(.+?)\s*②\s*(.+?)\s*③\s*(.+?)\s*④\s*(.+?)(?:\n|\r|$)',
    re.DOTALL,
)
_CIRCLED5 = re.compile(
    r'①\s*(.+?)\s*②\s*(.+?)\s*③\s*(.+?)\s*④\s*(.+?)\s*⑤\s*(.+?)(?:\n|\r|$)',
    re.DOTALL,
)
_FRAME4 = re.compile(
    r'^(.*?)\s*\[1番目\]\s*\(\s*\)\s*\[3番目\]\s*\(\s*\)\s*(.*)$'
)
_FRAME5 = re.compile(
    r'^(.*?)\s*\(\s*\)\s*\[2番目\]\s*\(\s*\)\s*\[4番目\]\s*\(\s*\)\s*(.*)$'
)
_CORRECT4 = re.compile(
    r'【正解(\d+)】\s*\n?\s*(\d+)\.\s*(①|②|③|④)\s*[─\-]\s*(①|②|③|④)'
)
_CORRECT5 = re.compile(
    r'【正解(\d+)】\s*\n?\s*(\d+)\.\s*(①|②|③|④|⑤)\s*[─\-]\s*(①|②|③|④|⑤)'
)
_FULL = re.compile(r'【解説(\d+)】\s*([^\n]+)')
_NUM = re.compile(r'問題(\d+):')


def _norm_tokens(parts: list[str]) -> list[str]:
    out: list[str] = []
    for p in parts:
        t = p.strip().strip('.,!?;:「」\'"')
        # 全角アポストロフィを統一
        t = t.replace('’', "'").replace('′', "'")
        if t:
            out.append(t)
    return out


def _phrase_tokens(phrase: str) -> list[str]:
    return _norm_tokens(phrase.replace('\n', ' ').split())


def _cf(tokens: list[str]) -> list[str]:
    return [t.casefold() for t in tokens]


@dataclass
class Issue:
    number: int
    message: str


def _parse_blocks(text: str) -> list[str]:
    return [b.strip() for b in text.split('---') if b.strip()]


def validate_block(block: str) -> list[Issue]:
    issues: list[Issue] = []
    num_m = _NUM.search(block)
    if not num_m:
        return [Issue(0, '問題番号が無い')]
    n = int(num_m.group(1))

    head = block.split('選択肢')[0]
    five = '[2番目]' in block or '⑤' in head
    if five:
        circ_m = _CIRCLED5.search(head)
        labels = list('①②③④⑤')
        slot_count = 5
        asked = (1, 3)  # 2番目・4番目（0-index）
        asked_name = '2・4マス'
        frame_line = next((ln.strip() for ln in block.splitlines() if '[2番目]' in ln), None)
        frame_re = _FRAME5
        corr_re = _CORRECT5
        chip_name = '①〜⑤'
        empty_frame_msg = '英語枠（[2番目]）が無い'
    else:
        circ_m = _CIRCLED4.search(head)
        labels = list('①②③④')
        slot_count = 4
        asked = (0, 2)
        asked_name = '1・3マス'
        frame_line = next((ln.strip() for ln in block.splitlines() if '[1番目]' in ln), None)
        frame_re = _FRAME4
        corr_re = _CORRECT4
        chip_name = '①〜④'
        empty_frame_msg = '英語枠（[1番目]）が無い'

    if not circ_m:
        return [Issue(n, f'{chip_name}が読めない')]
    raw_phrases = [p.strip() for p in circ_m.groups()]
    phrases = {lab: _phrase_tokens(raw) for lab, raw in zip(labels, raw_phrases)}
    if any(not phrases[lab] for lab in labels):
        return [Issue(n, f'{chip_name}に空スロットがある: {raw_phrases}')]

    if not frame_line:
        return [Issue(n, empty_frame_msg)]

    frame_m = frame_re.match(frame_line)
    if not frame_m:
        return [Issue(n, f'枠形式が不正: {frame_line}')]
    prefix = _norm_tokens(frame_m.group(1).split())
    suffix = _norm_tokens(frame_m.group(2).split())

    full_m = _FULL.search(block)
    if not full_m:
        return [Issue(n, '解説先頭の正解全文が無い')]
    full = full_m.group(2).strip()
    full_words = _phrase_tokens(full)
    if full_words and full_words[0] in {'正解は', '1番目は', '2番目は'}:
        return [Issue(n, f'解説先頭が英文全文でない: {full}')]

    corr_m = corr_re.search(block)
    if not corr_m:
        return [Issue(n, '【正解】の ①─③ 形式が読めない')]
    label_a, label_b = corr_m.group(3), corr_m.group(4)

    if _cf(full_words[: len(prefix)]) != _cf(prefix):
        issues.append(
            Issue(n, f'全文先頭が枠前置と不一致: prefix={prefix} full_head={full_words[: len(prefix) + 2]}')
        )
        return issues

    mid = full_words[len(prefix) :]
    if suffix:
        if _cf(mid[-len(suffix) :]) != _cf(suffix):
            issues.append(
                Issue(n, f'全文末尾が枠後置と不一致: suffix={suffix} tail={mid[-len(suffix) :]}')
            )
            return issues
        mid = mid[: -len(suffix)]

    order = _match_phrase_order(mid, phrases, labels, slot_count)
    if order is None:
        issues.append(
            Issue(
                n,
                f'{slot_count}マスの語列 {mid} を{chip_name} {[raw_phrases]} の順列として再構成できない（枠={frame_line}）',
            )
        )
        return issues

    got_a, got_b = order[asked[0]], order[asked[1]]
    if got_a != label_a or got_b != label_b:
        issues.append(
            Issue(
                n,
                f'正解 {label_a}─{label_b} が再構成の{asked_name}（{got_a}─{got_b}）と不一致',
            )
        )

    flat_circled = [t for lab in labels for t in phrases[lab]]
    fixed = prefix + suffix
    for tok in flat_circled:
        in_fixed = sum(1 for f in fixed if f.casefold() == tok.casefold())
        if not in_fixed:
            continue
        in_mid = sum(1 for m in mid if m.casefold() == tok.casefold())
        in_full = sum(1 for f in full_words if f.casefold() == tok.casefold())
        if in_full < in_mid + in_fixed:
            issues.append(
                Issue(
                    n,
                    f'{chip_name}の要素 {tok!r} が枠固定にもあり二重 '
                    f'(full={in_full}, mid={in_mid}, fixed={in_fixed}): {frame_line}',
                )
            )

    return issues


def _match_phrase_order(
    mid: list[str], phrases: dict[str, list[str]], labels: list[str], slot_count: int
) -> list[str] | None:
    """mid トークン列をフレーズの順列でちょうど消費できるラベル順を返す。"""
    mid_cf = _cf(mid)

    def dfs(pos: int, used: set[str], acc: list[str]) -> list[str] | None:
        if len(acc) == slot_count:
            return acc if pos == len(mid_cf) else None
        for lab in labels:
            if lab in used:
                continue
            toks = _cf(phrases[lab])
            end = pos + len(toks)
            if mid_cf[pos:end] == toks:
                got = dfs(end, used | {lab}, acc + [lab])
                if got is not None:
                    return got
        return None

    return dfs(0, set(), [])


def validate_file(path: Path) -> list[Issue]:
    text = path.read_text(encoding='utf-8')
    issues: list[Issue] = []
    for block in _parse_blocks(text):
        issues.extend(validate_block(block))
    return issues


def _default_original(level: str) -> Path:
    return _REPO / 'data' / 'questions' / 'original' / f'level{level}' / 'wordorder_questions.txt'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'path',
        nargs='?',
        type=Path,
        help='wordorder_questions.txt のパス（省略時は original/level5）',
    )
    parser.add_argument('--level', default='5', help='--original 時の級（既定 5）')
    parser.add_argument(
        '--original',
        action='store_true',
        help='data/questions/original/level{N}/wordorder_questions.txt を使う',
    )
    args = parser.parse_args(argv)

    if args.path:
        path = args.path if args.path.is_absolute() else _REPO / args.path
    elif args.original:
        path = _default_original(args.level)
    else:
        path = _default_original('5')

    if not path.exists():
        print(f'MISSING: {path}', file=sys.stderr)
        return 2

    issues = validate_file(path)
    rel = path.relative_to(_REPO) if path.is_relative_to(_REPO) else path
    if not issues:
        blocks = _parse_blocks(path.read_text(encoding='utf-8'))
        print(f'OK: {rel} ({len(blocks)} questions)')
        return 0

    print(f'FAIL: {rel} ({len(issues)} issue(s))', file=sys.stderr)
    for issue in issues:
        print(f'  Q{issue.number}: {issue.message}', file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
