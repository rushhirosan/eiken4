#!/usr/bin/env python3
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
        
        # テキストをファイルに保存
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(all_text)
            print(f"テキストを {output_path} に保存しました。")
            
        return all_text
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return None

def main():
    # 設定
    pdf_path = "/Users/igusahiroyuki/Downloads/eiken/2024-1-1ji-script-4kyu.pdf"
    output_path = "output.txt"
    
    # 全ページを抽出する場合
    text = extract_text_from_pdf(pdf_path, output_path)
    
    # 特定のページ範囲を抽出する場合（例：14-16ページ）
    # text = extract_text_from_pdf(pdf_path, output_path, page_range=(13, 15))
    
    if text:
        print(f"抽出文字数: {len(text)}")
        print("\n=== 抽出テキストの最初の500文字 ===\n")
        print(text[:500])

if __name__ == "__main__":
    main() 