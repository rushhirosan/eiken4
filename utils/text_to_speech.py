#!/usr/bin/env python3
"""
リスニング第1部（イラスト問題）の音声生成エントリポイント。

会話は M/W で話者分けし、セリフ間に無音を挟む（第2・第3部と同じ Edge TTS パイプライン）。
会話 → 質問 → 選択肢の順で結合（選択肢は extract の join 済み文字列をそのまま TTS）。
「Question No.xx」は読まず Question のみ。
"""
import asyncio
import os

from text_to_speech_conversation import generate_illustration_audio_from_file


def generate_illustration_audio(input_file, output_dir, question_range=None):
    """同期ラッパー（既存呼び出し互換）。"""
    asyncio.run(
        generate_illustration_audio_from_file(
            input_file, output_dir, question_range
        )
    )


def main():
    input_file = 'data/questions/listening_illustration_questions.txt'
    output_dir = 'static/audio/part1'
    question_range = None

    if not os.path.exists(input_file):
        raise SystemExit(f'入力ファイルが見つかりません: {input_file}')

    generate_illustration_audio(input_file, output_dir, question_range)


if __name__ == '__main__':
    main()
