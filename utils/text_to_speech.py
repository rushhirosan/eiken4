import edge_tts
import asyncio
import os
import re
from pydub import AudioSegment

def extract_passage_and_question(text):
    """文章と問題を抽出"""
    lines = text.strip().split('\n')
    passage = []
    question = []
    is_question = False
    skip_until_next_question = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # No.X: をスキップ
        if re.match(r'No\.\d+:', line):
            skip_until_next_question = False
            continue
            
        # 正解と解説が始まったら、次の問題までスキップ
        if line.startswith('【正解') or line.startswith('【解説'):
            skip_until_next_question = True
            continue
            
        if skip_until_next_question:
            continue
            
        # Question No.X: の場合
        if line.startswith('Question No.'):
            is_question = True
            # Question のみを追加
            question.append("Question")
            continue
            
        # 選択肢をスキップ
        if re.match(r'^\d+\.', line):
            continue
            
        # M: と W: を除去
        if line.startswith('M:') or line.startswith('W:'):
            line = line[2:].strip()
            
        if is_question:
            question.append(line)
        else:
            passage.append(line)
    
    return '\n'.join(passage), '\n'.join(question)

def combine_audio_files(passage_audio, question_audio, output_path):
    """音声ファイルを結合"""
    # 音声ファイルを読み込み
    passage = AudioSegment.from_mp3(passage_audio)
    question = AudioSegment.from_mp3(question_audio)
    
    # 1秒の無音を作成
    silence = AudioSegment.silent(duration=1000)
    
    # 音声を結合（文章 → 1秒の無音 → Question → 1秒の無音 → 問題文）
    combined = passage + silence + question
    
    # 結合した音声を保存
    combined.export(output_path, format="mp3")
    
    # 一時ファイルを削除
    os.remove(passage_audio)
    os.remove(question_audio)

async def text_to_speech(text, output_path, voice):
    """テキストを音声ファイルに変換する"""
    try:
        # 出力ディレクトリが存在しない場合は作成
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 音声を生成
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        print(f"音声ファイルを {output_path} に保存しました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

async def main():
    # 入力ファイルのパス
    input_file = 'questions/listening_passage_questions.txt'
    
    # 出力ディレクトリ
    output_dir = 'static/audio/part3'
    os.makedirs(output_dir, exist_ok=True)
    
    # ファイルを読み込み
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 問題ブロックを分割
    question_blocks = content.split('---')
    
    for block in question_blocks:
        if not block.strip():
            continue
            
        # 問題番号を抽出
        number_match = re.search(r'No\.(\d+):', block)
        if not number_match:
            continue
            
        question_number = number_match.group(1)
        
        # 文章と問題を抽出
        passage, question = extract_passage_and_question(block)
        
        # 音声ファイルのパス
        passage_audio = os.path.join(output_dir, f'temp_passage_{question_number}.mp3')
        question_audio = os.path.join(output_dir, f'temp_question_{question_number}.mp3')
        output_audio = os.path.join(output_dir, f'listening_passage_question{question_number}.mp3')
        
        # 文章の音声を生成（男性の声）
        await text_to_speech(passage, passage_audio, "en-US-GuyNeural")
        
        # 問題の音声を生成（女性の声）
        await text_to_speech(question, question_audio, "en-US-JennyNeural")
            
            # 音声ファイルを結合
        combine_audio_files(passage_audio, question_audio, output_audio)
                
        print(f"Processed question {question_number}")

if __name__ == "__main__":
    asyncio.run(main()) 