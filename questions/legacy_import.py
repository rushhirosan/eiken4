"""レガシー（公式PDF由来）問題の取り込みガード。

方針:
- data/pdf_import や既存 txt は保管・形式参考用に残してよい
- サイトへの配信・再登録は既定で禁止（問題ゼロ公開を維持）
- 明示フラグ時のみ blocked 登録を許可（公開には出ない）
"""

from __future__ import annotations

from django.conf import settings
from django.core.management.base import CommandError

LEGACY_IMPORT_BLOCK_MESSAGE = (
    'レガシー問題の取り込みは配信パイプラインから切り離されています。\n'
    '公式PDF由来・既存 data/questions の再登録は既定で禁止です。\n'
    '（保管ファイルの参照や、形式を頭に入れての自作は可能です。）\n'
    '\n'
    'どうしても blocked としてDBに再投入する場合のみ:\n'
    '  --allow-legacy-blocked-import\n'
    'または settings.LEGACY_QUESTION_IMPORT_ENABLED = True\n'
    '\n'
    '公開用は data/questions/original/ に新規自作し provenance=original で登録してください。'
)


def assert_legacy_question_import_allowed(*, allow_flag: bool = False) -> None:
    """register/create/append の先頭で呼ぶ。許可されていなければ CommandError。"""
    if getattr(settings, 'LEGACY_QUESTION_IMPORT_ENABLED', False):
        return
    if allow_flag:
        return
    raise CommandError(LEGACY_IMPORT_BLOCK_MESSAGE)
