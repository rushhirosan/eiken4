#!/usr/bin/env python3
"""英検5級リスニング問題冊子PDFからイラストを切り出して static に配置する。

過去問 PDF の囲み枠（get_drawings）を検出して切り出す。
  Part1: listening_illustration_image{1-30}.png
  Part3: listening_illustration_image{31-60}.png
"""
from __future__ import annotations

from pathlib import Path

import fitz

_REPO = Path(__file__).resolve().parents[1]
_PDF_DIR = _REPO / 'data' / 'pdf_import' / 'level5_kakomon'
_OUT_DIR = _REPO / 'static' / 'images' / 'level5' / 'part1'

ROUNDS = (
    {'exam_pdf': '2025-2-1ji-5kyu.pdf', 'p1_start': 1, 'p3_start': 31},
    {'exam_pdf': '2025-3-1ji-5kyu.pdf', 'p1_start': 11, 'p3_start': 41},
    {'exam_pdf': '2026-1-1ji-5kyu.pdf', 'p1_start': 21, 'p3_start': 51},
)

# (page_index, local_question_numbers_in_order)
_PART1_PAGES = (
    (5, list(range(1, 3))),    # page 6: No.1–2
    (6, list(range(3, 11))),   # page 7: No.3–10
)
_PART3_PAGES = (
    (8, list(range(16, 22))),  # page 9: No.16–21
    (9, list(range(22, 26))),  # page 10: No.22–25
)


def _illustration_boxes(page: fitz.Page) -> list[fitz.Rect]:
    """ページ内のイラスト枠（近似重複・内包除去・左上からソート）。"""
    raw: list[fitz.Rect] = []
    for drawing in page.get_drawings():
        rect = drawing.get('rect')
        if rect is None:
            continue
        if not (100 < rect.width < 300 and 60 < rect.height < 200):
            continue
        raw.append(rect)

    merged: list[fitz.Rect] = []
    for rect in raw:
        replaced = False
        for idx, existing in enumerate(merged):
            if (
                abs(existing.x0 - rect.x0) <= 3
                and abs(existing.y0 - rect.y0) <= 3
                and abs(existing.x1 - rect.x1) <= 3
            ):
                merged[idx] = fitz.Rect(
                    min(existing.x0, rect.x0),
                    min(existing.y0, rect.y0),
                    max(existing.x1, rect.x1),
                    max(existing.y1, rect.y1),
                )
                replaced = True
                break
        if not replaced:
            merged.append(rect)

    outer: list[fitz.Rect] = []
    for rect in merged:
        rect_area = rect.width * rect.height
        if any(
            other != rect
            and other.x0 <= rect.x0 + 1
            and other.y0 <= rect.y0 + 1
            and other.x1 >= rect.x1 - 1
            and other.y1 >= rect.y1 - 1
            and other.width * other.height > rect_area * 1.05
            for other in merged
        ):
            continue
        outer.append(rect)

    outer.sort(key=lambda r: (round(r.y0 / 120), r.x0))
    return outer


def _save_crop(page: fitz.Page, rect: fitz.Rect, out_path: Path) -> None:
    pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), clip=rect, alpha=False)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(out_path))


def extract_all() -> int:
    total = 0
    for rnd in ROUNDS:
        pdf_path = _PDF_DIR / rnd['exam_pdf']
        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)
        doc = fitz.open(pdf_path)

        for page_index, local_numbers in _PART1_PAGES:
            boxes = _illustration_boxes(doc[page_index])
            if len(boxes) != len(local_numbers):
                raise ValueError(
                    f'{rnd["exam_pdf"]} page {page_index + 1}: '
                    f'expected {len(local_numbers)} boxes, found {len(boxes)}'
                )
            for local_no, rect in zip(local_numbers, boxes):
                global_no = rnd['p1_start'] + local_no - 1
                out = _OUT_DIR / f'listening_illustration_image{global_no}.png'
                _save_crop(doc[page_index], rect, out)
                total += 1

        for page_index, local_numbers in _PART3_PAGES:
            boxes = _illustration_boxes(doc[page_index])
            if len(boxes) != len(local_numbers):
                raise ValueError(
                    f'{rnd["exam_pdf"]} page {page_index + 1}: '
                    f'expected {len(local_numbers)} boxes, found {len(boxes)}'
                )
            for local_no, rect in zip(local_numbers, boxes):
                global_no = rnd['p3_start'] + (local_no - 16)
                out = _OUT_DIR / f'listening_illustration_image{global_no}.png'
                _save_crop(doc[page_index], rect, out)
                total += 1

        doc.close()
        print(
            f'{rnd["exam_pdf"]}: P1 {rnd["p1_start"]}–{rnd["p1_start"] + 9}, '
            f'P3 {rnd["p3_start"]}–{rnd["p3_start"] + 9}'
        )
    print(f'Done. {total} images → {_OUT_DIR}')
    return total


def main() -> int:
    extract_all()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
