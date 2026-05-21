#!/usr/bin/env python3
"""
3級リスニング第1部（イラスト問題）の画像を過去問 PDF から再抽出する。

data/questions/level3/listening_illustration_questions.txt は次の 3 回分を
1〜30 番に通し番号でまとめている:
  - No. 1〜10:  2025 第1回 (2025-1_3kyu.pdf)
  - No. 11〜20: 2025 第2回 (2025-2_3kyu.pdf) … 2 列レイアウトのため領域クリップ
  - No. 21〜30: 2025 第3回 (2025-3_3kyu.pdf)

出力: static/images/level3/part1/listening_illustration_image{N}.png
"""
from __future__ import annotations

import argparse
import io
import os
import sys

import fitz
from PIL import Image

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from utils.eiken_paths import static_images_part1

_PDF_DIR = os.path.join(_REPO, 'data', 'pdf_import', 'level3_kakomon')
_PDF_ROUND1 = os.path.join(_PDF_DIR, '2025-1_3kyu.pdf')
_PDF_ROUND2 = os.path.join(_PDF_DIR, '2025-2_3kyu.pdf')
_PDF_ROUND3 = os.path.join(_PDF_DIR, '2025-3_3kyu.pdf')

# 2025-3 第1部: PDF 上の No. ラベル順の埋め込み画像と、台本 No. の対応が一致しない。
# 台本・listening_illustration_questions.txt の No.21–30 に合わせて並べ替える（0-based）。
_ROUND3_IMAGE_PERMUTATION = [0, 1, 2, 3, 6, 9, 4, 8, 5, 7]

# 2025-2 第1部: ページ 12 に No.1–2、ページ 13 に No.3–10（2 列）
_ROUND2_CLIPS = [
    (12, fitz.Rect(35, 630, 295, 790)),
    (12, fitz.Rect(300, 630, 560, 790)),
    (13, fitz.Rect(35, 190, 295, 335)),
    (13, fitz.Rect(300, 190, 560, 335)),
    (13, fitz.Rect(35, 335, 295, 485)),
    (13, fitz.Rect(300, 335, 560, 485)),
    (13, fitz.Rect(35, 485, 295, 635)),
    (13, fitz.Rect(300, 485, 560, 635)),
    (13, fitz.Rect(35, 635, 295, 785)),
    (13, fitz.Rect(300, 635, 560, 785)),
]


def _save_pixmap(pix: fitz.Pixmap, path: str) -> None:
    image = Image.open(io.BytesIO(pix.tobytes('png')))
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image.save(path, 'PNG', quality=95)


def _page_images_sorted(page: fitz.Page) -> list[tuple[int, Image.Image]]:
    """ページ上の位置（上→下、左→右）で埋め込み画像を並べる。"""
    seen: set[int] = set()
    items: list[tuple[float, float, int]] = []
    for info in page.get_image_info(xrefs=True):
        xref = info.get('xref')
        if xref is None or xref in seen:
            continue
        seen.add(xref)
        y0, x0, _, _ = info['bbox']
        items.append((y0, x0, xref))
    # 2 列配置のページでは y だけだと左右が逆になるため、行バケット後に x で整列
    items.sort(key=lambda t: (round(t[0] / 120), t[1]))
    images: list[tuple[int, Image.Image]] = []
    for _, _, xref in items:
        base = page.parent.extract_image(xref)
        image = Image.open(io.BytesIO(base['image']))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        images.append((xref, image))
    return images


def _extract_embedded_part1(pdf_path: str, pages_1based: list[int]) -> list[Image.Image]:
    """第1回・第3回 PDF: ページ 12 の先頭（例題）を除き、埋め込み画像を順に取得。"""
    doc = fitz.open(pdf_path)
    images: list[Image.Image] = []
    first_page = True
    for page_no in pages_1based:
        page = doc[page_no - 1]
        page_images = _page_images_sorted(page)
        start = 1 if first_page else 0
        first_page = False
        for _, image in page_images[start:]:
            images.append(image)
    doc.close()
    return images


def _extract_clipped_round2(pdf_path: str) -> list[Image.Image]:
    doc = fitz.open(pdf_path)
    zoom = fitz.Matrix(2, 2)
    images: list[Image.Image] = []
    for page_no, rect in _ROUND2_CLIPS:
        page = doc[page_no - 1]
        pix = page.get_pixmap(matrix=zoom, clip=rect)
        image = Image.open(io.BytesIO(pix.tobytes('png')))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        images.append(image)
    doc.close()
    return images


def extract_all(output_dir: str | None = None) -> int:
    out = output_dir or static_images_part1('3')
    os.makedirs(out, exist_ok=True)

    batches = [
        (_PDF_ROUND1, 'embedded', [12, 13]),
        (_PDF_ROUND2, 'clip', None),
        (_PDF_ROUND3, 'embedded', [12, 13]),
    ]
    number = 1
    for pdf_path, mode, pages in batches:
        if not os.path.isfile(pdf_path):
            raise FileNotFoundError(f'PDF not found: {pdf_path}')
        if mode == 'embedded':
            images = _extract_embedded_part1(pdf_path, pages)
            if pdf_path == _PDF_ROUND3:
                images = [images[i] for i in _ROUND3_IMAGE_PERMUTATION]
        else:
            images = _extract_clipped_round2(pdf_path)
        if len(images) != 10:
            raise RuntimeError(f'{pdf_path}: expected 10 images, got {len(images)}')
        for image in images:
            path = os.path.join(out, f'listening_illustration_image{number}.png')
            image.save(path, 'PNG', quality=95)
            print(f'wrote {path}')
            number += 1
    return number - 1


def main() -> None:
    parser = argparse.ArgumentParser(description='3級イラストリスニング画像を PDF から再抽出')
    parser.add_argument(
        '-o', '--output-dir',
        default=static_images_part1('3'),
        help='出力ディレクトリ（既定: static/images/level3/part1）',
    )
    args = parser.parse_args()
    total = extract_all(args.output_dir)
    print(f'完了: {total} 件を {args.output_dir} に保存しました')


if __name__ == '__main__':
    main()
