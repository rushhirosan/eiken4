import os
import re
from PyPDF2 import PdfReader
from PIL import Image
import io
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import tempfile
from gtts import gTTS

def clean_text(text):
    """
    テキストを整形する
    
    Args:
        text (str): 整形前のテキスト
        
    Returns:
        str: 整形後のテキスト
    """
    # 段落ごとに分割
    paragraphs = text.split('\n\n')
    cleaned_paragraphs = []
    
    for paragraph in paragraphs:
        # 段落内の連続するスペースを1つのスペースに置換
        paragraph = re.sub(r'\s+', ' ', paragraph)
        
        # 文末のピリオドの後のスペースを1つに統一
        paragraph = re.sub(r'\.\s+', '. ', paragraph)
        
        # カンマの後のスペースを1つに統一
        paragraph = re.sub(r',\s+', ', ', paragraph)
        
        # コロンの後のスペースを1つに統一
        paragraph = re.sub(r':\s+', ': ', paragraph)
        
        # セミコロンの後のスペースを1つに統一
        paragraph = re.sub(r';\s+', '; ', paragraph)
        
        # 疑問符の後のスペースを1つに統一
        paragraph = re.sub(r'\?\s+', '? ', paragraph)
        
        # 感嘆符の後のスペースを1つに統一
        paragraph = re.sub(r'!\s+', '! ', paragraph)
        
        # 括弧の前後のスペースを調整
        paragraph = re.sub(r'\s+\(', ' (', paragraph)
        paragraph = re.sub(r'\)\s+', ') ', paragraph)
        
        # 行頭のスペースを削除
        paragraph = re.sub(r'^\s+', '', paragraph)
        
        # 行末のスペースを削除
        paragraph = re.sub(r'\s+$', '', paragraph)
        
        # 空の段落はスキップ
        if not paragraph.strip():
            continue
            
        # 一般的な英語の表記ミスを修正
        replacements = {
            'i ': 'I ',  # 文頭の小文字のiを大文字に
            ' i ': ' I ',  # 文中の小文字のiを大文字に
            ' i\'': ' I\'',  # I'm, I've などのiを大文字に
            ' dont ': ' don\'t ',
            ' doesnt ': ' doesn\'t ',
            ' isnt ': ' isn\'t ',
            ' arent ': ' aren\'t ',
            ' wasnt ': ' wasn\'t ',
            ' werent ': ' weren\'t ',
            ' havent ': ' haven\'t ',
            ' hasnt ': ' hasn\'t ',
            ' hadnt ': ' hadn\'t ',
            ' wont ': ' won\'t ',
            ' wouldnt ': ' wouldn\'t ',
            ' couldnt ': ' couldn\'t ',
            ' shouldnt ': ' shouldn\'t ',
            ' cant ': ' can\'t ',
            ' lets ': ' let\'s ',
            ' thats ': ' that\'s ',
            ' its ': ' it\'s ',
            ' hes ': ' he\'s ',
            ' shes ': ' she\'s ',
            ' youre ': ' you\'re ',
            ' theyre ': ' they\'re ',
            ' were ': ' we\'re ',
            ' whos ': ' who\'s ',
            ' whats ': ' what\'s ',
            ' wheres ': ' where\'s ',
            ' whens ': ' when\'s ',
            ' whys ': ' why\'s ',
            ' hows ': ' how\'s '
        }
        
        for old, new in replacements.items():
            paragraph = paragraph.replace(old, new)
        
        cleaned_paragraphs.append(paragraph.strip())
    
    # 段落を改行で結合
    return '\n\n'.join(cleaned_paragraphs)

def extract_text_from_pdf(pdf_path, output_path=None, page_number=None, start_page=None, end_page=None):
    """
    PDFファイルからテキストを抽出する
    
    Args:
        pdf_path (str): PDFファイルのパス
        output_path (str, optional): 出力ファイルのパス。指定しない場合は出力しない
        page_number (int, optional): 抽出するページ番号（0から始まる）。指定しない場合は全ページ
        start_page (int, optional): 抽出開始ページ（0から始まる）
        end_page (int, optional): 抽出終了ページ（0から始まる）
        
    Returns:
        str: 抽出されたテキスト
    """
    try:
        # PDFファイルを開く
        reader = PdfReader(pdf_path)
        
        # ページ範囲の検証
        if start_page is not None and end_page is not None:
            if start_page < 0 or end_page >= len(reader.pages) or start_page > end_page:
                raise ValueError(f"ページ範囲 {start_page}-{end_page} は無効です。有効な範囲: 0-{len(reader.pages)-1}")
        
        # テキストを抽出
        text = ""
        if page_number is not None:
            # 特定のページのみ抽出
            text = reader.pages[page_number].extract_text() + "\n"
        elif start_page is not None and end_page is not None:
            # 指定された範囲のページを抽出
            for i in range(start_page, end_page + 1):
                text += reader.pages[i].extract_text() + "\n"
        else:
            # 全ページを抽出
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        # テキストを整形
        text = clean_text(text)
            
        # テキストをファイルに保存
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"テキストを {output_path} に保存しました。")
            
        return text
    
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return None

