"""utils スクリプト用の級別パス（Django なし）。音声・画像は全級 level{N}/ 配下。"""
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def questions_txt(level: str, basename: str) -> str:
    """レガシー問題 txt。4級は直下、3/5 は level{N}/。original は別途指定。"""
    if level == '4':
        return os.path.join(_ROOT, 'data', 'questions', basename)
    return os.path.join(_ROOT, 'data', 'questions', f'level{level}', basename)


LISTENING_ILLUSTRATION_PART3_MIN = 101


def listening_illustration_audio_part(level: str, question_number: int) -> str:
    if level == '5' and question_number >= LISTENING_ILLUSTRATION_PART3_MIN:
        return 'part3'
    return 'part1'


def static_audio_part(level: str, part: str) -> str:
    return os.path.join(_ROOT, 'static', 'audio', f'level{level}', part)


def static_images_part1(level: str) -> str:
    return os.path.join(_ROOT, 'static', 'images', f'level{level}', 'part1')


def default_tts_rate(level: str) -> str:
    """Edge TTS 話速の級別既定。5級は初学者向けに少しゆっくり。"""
    return '-15%' if level == '5' else '+0%'
