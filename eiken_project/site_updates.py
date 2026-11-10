"""サイトの最近の更新メモ（DBなし。新しい行を先頭に足す）。"""

from __future__ import annotations

from typing import TypedDict


class SiteUpdate(TypedDict):
    date: str  # YYYY-MM-DD
    levels: list[str]  # '5' / '4' / '3' / 'pre2' / 'site'
    summary: str


# 新しい更新を上に追加する。公開に載せた内容だけ書く。
SITE_UPDATES: list[SiteUpdate] = [
    {
        'date': '2026-11-10',
        'levels': ['4', '3', 'pre2'],
        'summary': (
            '4級・3級・準2級のオリジナル練習を増やしました。'
            '4級は文法・語彙と語順、3級は文法・語彙・会話補充・ライティング、'
            '準2級は文法・語彙の型を追加しています。'
            '新しく足した問題は未回答のため、該当カテゴリの進捗％が少し下がることがあります。'
        ),
    },
    {
        'date': '2026-11-09',
        'levels': ['5'],
        'summary': '5級の文法・語彙と語順の練習を少し増やしました（定型表現・語順の型など）。',
    },
]


LEVEL_LABELS = {
    '5': '5級',
    '4': '4級',
    '3': '3級',
    'pre2': '準2級',
    'site': 'サイト全体',
}


def iter_site_updates() -> list[dict]:
    """テンプレ用にラベル付きで返す（新しい順のまま）。"""
    rows = []
    for item in SITE_UPDATES:
        labels = [LEVEL_LABELS.get(code, code) for code in item['levels']]
        rows.append({
            'date': item['date'],
            'levels': item['levels'],
            'level_labels': labels,
            'summary': item['summary'],
        })
    return rows
