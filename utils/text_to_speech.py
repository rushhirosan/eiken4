#!/usr/bin/env python3
"""
リスニング第1部（イラスト問題）の音声生成エントリポイント。

会話は M/W で話者分けし、セリフ間に無音を挟む（第2・第3部と同じ Edge TTS パイプライン）。
会話 → 「Question」→ 選択肢1〜3 の順で結合（「Question No.xx」は読まない）。
"""
import argparse
import asyncio
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from text_to_speech_conversation import generate_illustration_audio_from_file

from utils.eiken_paths import questions_txt, static_audio_part


def generate_illustration_audio(input_file, output_dir, question_range=None, rate="+0%"):
    """同期ラッパー（既存呼び出し互換）。"""
    asyncio.run(
        generate_illustration_audio_from_file(
            input_file, output_dir, question_range, rate=rate
        )
    )


def main():
    parser = argparse.ArgumentParser(
        description='リスニング第1部（イラスト）の MP3 生成'
    )
    parser.add_argument(
        '--level',
        default=os.environ.get('EIKEN_LEVEL', '4'),
        choices=['3', '4', '5'],
        help='3 のとき data/questions/level3/ と static/audio/level3/part1 を既定にする',
    )
    parser.add_argument(
        '--input', '-i',
        default=None,
        help='listening_illustration_questions.txt（未指定時は級に応じた既定パス）',
    )
    parser.add_argument(
        '--output-dir', '-o',
        default=None,
        help='出力先ディレクトリ（未指定時は級に応じた part1）',
    )
    parser.add_argument(
        '--question-range',
        nargs=2,
        type=int,
        metavar=('START', 'END'),
        default=None,
        help='問題番号の範囲（オプション）',
    )
    parser.add_argument(
        '--rate',
        default='+0%',
        help='Edge TTS の話速（例: "-10%%" で少しゆっくり、既定は "+0%%"）',
    )
    args = parser.parse_args()

    lev = args.level
    input_file = args.input or questions_txt(lev, 'listening_illustration_questions.txt')
    output_dir = args.output_dir or static_audio_part(lev, 'part1')
    question_range = None
    if args.question_range:
        question_range = tuple(args.question_range)

    if not os.path.exists(input_file):
        raise SystemExit(f'入力ファイルが見つかりません: {input_file}')

    generate_illustration_audio(input_file, output_dir, question_range, rate=args.rate)


if __name__ == '__main__':
    main()
