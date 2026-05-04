"""
級別の問題テキスト・静的ファイル（DB に保存する相対パス）の規約。

- level=='4': 従来どおり data/questions/*.txt、audio/part*、images/part1（変更しない）。
- level=='3': data/questions/level3/*.txt、audio/level3/part*、images/level3/part1。
"""
import os

from django.conf import settings


def questions_file_relpath(level: str, filename: str) -> str:
    """プロジェクトルートからの相対パス（manage.py と同じ cwd を想定）。"""
    if level == '4':
        return os.path.join('data', 'questions', filename)
    return os.path.join('data', 'questions', f'level{level}', filename)


def questions_file_abspath(level: str, filename: str) -> str:
    return os.path.join(settings.BASE_DIR, questions_file_relpath(level, filename))


def db_audio_path(level: str, part: str, basename: str) -> str:
    """part: part1 | part2 | part3"""
    if level == '4':
        return f'audio/{part}/{basename}'
    return f'audio/level{level}/{part}/{basename}'


def db_image_path_part1(level: str, basename: str) -> str:
    if level == '4':
        return f'images/part1/{basename}'
    return f'images/level{level}/part1/{basename}'


def static_audio_dir(level: str, part: str) -> str:
    if level == '4':
        return os.path.join(settings.BASE_DIR, 'static', 'audio', part)
    return os.path.join(settings.BASE_DIR, 'static', 'audio', f'level{level}', part)


def static_images_part1_dir(level: str) -> str:
    if level == '4':
        return os.path.join(settings.BASE_DIR, 'static', 'images', 'part1')
    return os.path.join(settings.BASE_DIR, 'static', 'images', f'level{level}', 'part1')


def add_default_register_arguments(parser):
    """register_* / create_* 共通: --level（既定 4、3 級は level3 配下と DB）。"""
    parser.add_argument(
        '--level',
        type=str,
        default='4',
        choices=['3', '4'],
        help='試験級（既定: 4）。3 のとき data/questions/level3/ と DB の level=3 を使用。',
    )
