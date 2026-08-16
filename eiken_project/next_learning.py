"""「このあとの学習」アフィリエイト導線のコピーとリンク。

ベース URL は Amazon.co.jp 検索。`settings.AMAZON_ASSOCIATE_TAG` があれば
クエリに `tag=` を付与して紹介料対象にする（Fly の環境変数で設定）。
"""

from __future__ import annotations

from typing import TypedDict
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def affiliate_url(url: str, tag: str | None = None) -> str:
    """Amazon URL にアソシエイトタグを付与。タグが空ならそのまま返す。"""
    if not url:
        return url
    if tag is None:
        try:
            from django.conf import settings

            tag = (getattr(settings, 'AMAZON_ASSOCIATE_TAG', '') or '').strip()
        except Exception:
            tag = ''
    else:
        tag = (tag or '').strip()
    if not tag:
        return url

    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query['tag'] = tag
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
    )


class NextLearningResource(TypedDict):
    level: str
    level_label: str
    reason: str
    resource_title: str
    resource_url: str


class LearningTip(TypedDict):
    title: str
    reason: str
    url: str
    optional: bool


class ResourcesPageSection(TypedDict):
    level: str
    level_label: str
    intro: str
    tips: list[LearningTip]
    official_past_questions_url: str
    official_past_questions_label: str


# 協会の級別過去問ページ（アフィリエイト対象外）
OFFICIAL_GRADE_PAST_QUESTION_URLS: dict[str, str] = {
    '5': 'https://www.eiken.or.jp/eiken/exam/grade_5/',
    '4': 'https://www.eiken.or.jp/eiken/exam/grade_4/',
    '3': 'https://www.eiken.or.jp/eiken/exam/grade_3/',
}


def official_past_questions_url(level: str) -> str:
    """級の協会公式過去問ページ URL。未知の級は試験一覧へ。"""
    return OFFICIAL_GRADE_PAST_QUESTION_URLS.get(
        str(level),
        'https://www.eiken.or.jp/eiken/exam/',
    )

NEXT_LEARNING_BY_LEVEL: dict[str, NextLearningResource] = {
    '5': {
        'level': '5',
        'level_label': '5級',
        'reason': (
            'このサイトの演習だけでも十分進められます。'
            '紙の過去問・問題集は必須ではありませんが、時間配分やマークの感覚を'
            '一度確かめたいときの参考になります。'
        ),
        'resource_title': '5級の過去問・問題集を見てみる',
        'resource_url': 'https://www.amazon.co.jp/s?k=%E8%8B%B1%E6%A4%9C+5%E7%B4%9A+%E9%81%8E%E5%8E%BB%E5%95%8F',
    },
    '4': {
        'level': '4',
        'level_label': '4級',
        'reason': (
            'このサイトの練習を続けて大丈夫です。'
            '紙の過去問・問題集は必須ではありませんが、長文込みの通しペースを'
            '一度確かめたいときの参考になります。'
        ),
        'resource_title': '4級の過去問・問題集を見てみる',
        'resource_url': 'https://www.amazon.co.jp/s?k=%E8%8B%B1%E6%A4%9C+4%E7%B4%9A+%E9%81%8E%E5%8E%BB%E5%95%8F',
    },
    '3': {
        'level': '3',
        'level_label': '3級',
        'reason': (
            'このサイトで選択とライティングを分けて練習するだけで十分進められます。'
            '紙の過去問・問題集は必須ではありませんが、全体の流れを一度通したいときの参考になります。'
        ),
        'resource_title': '3級の過去問・問題集を見てみる',
        'resource_url': 'https://www.amazon.co.jp/s?k=%E8%8B%B1%E6%A4%9C+3%E7%B4%9A+%E9%81%8E%E5%8E%BB%E5%95%8F',
    },
}


def decorated_next_learning_by_level() -> dict[str, NextLearningResource]:
    """guides 用。resource_url にタグを付与したコピー。"""
    return {
        key: {
            **value,
            'resource_url': affiliate_url(value['resource_url']),
        }
        for key, value in NEXT_LEARNING_BY_LEVEL.items()
    }


def next_learning_for_guides() -> list[NextLearningResource]:
    """ガイドページ用に 5→4→3 の順で返す。"""
    by_level = decorated_next_learning_by_level()
    return [by_level['5'], by_level['4'], by_level['3']]


