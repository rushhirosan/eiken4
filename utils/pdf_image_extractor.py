#!/usr/bin/env python3
import os
import fitz  # PyMuPDF
from PIL import Image
import io
import numpy as np

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
        
        # 出力ディレクトリが指定されている場合は作成
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"出力ディレクトリを作成しました: {output_dir}")
        
        image_counter = start_number
        total_images = 0
        
        # 各ページを処理
        for page_num in range(len(doc)):
            print(f"ページ {page_num + 1} を処理しています...")
            page = doc[page_num]
            
            # 画像の位置情報を取得
            image_list = page.get_images(full=True)
            print(f"見つかった画像の数: {len(image_list)}")
            
            # 各画像を処理
            for img_index, img in enumerate(image_list):
                try:
                    print(f"画像 {img_index + 1} を処理しています...")
                    
                    # 画像の位置情報を取得
                    xref = img[0]
                    
                    # 画像を抽出
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # 画像をPIL.Imageオブジェクトに変換
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # 画像のモードを確認し、必要に応じて変換
                    if image.mode == 'CMYK':
                        image = image.convert('RGB')
                    elif image.mode == 'RGBA':
                        image = image.convert('RGB')
                    elif image.mode == 'L':
                        image = image.convert('RGB')
                    
                    # 画像が反転しているかチェック（黒背景問題の解決）
                    if image.mode == 'RGB':
                        img_array = np.array(image)
                        # 暗いピクセル（値が50未満）の割合を計算
                        dark_pixels = np.sum(img_array < 50)
                        total_pixels = img_array.shape[0] * img_array.shape[1] * img_array.shape[2]
                        dark_ratio = dark_pixels / total_pixels
                        
                        # 暗いピクセルが50%以上ある場合、画像を反転
                        if dark_ratio > 0.5:
                            print(f"画像が反転しているため、色を反転します（暗いピクセル割合: {dark_ratio:.2%}）")
                            img_array = 255 - img_array
                            image = Image.fromarray(img_array, mode='RGB')
                    
                    # 画像を保存
                    if output_dir:
                        output_path = os.path.join(output_dir, f"listening_illustration_image{image_counter}.png")
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
    # 設定
    pdf_path = "/Users/igusahiroyuki/Downloads/eiken/2025-1-1ji-4kyu.pdf"
    output_dir = "static/images/part1"
    start_number = 31  # 画像ファイル名の開始番号
    
    # 画像を抽出
    total_images = extract_images_from_pdf(pdf_path, output_dir, start_number)
    
    if total_images > 0:
        print(f"画像抽出が完了しました。{total_images}個の画像を抽出しました。")
    else:
        print("画像の抽出に失敗しました。")

if __name__ == "__main__":
    main() 