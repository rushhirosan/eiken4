"""公式PDFツール用ガード（Django 非依存）。

ALLOW_LEGACY_PDF_IMPORT=1 のときだけ実行を許可。
ファイル自体は data/pdf_import に保管してよい（配信・再生成の既定経路にはしない）。
"""

from __future__ import annotations

import os
import sys

_MESSAGE = """\
レガシーPDFパイプラインは配信から切り離されています。

- data/pdf_import の保管・人が形式を思い出す用途は可
- PDF→txt→サイト公開の再実行は既定で禁止
- どうしてもローカルでツールを動かす場合のみ:
    ALLOW_LEGACY_PDF_IMPORT=1 python utils/...

公開用コンテンツは公式PDFを入力にせず、新規自作してください。
"""


def require_legacy_pdf_tools_allowed() -> None:
    if os.environ.get('ALLOW_LEGACY_PDF_IMPORT') == '1':
        return
    print(_MESSAGE, file=sys.stderr)
    sys.exit(2)