def resources_page_sections() -> list[ResourcesPageSection]:
    """学習リソース一覧ページ用（過去問＋任意の補強）。URL にタグを付与。"""
    raw: list[ResourcesPageSection] = [
        {
            'level': '5',
            'level_label': '5級',
            'intro': (
                '入門級です。サイトで文法・会話・リスニングを固めるだけで十分進められます。'
                '紙の過去問・問題集は必須ではありません。'
            ),
            'official_past_questions_url': OFFICIAL_GRADE_PAST_QUESTION_URLS['5'],
            'official_past_questions_label': '協会の5級過去問・試験内容ページ（公式）',
            'tips': [
                {
                    'title': '5級の過去問・問題集',
                    'reason': '時間配分やマークの感覚を一度確かめたいときの参考です。購入の義務はありません。',
                    'url': NEXT_LEARNING_BY_LEVEL['5']['resource_url'],
                    'optional': False,
                },
                {
                    'title': '5級向けの単語帳',
                    'reason': '文法演習と並行して、短い単語学習を足したいときの選択肢です。',
                    'url': 'https://www.amazon.co.jp/s?k=%E8%8B%B1%E6%A4%9C+5%E7%B4%9A+%E5%8D%98%E8%AA%9E',
                    'optional': True,
                },
            ],
        },
        {
            'level': '4',
            'level_label': '4級',
            'intro': (
                '長文が加わる級です。サイトで形式別に練習するだけで十分進められます。'
                '紙の過去問・問題集は必須ではありません。'
            ),
            'official_past_questions_url': OFFICIAL_GRADE_PAST_QUESTION_URLS['4'],
            'official_past_questions_label': '協会の4級過去問・試験内容ページ（公式）',
            'tips': [
                {
                    'title': '4級の過去問・問題集',
                    'reason': '長文込みのペース配分を一度通したいときの参考です。購入の義務はありません。',
                    'url': NEXT_LEARNING_BY_LEVEL['4']['resource_url'],
                    'optional': False,
                },
                {
                    'title': '4級の長文対策',
                    'reason': 'サイトの長文読解メニューで慣れたあと、解説付きの長文問題集で読み方の型を固めたいときの選択肢です。',
                    'url': 'https://www.amazon.co.jp/s?k=%E8%8B%B1%E6%A4%9C+4%E7%B4%9A+%E9%95%B7%E6%96%87',
                    'optional': True,
                },
                {
                    'title': '4級向けの単語帳',
                    'reason': '正答率が伸び悩むときの語彙補強として併用する人もいます。',
                    'url': 'https://www.amazon.co.jp/s?k=%E8%8B%B1%E6%A4%9C+4%E7%B4%9A+%E5%8D%98%E8%AA%9E',
                    'optional': True,
                },
            ],
        },
        {
            'level': '3',
            'level_label': '3級',
            'intro': (
                'ライティングがある級です。選択問題と英作文をサイトで分けて練習するだけで十分進められます。'
                '紙の過去問・問題集は必須ではありません。'
            ),
            'official_past_questions_url': OFFICIAL_GRADE_PAST_QUESTION_URLS['3'],
            'official_past_questions_label': '協会の3級過去問・試験内容ページ（公式）',
            'tips': [
                {
                    'title': '3級の過去問・問題集',
                    'reason': '選択・読解・リスニングの通しを一度確かめたいときの参考です。購入の義務はありません。',
                    'url': NEXT_LEARNING_BY_LEVEL['3']['resource_url'],
                    'optional': False,
                },
                {
                    'title': '3級の長文対策',
                    'reason': 'サイトの読解演習のあとに、長めの文章の読み方・設問の解き方を本で補強したいときの選択肢です。',
                    'url': 'https://www.amazon.co.jp/s?k=%E8%8B%B1%E6%A4%9C+3%E7%B4%9A+%E9%95%B7%E6%96%87',
                    'optional': True,
                },
                {
                    'title': '3級向けの単語帳',
                    'reason': '文法・語彙の正答率が伸び悩むときの補強として併用する人もいます。',
                    'url': 'https://www.amazon.co.jp/s?k=%E8%8B%B1%E6%A4%9C+3%E7%B4%9A+%E5%8D%98%E8%AA%9E',
                    'optional': True,
                },
                {
                    'title': '3級の英作文・ライティング対策',
                    'reason': 'サイトの自己チェックのあとに、書き方の型を本で確認したいときの選択肢です。',
                    'url': 'https://www.amazon.co.jp/s?k=%E8%8B%B1%E6%A4%9C+3%E7%B4%9A+%E3%83%A9%E3%82%A4%E3%83%86%E3%82%A3%E3%83%B3%E3%82%B0',
                    'optional': True,
                },
            ],
        },
    ]
    return [
        {
            **section,
            'tips': [
                {**tip, 'url': affiliate_url(tip['url'])}
                for tip in section['tips']
            ],
        }
        for section in raw
    ]


