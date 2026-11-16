#!/usr/bin/env python3
import argparse
import os

import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path, output_path=None, page_range=None):
    """
    PDFファイルからテキストを抽出する

    Args:
        pdf_path (str): PDFファイルのパス
        output_path (str, optional): 出力ファイルのパス
        page_range (tuple, optional): ページ範囲 (start, end) 0から始まる

    Returns:
        str: 抽出されたテキスト
    """
    try:
        doc = fitz.open(pdf_path)
        all_text = ""

        if page_range:
            start_page, end_page = page_range
            pages = range(start_page, end_page + 1)
        else:
            pages = range(len(doc))

        for page_num in pages:
            page = doc[page_num]
            page_text = page.get_text()
            if page_range:
                all_text += f"\n=== ページ {page_num + 1} ===\n"
            all_text += page_text
            all_text += "\n"

        doc.close()

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(all_text)
            print(f"テキストを {output_path} に保存しました。")

        return all_text

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='PDF からテキストを抽出する（既定パスは EIKEN_* 環境変数で上書き可能）'
    )
    parser.add_argument('--pdf', default=os.environ.get('EIKEN_PDF_PATH'), help='入力 PDF')
    parser.add_argument(
        '--output', '-o',
        default=os.environ.get('EIKEN_TEXT_OUTPUT', 'output.txt'),
        help='出力テキストファイル',
    )
    parser.add_argument('--page-start', type=int, default=None, help='開始ページ（0始まり）')
    parser.add_argument('--page-end', type=int, default=None, help='終了ページ（0始まり・含む）')
    args = parser.parse_args()

    if not args.pdf:
        parser.error('--pdf を指定するか、環境変数 EIKEN_PDF_PATH を設定してください')

    page_range = None
    if args.page_start is not None or args.page_end is not None:
        if args.page_start is None or args.page_end is None:
            parser.error('--page-start と --page-end は両方指定してください')
        page_range = (args.page_start, args.page_end)

    text = extract_text_from_pdf(args.pdf, args.output, page_range=page_range)

    if text:
        print(f"抽出文字数: {len(text)}")
        print("\n=== 抽出テキストの最初の500文字 ===\n")
        print(text[:500])


if __name__ == "__main__":
    main()
