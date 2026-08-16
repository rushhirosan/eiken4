"""
級別の問題テキスト・静的ファイル（DB に保存する相対パス）の規約。

- 音声・画像: 全級とも `static/audio/level{N}/part*`・`static/images/level{N}/part1`
  （DB 相対パスは `audio/level{N}/part*`・`images/level{N}/part1`）。
- レガシー問題 txt: level=='4' は `data/questions/*.txt`、3/5 は `data/questions/level{N}/`。
- 公開用 original: `data/questions/original/level{N}/`。
- 5級イラスト系: No.1–100→part1（会話応答）、No.101+→part3（イラスト一致）。
"""
import os

from django.conf import settings


def questions_file_relpath(level: str, filename: str, *, original: bool = False) -> str:
    """プロジェクトルートからの相対パス（manage.py と同じ cwd を想定）。"""
    if original:
        return os.path.join('data', 'questions', 'original', f'level{level}', filename)
    if level == '4':
        return os.path.join('data', 'questions', filename)
    return os.path.join('data', 'questions', f'level{level}', filename)


def questions_file_abspath(level: str, filename: str, *, original: bool = False) -> str:
    return os.path.join(settings.BASE_DIR, questions_file_relpath(level, filename, original=original))


LISTENING_ILLUSTRATION_PART3_MIN = 101


def listening_illustration_audio_part(level: str, question_number: int) -> str:
    """イラストリスニングの音声 part。5級 No.101+ は第3部（イラスト一致）に合わせ part3。"""
    if level == '5' and question_number >= LISTENING_ILLUSTRATION_PART3_MIN:
        return 'part3'
    return 'part1'


def db_audio_path(level: str, part: str, basename: str) -> str:
    """part: part1 | part2 | part3"""
    return f'audio/level{level}/{part}/{basename}'


def db_image_path_part1(level: str, basename: str) -> str:
    return f'images/level{level}/part1/{basename}'


def static_audio_dir(level: str, part: str) -> str:
    return os.path.join(settings.BASE_DIR, 'static', 'audio', f'level{level}', part)


def static_images_part1_dir(level: str) -> str:
    """公開用 static。公式由来アーカイブは archived_images_part1_dir。"""
    return os.path.join(settings.BASE_DIR, 'static', 'images', f'level{level}', 'part1')


def archived_audio_dir(level: str, part: str) -> str:
    """公式由来音声の保管先（配信対象外）。"""
    return os.path.join(
        settings.BASE_DIR, 'data', 'archived_media', 'audio', f'level{level}', part
    )


def archived_images_part1_dir(level: str) -> str:
    """公式由来画像の保管先（配信対象外）。"""
    return os.path.join(
        settings.BASE_DIR, 'data', 'archived_media', 'images', f'level{level}', 'part1'
    )


def add_default_register_arguments(parser):
    """register_* / create_* 共通: --level（既定 4、3 級は level3 配下と DB）。"""
    parser.add_argument(
        '--level',
        type=str,
        default='4',
        choices=['3', '4', '5'],
        help='試験級（既定: 4）。3/5 のとき data/questions/level{N}/ と DB の level=N を使用。',
    )
    parser.add_argument(
        '--original',
        action='store_true',
        help=(
            'data/questions/original/level{N}/ から読み、provenance=original で登録する。'
            '既存の original のみ削除して差し替える（blocked は残す）。'
        ),
    )
    parser.add_argument(
        '--allow-legacy-blocked-import',
        action='store_true',
        help=(
            'レガシー取り込み禁止を一時解除し、provenance=blocked として再登録する。'
            '公開には出ない。通常は使わない。'
        ),
    )
