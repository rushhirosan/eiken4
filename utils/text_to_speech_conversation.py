#!/usr/bin/env python3
import os
import re
import sys
import asyncio
from typing import Optional, Tuple
import edge_tts
from pydub import AudioSegment

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

def extract_conversation_parts(text):
    """
    会話文を順番通りに抽出（MとWを区別）。

    Returns:
        tuple: (conversation_parts, question_str, choices_lines)
        choices_lines は選択肢行の list。「join 済み str」ではない（誤って再 join しないこと）。
    """
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
    
    return conversation_parts, '\n'.join(question), choices


def extract_illustration_correct_answer(block: str) -> Tuple[Optional[str], Optional[str]]:
    """
    イラスト問題ブロックから正解応答文と話者を取得する。

    話者は会話3行の最後の話者と逆（★=M, ☆=W）とする（英検第1部の慣例）。
    """
    conversation_parts, _, choices_lines = extract_conversation_parts(block)
    if not conversation_parts or not choices_lines:
        return None, None

    ans_match = re.search(r'【正解\d+】\s*\n\s*(\d+)\.', block)
    if not ans_match:
        return None, None

    order = int(ans_match.group(1))
    response_text = None
    for line in choices_lines:
        m = re.match(r'^(\d+)\.\s+(.+)$', line.strip())
        if m and int(m.group(1)) == order:
            response_text = m.group(2).strip()
            break
    if not response_text:
        return None, None

    last_speaker = conversation_parts[-1][0]
    response_speaker = 'W' if last_speaker == 'M' else 'M'
    return response_text, response_speaker


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
        if isinstance(text, (list, tuple)):
            text = '\n'.join(str(x) for x in text)
        else:
            text = str(text)

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

async def generate_audio_from_file(
    input_file,
    output_dir,
    question_range=None,
    output_prefix='listening_passage_question',
):
    """
    ファイルから音声を生成する
    
    Args:
        input_file (str): 入力テキストのパス
        output_dir (str): 出力ディレクトリ
        question_range (tuple, optional): 問題範囲 (start, end)。None で全問
        output_prefix (str): ファイル名プレフィックス（例: listening_conversation_question）
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
        conversation_parts, question, _choices_lines = extract_conversation_parts(
            block
        )
        
        output_audio = os.path.join(
            output_dir, f'{output_prefix}{question_number}.mp3'
        )
        
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


async def generate_illustration_audio_from_file(
    input_file,
    output_dir,
    question_range=None,
):
    """
    リスニング第1部（イラスト問題）の音声を生成する。

    会話は M/W で話者別（Edge TTS）、セリフ間に短い無音。
    「Question No.xx」は読まず Question のみ。続けて選択肢1〜3を読み上げる。
    """
    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    question_blocks = content.split('---')

    for block in question_blocks:
        if not block.strip():
            continue

        number_match = re.search(r'No\.(\d+):', block)
        if not number_match:
            continue

        question_number = int(number_match.group(1))

        if question_range:
            start_num, end_num = question_range
            if question_number < start_num or question_number > end_num:
                continue

        conversation_parts, question, choices_lines = extract_conversation_parts(
            block
        )

        output_audio = os.path.join(
            output_dir, f'listening_illustration_question{question_number}.mp3'
        )
        conversation_audio = os.path.join(
            output_dir, f'temp_conversation_{question_number}.mp3'
        )

        audio_segments = []
        silence = AudioSegment.silent(duration=500)

        for speaker, text in conversation_parts:
            temp_audio = os.path.join(
                output_dir, f'temp_{speaker}_{question_number}.mp3'
            )
            voice = "en-US-GuyNeural" if speaker == 'M' else "en-US-JennyNeural"
            print(f"Illustration {question_number} - {speaker}: {text}")
            await text_to_speech(text, temp_audio, voice)

            if os.path.exists(temp_audio):
                audio_segments.append(AudioSegment.from_mp3(temp_audio))
                audio_segments.append(silence)
                os.remove(temp_audio)

        if audio_segments:
            combined_conversation = sum(audio_segments)
            combined_conversation.export(conversation_audio, format="mp3")

        question_audio = os.path.join(
            output_dir, f'temp_question_{question_number}.mp3'
        )
        print(f"Illustration {question_number} - Question text: {question}")
        await text_to_speech(question, question_audio, "en-US-GuyNeural")

        ct = '\n'.join(choices_lines).strip()
        if ct:
            choices_audio = os.path.join(
                output_dir, f'temp_choices_{question_number}.mp3'
            )
            print(f"Illustration {question_number} - Choices:\n{ct}")
            await text_to_speech(ct, choices_audio, "en-US-GuyNeural")
            combine_audio_files_with_choices(
                conversation_audio, question_audio, choices_audio, output_audio
            )
        else:
            combine_audio_files(conversation_audio, question_audio, output_audio)

        print(f"Illustration question {question_number} done -> {output_audio}")


async def main_async(args):
    """第2部・第3部を全問再生成（Question No. は読み上げテキストから除外済み）。"""
    from utils.eiken_paths import questions_txt, static_audio_part

    lev = args.level
    conv_txt = args.conversation_txt or questions_txt(lev, 'listening_conversation_questions.txt')
    pass_txt = args.passage_txt or questions_txt(lev, 'listening_passage_questions.txt')
    part2_dir = args.part2_dir or static_audio_part(lev, 'part2')
    part3_dir = args.part3_dir or static_audio_part(lev, 'part3')

    for path in (conv_txt, pass_txt):
        if not os.path.exists(path):
            raise SystemExit(f'入力ファイルが見つかりません: {path}')

    await generate_audio_from_file(
        conv_txt,
        part2_dir,
        question_range=None,
        output_prefix='listening_conversation_question',
    )
    print('--- 第2部 完了 ---')
    await generate_audio_from_file(
        pass_txt,
        part3_dir,
        question_range=None,
        output_prefix='listening_passage_question',
    )
    print('--- 第3部 完了 ---')
    print('音声生成が完了しました。')


def main():
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description='リスニング第2・第3部の音声生成（既定は 4級パス）'
    )
    parser.add_argument(
        '--level',
        default=os.environ.get('EIKEN_LEVEL', '4'),
        choices=['3', '4'],
        help='3 のとき level3 配下のテキスト・音声ディレクトリを既定にする',
    )
    parser.add_argument('--conversation-txt', default=None, help='第2部の入力テキスト')
    parser.add_argument('--passage-txt', default=None, help='第3部の入力テキスト')
    parser.add_argument('--part2-dir', default=None, help='第2部 MP3 の出力ディレクトリ')
    parser.add_argument('--part3-dir', default=None, help='第3部 MP3 の出力ディレクトリ')
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main() 