#!/usr/bin/env python3
import argparse
import io
import os

import fitz  # PyMuPDF
import numpy as np
from PIL import Image


def extract_images_from_pdf(pdf_path, output_dir=None, start_number=1):
    """
    PDFファイルから画像を抽出する

    Args:
        pdf_path (str): PDFファイルのパス
        output_dir (str, optional): 出力ディレクトリのパス
        start_number (int): 画像ファイル名の開始番号

    Returns:
        int: 抽出された画像の数
    """
    try:
        print(f"PDFファイルを開いています: {pdf_path}")
        doc = fitz.open(pdf_path)

        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"出力ディレクトリを作成しました: {output_dir}")

        image_counter = start_number
        total_images = 0

        for page_num in range(len(doc)):
            print(f"ページ {page_num + 1} を処理しています...")
            page = doc[page_num]

            image_list = page.get_images(full=True)
            print(f"見つかった画像の数: {len(image_list)}")

            for img_index, img in enumerate(image_list):
                try:
                    print(f"画像 {img_index + 1} を処理しています...")

                    xref = img[0]

                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]

                    image = Image.open(io.BytesIO(image_bytes))

                    if image.mode == 'CMYK':
                        image = image.convert('RGB')
                    elif image.mode == 'RGBA':
                        image = image.convert('RGB')
                    elif image.mode == 'L':
                        image = image.convert('RGB')

                    if image.mode == 'RGB':
                        img_array = np.array(image)
                        dark_pixels = np.sum(img_array < 50)
                        total_pixels = img_array.shape[0] * img_array.shape[1] * img_array.shape[2]
                        dark_ratio = dark_pixels / total_pixels

                        if dark_ratio > 0.5:
                            print(f"画像が反転しているため、色を反転します（暗いピクセル割合: {dark_ratio:.2%}）")
                            img_array = 255 - img_array
                            image = Image.fromarray(img_array, mode='RGB')

                    if output_dir:
                        output_path = os.path.join(
                            output_dir, f"listening_illustration_image{image_counter}.png"
                        )
                        image.save(output_path, "PNG", quality=95)
                        print(f"画像を {output_path} に保存しました。")
                        image_counter += 1
                        total_images += 1

                except Exception as e:
                    print(f"画像 {img_index + 1} の処理中にエラーが発生しました: {str(e)}")
                    continue

        doc.close()
        print(f"合計 {total_images} 個の画像を抽出しました。")
        return total_images

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description='PDF から画像を抽出する（既定は 4級の static/images/part1）'
    )
    parser.add_argument('--pdf', default=os.environ.get('EIKEN_PDF_PATH'), help='入力 PDF')
    parser.add_argument(
        '--output-dir', '-o',
        default=os.environ.get('EIKEN_IMAGE_OUTPUT_DIR', 'static/images/part1'),
        help='出力ディレクトリ（例: static/images/level3/part1）',
    )
    parser.add_argument(
        '--start-number',
        type=int,
        default=int(os.environ.get('EIKEN_IMAGE_START', '1')),
        help='ファイル名 listening_illustration_image{N} の N 開始値',
    )
    args = parser.parse_args()

    if not args.pdf:
        parser.error('--pdf を指定するか、環境変数 EIKEN_PDF_PATH を設定してください')

    total_images = extract_images_from_pdf(args.pdf, args.output_dir, args.start_number)

    if total_images > 0:
        print(f"画像抽出が完了しました。{total_images}個の画像を抽出しました。")
    else:
        print("画像の抽出に失敗しました。")


if __name__ == "__main__":
    main()
