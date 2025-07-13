#!/usr/bin/env python3
import os
import re
import asyncio
import edge_tts
from pydub import AudioSegment

def extract_conversation_parts(text):
    """会話文を順番通りに抽出（MとWを区別）"""
    lines = text.strip().split('\n')
    conversation_parts = []
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
            # Question のみを追加
            question.append("Question")
            continue
            
        # 選択肢の開始（数字で始まる行）
        if re.match(r'^\d+\.', line):
            is_question = False
            is_choices = True
            choices.append(line)
            continue
            
        # M: と W: を順番通りに処理（話者情報付き）
        if line.startswith('M:') or line.startswith('W:'):
            speaker = 'M' if line.startswith('M:') else 'W'
            text = line[2:].strip()
            conversation_parts.append((speaker, text))
        # ☆ と ★ を順番通りに処理（リスニングイラスト問題用）
        elif line.startswith('☆') or line.startswith('★'):
            speaker = 'W' if line.startswith('☆') else 'M'  # ☆を女性、★を男性として扱う
            text = line[1:].strip()
            conversation_parts.append((speaker, text))
        elif is_question:
            question.append(line)
        elif is_choices:
            choices.append(line)
    
    return conversation_parts, '\n'.join(question), '\n'.join(choices)

def combine_audio_files(conversation_audio, question_audio, output_path):
    """音声ファイルを結合"""
    # 音声ファイルを読み込み
    audio_segments = []
    
    # 1秒の無音を作成
    silence = AudioSegment.silent(duration=1000)
    
    # 会話の音声を追加
    if os.path.exists(conversation_audio):
        conversation_audio_segment = AudioSegment.from_mp3(conversation_audio)
        audio_segments.append(conversation_audio_segment)
        audio_segments.append(silence)
    
    # 問題の音声を追加
    if os.path.exists(question_audio):
        question_audio_segment = AudioSegment.from_mp3(question_audio)
        audio_segments.append(question_audio_segment)
    
    # 音声を結合
    if audio_segments:
        combined_audio = sum(audio_segments)
        combined_audio.export(output_path, format="mp3")
    
    # 一時ファイルを削除
    if os.path.exists(conversation_audio):
        os.remove(conversation_audio)
    if os.path.exists(question_audio):
        os.remove(question_audio)

def combine_audio_files_with_choices(conversation_audio, question_audio, choices_audio, output_path):
    """音声ファイルを結合（選択肢付き）"""
    # 音声ファイルを読み込み
    audio_segments = []
    
    # 1秒の無音を作成
    silence = AudioSegment.silent(duration=1000)
    
    # 会話の音声を追加
    if os.path.exists(conversation_audio):
        conversation_audio_segment = AudioSegment.from_mp3(conversation_audio)
        audio_segments.append(conversation_audio_segment)
        audio_segments.append(silence)
    
    # 問題の音声を追加
    if os.path.exists(question_audio):
        question_audio_segment = AudioSegment.from_mp3(question_audio)
        audio_segments.append(question_audio_segment)
        audio_segments.append(silence)
    
    # 選択肢の音声を追加
    if os.path.exists(choices_audio):
        choices_audio_segment = AudioSegment.from_mp3(choices_audio)
        audio_segments.append(choices_audio_segment)
    
    # 音声を結合
    if audio_segments:
        combined_audio = sum(audio_segments)
        combined_audio.export(output_path, format="mp3")
    
    # 一時ファイルを削除
    if os.path.exists(conversation_audio):
        os.remove(conversation_audio)
    if os.path.exists(question_audio):
        os.remove(question_audio)
    if os.path.exists(choices_audio):
        os.remove(choices_audio)

async def text_to_speech(text, output_path, voice="en-US-GuyNeural"):
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

async def generate_audio_from_file(input_file, output_dir, question_range=None):
    """
    ファイルから音声を生成する
    
    Args:
        input_file (str): 入力ファイルのパス
        output_dir (str): 出力ディレクトリのパス
        question_range (tuple, optional): 問題範囲 (start, end)
    """
    # 出力ディレクトリを作成
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
            
        question_number = int(number_match.group(1))
        
        # 問題範囲が指定されている場合はチェック
        if question_range:
            start_num, end_num = question_range
            if question_number < start_num or question_number > end_num:
                continue
        
        # 会話と問題と選択肢を抽出
        conversation_parts, question, choices = extract_conversation_parts(block)
        
        # 音声ファイル名（passageに変更）
        output_audio = os.path.join(output_dir, f'listening_passage_question{question_number}.mp3')
        
        # 会話の音声ファイルを作成（順番通り、話者別）
        conversation_audio = os.path.join(output_dir, f'temp_conversation_{question_number}.mp3')
        
        # 話者別に音声を生成して結合
        audio_segments = []
        silence = AudioSegment.silent(duration=500)  # 0.5秒の無音
        
        for speaker, text in conversation_parts:
            temp_audio = os.path.join(output_dir, f'temp_{speaker}_{question_number}.mp3')
            voice = "en-US-GuyNeural" if speaker == 'M' else "en-US-JennyNeural"
            print(f"Question {question_number} - {speaker}: {text}")
            await text_to_speech(text, temp_audio, voice)
            
            if os.path.exists(temp_audio):
                audio_segment = AudioSegment.from_mp3(temp_audio)
                audio_segments.append(audio_segment)
                audio_segments.append(silence)
                os.remove(temp_audio)
        
        # 会話音声を結合
        if audio_segments:
            combined_conversation = sum(audio_segments)
            combined_conversation.export(conversation_audio, format="mp3")
        
        # 問題の音声ファイルを作成
        question_audio = os.path.join(output_dir, f'temp_question_{question_number}.mp3')
        print(f"Question {question_number} - Question text: {question}")
        await text_to_speech(question, question_audio, "en-US-GuyNeural")
        
        # 音声ファイルを結合（会話 + 問題のみ）
        combine_audio_files(conversation_audio, question_audio, output_audio)
                
        print(f"Processed question {question_number}")

async def main():
    # 設定
    input_file = 'questions/listening_passage_questions.txt'
    output_dir = 'static/audio/part3'
    question_range = (31, 40)  # 31問目から40問目
    
    # 音声を生成
    await generate_audio_from_file(input_file, output_dir, question_range)
    print("音声生成が完了しました。")

if __name__ == "__main__":
    asyncio.run(main()) 