#!/usr/bin/env python3
"""語順問題テキストの枠・①〜④・正解ラベルを機械検算する。

①〜④（各番号は1語でも句でも可）が [1番目]( )[3番目]( ) の4マスに入り、
固定部分との二重書きが無く、【正解】の1番目・3番目が再構成と一致することを確認する。

例:
  python utils/validate_wordorder_questions.py
  python utils/validate_wordorder_questions.py data/questions/original/level5/wordorder_questions.txt
  python utils/validate_wordorder_questions.py --level 5 --original
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]

# ①〜④は改行または選択肢行の手前まで。各スロットは空白を含んでよい。
_CIRCLED = re.compile(
    r'①\s*(.+?)\s*②\s*(.+?)\s*③\s*(.+?)\s*④\s*(.+?)(?:\n|\r|$)',
    re.DOTALL,
)
_FRAME = re.compile(
    r'^(.*?)\s*\[1番目\]\s*\(\s*\)\s*\[3番目\]\s*\(\s*\)\s*(.*)$'
)
_CORRECT = re.compile(
    r'【正解(\d+)】\s*\n?\s*(\d+)\.\s*(①|②|③|④)\s*[─\-]\s*(①|②|③|④)'
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

    # ①〜④は問題文ブロック内（選択肢より前）から取る
    head = block.split('選択肢')[0]
    circ_m = _CIRCLED.search(head)
    if not circ_m:
        return [Issue(n, '①〜④が読めない')]
    raw_phrases = [p.strip() for p in circ_m.groups()]
    phrases = {lab: _phrase_tokens(raw) for lab, raw in zip('①②③④', raw_phrases)}
    if any(not phrases[lab] for lab in '①②③④'):
        return [Issue(n, f'①〜④に空スロットがある: {raw_phrases}')]

    frame_line = next((ln.strip() for ln in block.splitlines() if '[1番目]' in ln), None)
    if not frame_line:
        return [Issue(n, '英語枠（[1番目]）が無い')]

    frame_m = _FRAME.match(frame_line)
    if not frame_m:
        return [Issue(n, f'枠形式が不正: {frame_line}')]
    prefix = _norm_tokens(frame_m.group(1).split())
    suffix = _norm_tokens(frame_m.group(2).split())

    full_m = _FULL.search(block)
    if not full_m:
        return [Issue(n, '解説先頭の正解全文が無い')]
    full = full_m.group(2).strip()
    # 解説1行目が「I walk...」以外（説明文）のときは英語全文だけ拾う
    full_words = _phrase_tokens(full)
    # まれに解説が「正解は…」で始まる場合はスキップ扱いにする
    if full_words and full_words[0] in {'正解は', '1番目は'}:
        return [Issue(n, f'解説先頭が英文全文でない: {full}')]

    corr_m = _CORRECT.search(block)
    if not corr_m:
        return [Issue(n, '【正解】の ①─③ 形式が読めない')]
    label_1, label_3 = corr_m.group(3), corr_m.group(4)

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

    # mid を①〜④の4フレーズの順列として消費できるか
    order = _match_phrase_order(mid, phrases)
    if order is None:
        issues.append(
            Issue(
                n,
                f'4マスの語列 {mid} を①〜④ {[raw_phrases]} の順列として再構成できない（枠={frame_line}）',
            )
        )
        return issues

    if order[0] != label_1 or order[2] != label_3:
        issues.append(
            Issue(
                n,
                f'正解 {label_1}─{label_3} が再構成の1・3マス（{order[0]}─{order[2]}）と不一致',
            )
        )

    # 二重書き: 固定トークンが、4マス側フレーズのトークンと重なり全文カウントが足りない
    flat_circled = [t for lab in '①②③④' for t in phrases[lab]]
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
                    f'①〜④の要素 {tok!r} が枠固定にもあり二重 '
                    f'(full={in_full}, mid={in_mid}, fixed={in_fixed}): {frame_line}',
                )
            )

    return issues


def _match_phrase_order(mid: list[str], phrases: dict[str, list[str]]) -> list[str] | None:
    """mid トークン列を4フレーズの順列でちょうど消費できるラベル順を返す。"""
    labels = list('①②③④')
    mid_cf = _cf(mid)

    def dfs(pos: int, used: set[str], acc: list[str]) -> list[str] | None:
        if len(acc) == 4:
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
