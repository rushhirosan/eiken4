#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""保管 txt と original のリスニング疑問詞焦点の偏りを比較する（任意・warn 中心）。

release / preflight には入れない。作問前の穴探し用。

  python scripts/check_inventory_coverage.py --level 4
  python scripts/check_inventory_coverage.py --level 3,4,5
  python scripts/check_inventory_coverage.py --level 4 --fail-on-gap
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from collections import Counter
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent

LISTENING_FILES = (
    "listening_illustration_questions.txt",
    "listening_conversation_questions.txt",
    "listening_passage_questions.txt",
)


def _load_goi():
    path = SCRIPTS / "gen_official_inventory.py"
    spec = importlib.util.spec_from_file_location("gen_official_inventory", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gen_official_inventory"] = mod
    spec.loader.exec_module(mod)
    return mod


def _original_dir(level: str) -> Path:
    return ROOT / "data" / "questions" / "original" / f"level{level}"


def _focus_counts(goi, path: Path) -> Counter:
    items = goi.parse_listening(path)
    c: Counter = Counter()
    for it in items:
        q = (it.get("question") or "").strip()
        if not q:
            continue
        c[goi.q_focus(q)] += 1
    return c


def _share(c: Counter) -> dict[str, float]:
    total = sum(c.values())
    if total == 0:
        return {}
    return {k: v / total for k, v in c.items()}


def _compare_level(goi, level: str, min_archive: int, gap: float) -> list[str]:
    """Return human-readable gap lines for one level."""
    lines: list[str] = []
    archive_root = goi.data_dir(level)
    original_root = _original_dir(level)

    for name in LISTENING_FILES:
        a_path = archive_root / name
        o_path = original_root / name
        if not a_path.exists() or not o_path.exists():
            continue
        a_c = _focus_counts(goi, a_path)
        o_c = _focus_counts(goi, o_path)
        if sum(a_c.values()) < min_archive or sum(o_c.values()) == 0:
            continue
        a_s = _share(a_c)
        o_s = _share(o_c)
        cat = name.replace("_questions.txt", "")
        hits = []
        for focus, a_ratio in sorted(a_s.items(), key=lambda x: -x[1]):
            if focus == "その他":
                continue
            o_ratio = o_s.get(focus, 0.0)
            if a_ratio - o_ratio >= gap:
                hits.append(
                    f"  - {focus}: archive {a_c[focus]}/{sum(a_c.values())} "
                    f"({a_ratio:.0%}) vs original {o_c.get(focus, 0)}/{sum(o_c.values())} "
                    f"({o_ratio:.0%})  Δ={a_ratio - o_ratio:.0%}"
                )
        if hits:
            lines.append(f"level{level} / {cat}")
            lines.extend(hits)
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare listening question-focus coverage: archive txt vs original."
    )
    parser.add_argument(
        "--level",
        required=True,
        help="級（3 / 4 / 5）。カンマ区切り可",
    )
    parser.add_argument(
        "--gap",
        type=float,
        default=0.08,
        help="archive 比率 − original 比率がこの値以上なら報告（既定 0.08）",
    )
    parser.add_argument(
        "--min-archive",
        type=int,
        default=10,
        help="保管側の質問数がこれ未満のカテゴリはスキップ（既定 10）",
    )
    parser.add_argument(
        "--fail-on-gap",
        action="store_true",
        help="ギャップがあれば exit 1（既定は warn のみ exit 0）",
    )
    args = parser.parse_args(argv)

    levels: list[str] = []
    for part in args.level.split(","):
        part = part.strip()
        if part not in ("3", "4", "5"):
            print(f"error: invalid level {part!r}", file=sys.stderr)
            return 2
        if part not in levels:
            levels.append(part)

    goi = _load_goi()
    all_gaps: list[str] = []
    for level in levels:
        all_gaps.extend(
            _compare_level(goi, level, args.min_archive, args.gap)
        )

    if not all_gaps:
        print(
            f"OK: no listening-focus gaps ≥ {args.gap:.0%} "
            f"(levels={','.join(levels)}; advisory only)"
        )
        return 0

    print(
        f"Listening focus gaps (archive share − original share ≥ {args.gap:.0%}):"
    )
    print("(advisory — not part of release/preflight)")
    for line in all_gaps:
        print(line)
    print(
        "\nHint: pick 1–few missing focuses when authoring; "
        "see docs/inventory/official_update_flow.md"
    )
    return 1 if args.fail_on_gap else 0


if __name__ == "__main__":
    raise SystemExit(main())
