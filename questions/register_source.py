"""register_* / create_* の original / legacy 切り替え。"""

from __future__ import annotations

from django.core.management.base import CommandError

from exams.provenance import PROVENANCE_BLOCKED, PROVENANCE_ORIGINAL
from questions.legacy_import import assert_legacy_question_import_allowed
from questions.level_paths import questions_file_abspath


def resolve_register_io(options: dict, filename: str) -> tuple[str, str, str, bool]:
    """登録コマンド用に (level, txt_path, provenance, is_original) を返す。"""
    level = options['level']
    is_original = bool(options.get('original'))
    if is_original and options.get('allow_legacy_blocked_import'):
        raise CommandError('--original と --allow-legacy-blocked-import は同時に使えません。')
    if is_original:
        txt_path = questions_file_abspath(level, filename, original=True)
        return level, txt_path, PROVENANCE_ORIGINAL, True
    assert_legacy_question_import_allowed(
        allow_flag=options.get('allow_legacy_blocked_import', False)
    )
    txt_path = questions_file_abspath(level, filename, original=False)
    return level, txt_path, PROVENANCE_BLOCKED, False
