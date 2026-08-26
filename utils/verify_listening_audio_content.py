#!/usr/bin/env python3
"""オリジナル txt から再生成した音声と既存 MP3 の長さを比較し、番号ずれを検出する。"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from pydub import AudioSegment
from text_to_speech_conversation import (
    generate_audio_from_file,
    generate_illustration_audio_from_file,
)
from utils.eiken_paths import default_tts_rate, static_audio_part


def _dur_ms(path: Path) -> int:
    return len(AudioSegment.from_mp3(path))


async def _check_illustration(level: str, n: int, txt: Path, tol: float) -> str | None:
    out = static_audio_part(level, 'part1')
    existing = Path(out) / f'listening_illustration_question{n}.mp3'
    if not existing.exists():
        return f'level{level} ill #{n}: missing {existing.name}'
    with tempfile.TemporaryDirectory() as td:
        await generate_illustration_audio_from_file(
            str(txt), td, (n, n), rate=default_tts_rate(level)
        )
        fresh = Path(td) / f'listening_illustration_question{n}.mp3'
        if not fresh.exists():
            return f'level{level} ill #{n}: regen failed'
        e, f = _dur_ms(existing), _dur_ms(fresh)
        if f == 0 or abs(e - f) / f > tol:
            return f'level{level} ill #{n}: duration mismatch existing={e}ms regen={f}ms'
    return None


async def _check_exam(
    level: str, n: int, txt: Path, part: str, prefix: str, tol: float
) -> str | None:
    out = static_audio_part(level, part)
    existing = Path(out) / f'{prefix}{n}.mp3'
    if not existing.exists():
        return f'level{level} {prefix} #{n}: missing'
    with tempfile.TemporaryDirectory() as td:
        await generate_audio_from_file(
            str(txt),
            td,
            question_range=(n, n),
            output_prefix=prefix,
            rate=default_tts_rate(level),
        )
        fresh = Path(td) / f'{prefix}{n}.mp3'
        if not fresh.exists():
            return f'level{level} {prefix} #{n}: regen failed'
        e, f = _dur_ms(existing), _dur_ms(fresh)
        if f == 0 or abs(e - f) / f > tol:
            return f'level{level} {prefix} #{n}: duration mismatch existing={e}ms regen={f}ms'
    return None


async def run(levels: list[str], start: int, end: int, tol: float) -> list[str]:
    errors: list[str] = []
    for level in levels:
        base = _REPO / 'data' / 'questions' / 'original' / f'level{level}'
        ill = base / 'listening_illustration_questions.txt'
        conv = base / 'listening_conversation_questions.txt'
        pas = base / 'listening_passage_questions.txt'
        for n in range(start, end + 1):
            for coro in (
                _check_illustration(level, n, ill, tol),
                _check_exam(level, n, conv, 'part2', 'listening_conversation_question', tol),
                _check_exam(level, n, pas, 'part3', 'listening_passage_question', tol),
            ):
                err = await coro
                if err:
                    errors.append(err)
                else:
                    print(f'OK level{level} #{n} ({coro.cr_code.co_name if hasattr(coro, "cr_code") else "part"})')
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--level', action='append', default=None)
    parser.add_argument('--start', type=int, default=11)
    parser.add_argument('--end', type=int, default=20)
    parser.add_argument('--tolerance', type=float, default=0.12, help='duration diff ratio')
    args = parser.parse_args()
    levels = args.level or ['3', '4']
    errors: list[str] = []
    for level in levels:
        base = _REPO / 'data' / 'questions' / 'original' / f'level{level}'
        for n in range(args.start, args.end + 1):
            for label, coro in [
                ('ill', _check_illustration(level, n, base / 'listening_illustration_questions.txt', args.tolerance)),
                ('conv', _check_exam(level, n, base / 'listening_conversation_questions.txt', 'part2', 'listening_conversation_question', args.tolerance)),
                ('pass', _check_exam(level, n, base / 'listening_passage_questions.txt', 'part3', 'listening_passage_question', args.tolerance)),
            ]:
                err = asyncio.run(coro)
                if err:
                    errors.append(err)
                else:
                    print(f'OK level{level} {label} #{n}')
    if errors:
        print('FAIL', len(errors))
        for e in errors:
            print(' -', e)
        raise SystemExit(1)
    print(f'Audio fingerprint OK: levels {levels} #{args.start}-#{args.end}')


if __name__ == '__main__':
    main()
