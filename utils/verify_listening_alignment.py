#!/usr/bin/env python3
"""リスニングの番号・パス・テキストブロック整合を検証する（音声内容の ASR は行わない）。"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eiken_project.settings')

import django

django.setup()

from exams.models import Question
from questions.level_paths import db_audio_path, db_image_path_part1, questions_file_abspath
from questions.models import ListeningQuestion

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None


def _blocks(path: Path) -> dict[int, str]:
    content = path.read_text(encoding='utf-8')
    out: dict[int, str] = {}
    for block in content.split('---'):
        if not block.strip():
            continue
        m = re.search(r'No\.(\d+):', block)
        if m:
            out[int(m.group(1))] = block.strip()
    return out


def _first_dialogue_line(block: str) -> str:
    for line in block.splitlines():
        s = line.strip()
        if s.startswith(('M:', 'W:', '☆', '★')):
            return s[:80]
    return ''


def _question_line(block: str) -> str:
    m = re.search(r'Question No\.\d+:\s*(.*)', block)
    return (m.group(1).strip() if m else '')[:80]


def _audio_duration_ms(path: Path) -> int | None:
    if not path.exists() or AudioSegment is None:
        return None
    try:
        return len(AudioSegment.from_mp3(path))
    except Exception:
        return None


def verify_level(level: str, start: int, end: int, *, original: bool = True) -> list[str]:
    errors: list[str] = []
    static = _REPO / 'static'
    prov = 'original' if original else 'blocked'

    ill_txt = Path(questions_file_abspath(level, 'listening_illustration_questions.txt', original=original))
    conv_txt = Path(questions_file_abspath(level, 'listening_conversation_questions.txt', original=original))
    pass_txt = Path(questions_file_abspath(level, 'listening_passage_questions.txt', original=original))

    ill_blocks = _blocks(ill_txt)
    conv_blocks = _blocks(conv_txt)
    pass_blocks = _blocks(pass_txt)

    for n in range(start, end + 1):
        # --- illustration ---
        if n not in ill_blocks:
            errors.append(f'level{level} ill #{n}: missing text block')
        else:
            exp_audio = db_audio_path(level, 'part1', f'listening_illustration_question{n}.mp3')
            exp_image = db_image_path_part1(level, f'listening_illustration_image{n}.png')
            ap = static / exp_audio
            ip = static / exp_image
            if not ap.exists():
                errors.append(f'level{level} ill #{n}: missing audio {exp_audio}')
            else:
                dur = _audio_duration_ms(ap)
                if dur is not None and dur < 3000:
                    errors.append(f'level{level} ill #{n}: audio too short ({dur}ms)')
            if not ip.exists():
                errors.append(f'level{level} ill #{n}: missing image {exp_image}')

            lq = ListeningQuestion.objects.filter(
                level=level, provenance=prov, image__contains=f'image{n}.png'
            ).first()
            if not lq:
                errors.append(f'level{level} ill #{n}: no DB ListeningQuestion')
            elif lq.audio != exp_audio or lq.image != exp_image:
                errors.append(
                    f'level{level} ill #{n}: DB path mismatch audio={lq.audio!r} image={lq.image!r}'
                )

        # --- conversation ---
        if n not in conv_blocks:
            errors.append(f'level{level} conv #{n}: missing text block')
        else:
            exp_audio = db_audio_path(level, 'part2', f'listening_conversation_question{n}.mp3')
            ap = static / exp_audio
            if not ap.exists():
                errors.append(f'level{level} conv #{n}: missing audio {exp_audio}')
            else:
                dur = _audio_duration_ms(ap)
                if dur is not None and dur < 3000:
                    errors.append(f'level{level} conv #{n}: audio too short ({dur}ms)')

            q = Question.objects.filter(
                level=level, question_type='listening_conversation', provenance=prov, question_number=n
            ).first()
            if not q:
                errors.append(f'level{level} conv #{n}: no DB Question')
            elif q.audio_file != exp_audio:
                errors.append(f'level{level} conv #{n}: DB audio_file={q.audio_file!r}')

        # --- passage ---
        if n not in pass_blocks:
            errors.append(f'level{level} pass #{n}: missing text block')
        else:
            exp_audio = db_audio_path(level, 'part3', f'listening_passage_question{n}.mp3')
            ap = static / exp_audio
            if not ap.exists():
                errors.append(f'level{level} pass #{n}: missing audio {exp_audio}')
            else:
                dur = _audio_duration_ms(ap)
                if dur is not None and dur < 3000:
                    errors.append(f'level{level} pass #{n}: audio too short ({dur}ms)')

            q = Question.objects.filter(
                level=level, question_type='listening_passage', provenance=prov, question_number=n
            ).first()
            if not q:
                errors.append(f'level{level} pass #{n}: no DB Question')
            elif q.audio_file != exp_audio:
                errors.append(f'level{level} pass #{n}: DB audio_file={q.audio_file!r}')

    # 番号ずれ検出: 同じ会話先頭行が別番号に重複していないか
    for label, blocks in [('ill', ill_blocks), ('conv', conv_blocks), ('pass', pass_blocks)]:
        seen: dict[str, int] = {}
        for n in range(start, end + 1):
            if n not in blocks:
                continue
            sig = _first_dialogue_line(blocks[n])
            if not sig:
                sig = _question_line(blocks[n])
            if sig in seen and seen[sig] != n:
                errors.append(
                    f'level{level} {label}: duplicate dialogue signature #{seen[sig]} and #{n}: {sig!r}'
                )
            seen[sig] = n

    return errors


def main():
    parser = argparse.ArgumentParser(description='Verify listening number/path alignment')
    parser.add_argument('--level', action='append', default=None)
    parser.add_argument('--start', type=int, default=11)
    parser.add_argument('--end', type=int, default=20)
    args = parser.parse_args()

    levels = args.level or ['3', '4']
    all_errors: list[str] = []
    for level in levels:
        all_errors.extend(verify_level(level, args.start, args.end))

    if all_errors:
        print('FAIL', len(all_errors), 'issue(s):')
        for e in all_errors:
            print(' -', e)
        raise SystemExit(1)

    print(f'OK: levels {levels} #{args.start}-#{args.end} — paths, DB, files, durations')


if __name__ == '__main__':
    main()