def extract_text_from_directory(directory_path, output_dir=None, page_number=None):
    """
    指定されたディレクトリ内の全てのPDFファイルからテキストを抽出する
    
    Args:
        directory_path (str): PDFファイルが格納されているディレクトリのパス
        output_dir (str, optional): 出力ディレクトリのパス。指定しない場合は出力しない
        page_number (int, optional): 抽出するページ番号（0から始まる）。指定しない場合は全ページ
        
    Returns:
        dict: {ファイル名: 抽出されたテキスト} の辞書
    """
    results = {}
    
    # 出力ディレクトリが指定されている場合は作成
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # ディレクトリ内の全てのファイルを走査
    for filename in os.listdir(directory_path):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(directory_path, filename)
            text = extract_text_from_pdf(file_path, page_number=page_number)
            if text:
                results[filename] = text
                
                # 出力ディレクトリが指定されている場合は保存
                if output_dir:
                    output_filename = os.path.splitext(filename)[0] + '.txt'
                    output_path = os.path.join(output_dir, output_filename)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                    print(f"テキストを {output_path} に保存しました。")
                
    return results

def extract_images_from_pdf(pdf_path, output_dir=None, page_number=None):
    """
    PDFファイルから画像を抽出する
    
    Args:
        pdf_path (str): PDFファイルのパス
        output_dir (str, optional): 出力ディレクトリのパス。指定しない場合は出力しない
        page_number (int, optional): 抽出するページ番号（0から始まる）。指定しない場合は全ページ
        
    Returns:
        dict: {ページ番号: 画像リスト} の辞書
    """
    try:
        print(f"PDFファイルを開いています: {pdf_path}")
        # PDFファイルを開く
        doc = fitz.open(pdf_path)
        all_images = {}
        
        # 出力ディレクトリが指定されている場合は作成
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"出力ディレクトリを作成しました: {output_dir}")
        
        # 処理するページの範囲を決定
        if page_number is not None:
            pages_to_process = [page_number]
        else:
            pages_to_process = range(len(doc))
        
        # 各ページを処理
        for page_num in pages_to_process:
            print(f"ページ {page_num + 1} を処理しています...")
            page = doc[page_num]
            images = []
            
            # ページ全体を高解像度で画像として取得
            print("ページを画像として取得しています...")
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2倍の解像度
            page_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # 画像の位置情報を取得
            print("画像の位置情報を取得しています...")
            image_list = page.get_images(full=True)
            print(f"見つかった画像の数: {len(image_list)}")
            
            # 各画像を処理
            for img_index, img in enumerate(image_list):
                try:
                    print(f"画像 {img_index + 1} を処理しています...")
                    
                    # 画像の位置情報を取得
                    xref = img[0]
                    print(f"画像 {img_index + 1} のxref: {xref}")
                    
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
                    
                    # 画像を保存
                    if output_dir:
                        output_path = os.path.join(output_dir, f"page_{page_num + 1}_image_{img_index + 1}.png")
                        image.save(output_path, "PNG", quality=95)
                        print(f"画像を {output_path} に保存しました。")
                    
                    images.append(image)
                except Exception as e:
                    print(f"画像 {img_index + 1} の処理中にエラーが発生しました:")
                    print(f"エラーの種類: {type(e).__name__}")
                    print(f"エラーメッセージ: {str(e)}")
                    import traceback
                    print("詳細なエラー情報:")
                    print(traceback.format_exc())
                    continue
            
            all_images[page_num] = images
        
        doc.close()
        return all_images
    
    except Exception as e:
        print(f"エラーが発生しました:")
        print(f"エラーの種類: {type(e).__name__}")
        print(f"エラーメッセージ: {str(e)}")
        import traceback
        print("詳細なエラー情報:")
        print(traceback.format_exc())
        return None

def text_to_speech(text, output_path, lang='en'):
    """
    テキストを音声ファイルに変換する
    
    Args:
        text (str): 変換するテキスト
        output_path (str): 出力ファイルのパス
        lang (str): 言語コード（デフォルト: 'en'）
    """
    try:
        # gTTSオブジェクトを作成
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # 音声ファイルを保存
        tts.save(output_path)
        print(f"音声ファイルを {output_path} に保存しました。")
        
    except Exception as e:
        print(f"エラーが発生しました:")
        print(f"エラーの種類: {type(e).__name__}")
        print(f"エラーメッセージ: {str(e)}")
        import traceback
        print("詳細なエラー情報:")
        print(traceback.format_exc())

if __name__ == "__main__":
    # 使用例
    pdf_path = "../../Downloads/eiken/2024-3-1ji-4kyu.pdf"  # PDFファイルのパスを指定
    output_path = "output.txt"  # 出力ファイルのパスを指定
    
    # テキストを抽出
    text = extract_text_from_pdf(pdf_path, output_path)
    if text:
        print(f"テキストを {output_path} に保存しました。")
        print(f"抽出されたテキストの長さ: {len(text)} 文字")
        
        # テキストを音声に変換
        audio_output_path = "output.mp3"
        text_to_speech(text, audio_output_path)
    
    # 画像抽出の使用例（コメントアウト）
    """
    # 画像を含むPDFの場合
    output_dir = "extracted_images"  # 出力ディレクトリのパスを指定
    images = extract_images_from_pdf(pdf_path, output_dir)
    if images:
        total_images = sum(len(imgs) for imgs in images.values())
        print(f"合計 {total_images} 個の画像を抽出しました。")
        for page_num, page_images in images.items():
            print(f"ページ {page_num + 1} から {len(page_images)} 個の画像を抽出しました。")
    """ 