"""問題の出所（provenance）と公開フィルタ。

シンプル方針（分類しない）:
- 既存は出所を公式/AI などで振り分けない（誤ラベル自体がリスク）
- 既存はすべて blocked（削除せず非公開）
- 公開してよいのは、公式PDFも既存問題文も見ずに新規作成し、
  明示的に provenance=original としたものだけ
- 登録コマンド（過去問テキスト取り込み）は常に blocked
"""

from __future__ import annotations

from django.db import models

PROVENANCE_ORIGINAL = 'original'
PROVENANCE_BLOCKED = 'blocked'

PROVENANCE_CHOICES = [
    (PROVENANCE_ORIGINAL, 'オリジナル（公開可・明示したもののみ）'),
    (PROVENANCE_BLOCKED, '非公開（既存・未確認・取り込み含む）'),
]


class ProvenanceQuerySet(models.QuerySet):
    def published(self):
        return self.filter(provenance=PROVENANCE_ORIGINAL)

    def blocked(self):
        return self.filter(provenance=PROVENANCE_BLOCKED)


class ProvenanceManager(models.Manager.from_queryset(ProvenanceQuerySet)):
    """objects.published() で公開分だけ取得する。"""


def published_kwargs():
    """filter / get 用: provenance=original。"""
    return {'provenance': PROVENANCE_ORIGINAL}


def passage_published_kwargs():
    """ReadingQuestion 経由: passage が original。"""
    return {'passage__provenance': PROVENANCE_ORIGINAL}
