"""utils スクリプト用の級別パス（Django なし）。既定は 4 級の既存レイアウト。"""
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def questions_txt(level: str, basename: str) -> str:
    if level == '4':
        return os.path.join(_ROOT, 'data', 'questions', basename)
    return os.path.join(_ROOT, 'data', 'questions', f'level{level}', basename)


def static_audio_part(level: str, part: str) -> str:
    if level == '4':
        return os.path.join(_ROOT, 'static', 'audio', part)
    return os.path.join(_ROOT, 'static', 'audio', f'level{level}', part)


def static_images_part1(level: str) -> str:
    if level == '4':
        return os.path.join(_ROOT, 'static', 'images', 'part1')
    return os.path.join(_ROOT, 'static', 'images', f'level{level}', 'part1')
