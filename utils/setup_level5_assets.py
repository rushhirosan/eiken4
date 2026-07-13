#!/usr/bin/env python3
"""英検5級リスニング用のプレースホルダー画像と TTS 音声を生成する。"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_REPO = Path(__file__).resolve().parents[1]
_IMG_DIR = _REPO / 'static' / 'images' / 'level5' / 'part1'
_AUDIO_PART1 = _REPO / 'static' / 'audio' / 'level5' / 'part1'
_AUDIO_PART2 = _REPO / 'static' / 'audio' / 'level5' / 'part2'
_AUDIO_PART3 = _REPO / 'static' / 'audio' / 'level5' / 'part3'
# 第1部（会話応答）= No.1–100、第3部（イラスト一致）= No.101+
_PART1_MAX = 40
_PART3_MIN = 101
_PART3_MAX = 140


def _draw_placeholder(draw: ImageDraw.ImageDraw, label: str) -> None:
    draw.rectangle([10, 10, 310, 230], outline=(120, 120, 160), width=2)
    draw.text((20, 100), label, fill=(60, 60, 90))


def create_placeholder_images() -> None:
    _IMG_DIR.mkdir(parents=True, exist_ok=True)
    numbers = list(range(1, _PART1_MAX + 1)) + list(range(_PART3_MIN, _PART3_MAX + 1))
    for i in numbers:
        path = _IMG_DIR / f'listening_illustration_image{i}.png'
        if path.exists():
            continue
        img = Image.new('RGB', (320, 240), color=(245, 245, 250))
        draw = ImageDraw.Draw(img)
        _draw_placeholder(draw, f'5級 L-{i}')
        img.save(path, 'PNG')


def create_part3_choice_images() -> None:
    """Part3（No.101+）の3肢イラスト用プレースホルダー。"""
    _IMG_DIR.mkdir(parents=True, exist_ok=True)
    for q in range(_PART3_MIN, _PART3_MAX + 1):
        for c in range(1, 4):
            path = _IMG_DIR / f'listening_illustration_q{q}_choice{c}.png'
            if path.exists():
                continue
            img = Image.new('RGB', (200, 160), color=(250, 248, 245))
            draw = ImageDraw.Draw(img)
            _draw_placeholder(draw, f'Q{q}-{c}')
            img.save(path, 'PNG')


def create_placeholder_audio() -> None:
    """TTS が使えない環境向けに短い無音 MP3 を生成する。"""
    import shutil
    import subprocess

    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        print('ffmpeg not found; skipping audio generation')
        return

    for out_dir, start, end, prefix in (
        (_AUDIO_PART1, 1, _PART1_MAX, 'listening_illustration_question'),
        (_AUDIO_PART3, _PART3_MIN, _PART3_MAX, 'listening_illustration_question'),
        (_AUDIO_PART2, 1, 15, 'listening_conversation_question'),
    ):
        out_dir.mkdir(parents=True, exist_ok=True)
        for i in range(start, end + 1):
            path = out_dir / f'{prefix}{i}.mp3'
            if path.exists():
                continue
            subprocess.run(
                [
                    ffmpeg, '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                    '-t', '1', '-q:a', '9', '-acodec', 'libmp3lame', str(path),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


def run_tts() -> None:
    try:
        py = sys.executable
        tts = str(_REPO / 'utils' / 'text_to_speech.py')
        subprocess.run(
            [py, tts, '--level', '5', '--question-range', '1', str(_PART1_MAX)],
            check=True,
        )
        subprocess.run(
            [py, tts, '--level', '5', '--output-dir', str(_AUDIO_PART3),
             '--question-range', str(_PART3_MIN), str(_PART3_MAX)],
            check=True,
        )
        subprocess.run(
            [py, str(_REPO / 'utils' / 'text_to_speech_conversation.py'), '--level', '5'],
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, ModuleNotFoundError) as exc:
        print(f'TTS skipped ({exc}); using placeholder audio.')
        create_placeholder_audio()


def main() -> int:
    create_placeholder_images()
    create_part3_choice_images()
    run_tts()
    if not any(_AUDIO_PART1.glob('*.mp3')) and not any(_AUDIO_PART3.glob('*.mp3')):
        create_placeholder_audio()
    print('Level 5 assets ready.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