# --- 回答結果画面用（条件付き・週1回） ---

NEXT_LEARNING_WEEK_SESSION_KEY = 'next_learning_tip_week_id'

LISTENING_RESULT_TYPES = frozenset({
    'listening_illustration',
    'listening_illustration_part3',
    'listening_conversation',
    'listening_passage',
})

# 会話・語順・ランダムは出さない（ランダムは Phase 2）
_SKIP_RESULT_TYPES = frozenset({
    'conversation_fill',
    'word_order',
    'random',
})


class AnswerResultTip(TypedDict):
    reason: str
    resource_title: str
    resource_url: str


def _accuracy_percent(correct_count: int, total_count: int) -> float | None:
    if total_count <= 0:
        return None
    return (correct_count / total_count) * 100.0


def _tip_from_section(level: str, title_substr: str) -> AnswerResultTip | None:
    level = str(level)
    for section in resources_page_sections():
        if section['level'] != level:
            continue
        for tip in section['tips']:
            if title_substr in tip['title']:
                return {
                    'reason': tip['reason'],
                    'resource_title': tip['title'] + 'を見てみる',
                    'resource_url': tip['url'],  # already tagged via resources_page_sections
                }
    return None


def _past_papers_tip(level: str) -> AnswerResultTip | None:
    base = NEXT_LEARNING_BY_LEVEL.get(str(level))
    if not base:
        return None
    return {
        'reason': (
            'このサイトの練習を続けて大丈夫です。'
            '紙の過去問・問題集は必須ではありませんが、時間配分や本番の流れを'
            '一度確かめたいときの参考になります。'
        ),
        'resource_title': base['resource_title'],
        'resource_url': affiliate_url(base['resource_url']),
    }


def select_answer_result_tip(
    *,
    level: str,
    question_type: str,
    correct_count: int,
    total_count: int,
) -> AnswerResultTip | None:
    """回答結果向けのアフィリ導線。条件に合わなければ None。

    模擬: 完了時（1問以上）→ 過去問
    長文: 正答率 ≤60% → 長文対策
    文法: 正答率 50〜70% → 単語帳
    リスニング: 正答率 ≤60% → 過去問
    ライティング: 提出完了 → ライティング本
    会話・語順・ランダム: 出さない
    """
    level = str(level)
    question_type = str(question_type)
    if question_type in _SKIP_RESULT_TYPES:
        return None
    if total_count <= 0:
        return None

    if question_type == 'mock_exam':
        tip = _past_papers_tip(level)
        if tip:
            tip = {
                **tip,
                'reason': (
                    '模擬試験まで終えたら、このままサイトで復習するだけで十分です。'
                    '紙の過去問・問題集は必須ではありませんが、時間配分を一度確かめたいときの参考になります。'
                ),
            }
        return tip

    if question_type == 'writing':
        if level != '3':
            return None
        return _tip_from_section(level, 'ライティング')

    rate = _accuracy_percent(correct_count, total_count)
    if rate is None:
        return None

    if question_type == 'reading_comprehension':
        if rate <= 60.0:
            return _tip_from_section(level, '長文対策')
        return None

    if question_type == 'grammar_fill':
        if 50.0 <= rate <= 70.0:
            return _tip_from_section(level, '単語帳')
        return None

    if question_type in LISTENING_RESULT_TYPES:
        if rate <= 60.0:
            tip = _past_papers_tip(level)
            if tip:
                tip = {
                    **tip,
                    'reason': (
                        'リスニングで伸びしろが見えたときは、過去問の音声付き問題で'
                        '耳を慣らすのも手です。'
                    ),
                }
            return tip
        return None

    return None


def current_next_learning_week_id(today=None) -> str:
    from django.utils import timezone

    day = today or timezone.localdate()
    iso = day.isocalendar()
    return f'{iso.year}-W{iso.week:02d}'


def next_learning_weekly_cap_allows(session) -> bool:
    """同一ユーザー（セッション）あたり週1回まで。"""
    shown = session.get(NEXT_LEARNING_WEEK_SESSION_KEY)
    return shown != current_next_learning_week_id()


def mark_next_learning_tip_shown(session) -> None:
    session[NEXT_LEARNING_WEEK_SESSION_KEY] = current_next_learning_week_id()
    session.modified = True
