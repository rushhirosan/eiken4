#!/usr/bin/env python3
import fitz  # PyMuPDF

def main():
    pdf_path = "/Users/igusahiroyuki/Downloads/eiken/2024-2-1ji-script_4kyu.pdf"
    output_path = "output.txt"
    
    doc = fitz.open(pdf_path)
    all_text = ""
    for page in doc:
        all_text += page.get_text()
    doc.close()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(all_text)
    print(f"全ページ分のテキストを {output_path} に保存しました。\n抽出文字数: {len(all_text)}")
    print("\n=== 抽出テキストの最初の500文字 ===\n")
    print(all_text[:500])

if __name__ == "__main__":
    main() 