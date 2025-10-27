#!/usr/bin/env python3
import os
import re
from gtts import gTTS

def extract_illustration_parts(text):
    """リスニングイラスト問題の会話文、質問文、選択肢を抽出"""
    lines = text.strip().split('\n')
    conversation = []
    question = []
    choices = []
    is_question = False
    is_choices = False
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
            is_choices = False
            question.append("Question")
            continue
            
        # 選択肢の開始（数字で始まる行）
        if re.match(r'^\d+\.', line):
            is_question = False
            is_choices = True
            choices.append(line)
            continue
            
        # 会話文（M: と W: を順番通りに処理）
        if line.startswith('M:') or line.startswith('W:'):
            text = line[2:].strip()
            conversation.append(text)
        elif is_question:
            question.append(line)
    
    return ' '.join(conversation), ' '.join(question), choices

def create_audio_file(conversation, question, choices, output_path):
    """音声ファイルを作成"""
    try:
        # 完全なテキストを作成
        full_text = f"{conversation} {question} {' '.join(choices)}"
        
        # 音声ファイルを作成
        tts = gTTS(text=full_text, lang='en', slow=False)
        tts.save(output_path)
        print(f"音声ファイルを作成しました: {output_path}")
        return True
        
    except Exception as e:
        print(f"音声ファイル作成中にエラーが発生しました: {str(e)}")
        return False

def generate_illustration_audio(input_file, output_dir, question_range=None):
    """
    リスニングイラスト問題の音声ファイルを生成
    
    Args:
        input_file (str): 入力テキストファイルのパス
        output_dir (str): 出力ディレクトリのパス
        question_range (tuple, optional): 問題範囲 (start, end) 例: (31, 40)
    """
    # 出力ディレクトリを作成
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"ディレクトリを作成しました: {output_dir}")
    
    # ファイルを読み込み
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 問題ブロックを分割
    question_blocks = content.split('---')
    
    success_count = 0
    total_count = 0
    
    for block in question_blocks:
        if not block.strip():
            continue
            
        # 問題番号を抽出
        number_match = re.search(r'No\.(\d+):', block)
        if not number_match:
            continue
            
        question_number = int(number_match.group(1))
        
        # 問題範囲の指定がある場合はチェック
        if question_range:
            start_num, end_num = question_range
            if question_number < start_num or question_number > end_num:
                continue
        
        total_count += 1
        
        # 会話、質問、選択肢を抽出
        conversation, question, choices = extract_illustration_parts(block)
        
        # 音声ファイルを作成
        output_file = os.path.join(output_dir, f"listening_illustration_question{question_number}.mp3")
        
        if create_audio_file(conversation, question, choices, output_file):
            success_count += 1
            print(f"問題{question_number}を処理しました")
    
    print(f"\n音声ファイル作成完了！")
    print(f"成功: {success_count}/{total_count} 問")

def main():
    """メイン関数"""
    # 設定
    input_file = 'data/questions/listening_illustration_questions.txt'
    output_dir = 'static/audio/part1'
    
    # 問題範囲を指定（Noneの場合は全問題）
    # question_range = (31, 40)  # 31-40問のみ
    question_range = None  # 全問題
    
    # 音声ファイルを生成
    generate_illustration_audio(input_file, output_dir, question_range)

if __name__ == "__main__":
    main()