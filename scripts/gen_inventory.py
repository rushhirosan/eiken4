#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公式保管問題の inventory 再生成エントリ（級共通の入口）。

既存ロジックは触らず振り分けるだけ:
  - 3級: gen_level3_inventory.generate_level3
  - 4/5級: gen_official_inventory.generate_level
  - README: gen_official_inventory.update_readme（一本化）
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
INV = ROOT / "docs" / "inventory"


def _load(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _parse_levels(raw: str | None, all_levels: bool) -> list[str]:
    if all_levels:
        return ["3", "4", "5"]
    if not raw:
        raise SystemExit("error: --level or --all is required")
    levels: list[str] = []
    for part in raw.split(","):
        part = part.strip()
        if part not in ("3", "4", "5"):
            raise SystemExit(f"error: invalid level {part!r} (use 3, 4, 5)")
        if part not in levels:
            levels.append(part)
    return levels


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate docs/inventory from official archive question txts."
    )
    parser.add_argument(
        "--level",
        help="級（3 / 4 / 5）。カンマ区切り可（例: 4,5）",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="3・4・5 すべて再生成して README を更新",
    )
    parser.add_argument(
        "--no-readme",
        action="store_true",
        help="README.md を更新しない（級 md のみ）",
    )
    args = parser.parse_args(argv)

    levels = _parse_levels(args.level, args.all)
    goi = _load("gen_official_inventory")
    gl3 = _load("gen_level3_inventory")

    written: dict[str, list[str]] = {}
    for level in levels:
        if level == "3":
            files = gl3.generate_level3()
        else:
            files = sorted(goi.generate_level(level))
        written[level] = files
        print(f"level{level}:", ", ".join(files) if files else "(none)")

    if not args.no_readme:
        results = goi.collect_level_files(written)
        goi.update_readme(results)
        print("README updated")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
