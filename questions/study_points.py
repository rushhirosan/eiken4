"""問題テキストの【ポイントN】ブロックを学習ポイント（study_points）に変換する。

テキスト形式::

    【ポイント1】
    種別: 文法
    見出し: 理由をたずねる Why には Because で答える
    ・Because + 主語 + 動詞 で理由を表す
    ・Although は逆接、Before / Until は時を表す

`種別` は Question.STUDY_POINT_BADGE_CLASSES のキーに合わせる。
"""

import re

# 【解説N】の終端。空行で切らず、次のブロックかチャンク末尾までを解説とする
EXPLANATION_PATTERN = r'【解説{suffix}】\s*(.*?)(?=\n*【ポイント{suffix}】|\Z)'
POINT_PATTERN = r'【ポイント{suffix}】\s*(.*?)(?=\n*【|\Z)'


def explanation_regex(suffix=r'\d+'):
    """【解説N】本文を取り出す正規表現。suffix は識別子つき（例: r'\\d+[a-z]'）にも使える。"""
    return EXPLANATION_PATTERN.format(suffix=suffix)


def extract_explanation(block, suffix=r'\d+'):
    match = re.search(explanation_regex(suffix), block, re.DOTALL)
    return match.group(1).strip() if match else ''


def extract_study_points(block, suffix=r'\d+'):
    """【ポイントN】ブロックを dict にする。無ければ None。"""
    match = re.search(POINT_PATTERN.format(suffix=suffix), block, re.DOTALL)
    if not match:
        return None

    category = ''
    title = ''
    keys = []
    for raw_line in match.group(1).split('\n'):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith('種別:') or line.startswith('種別：'):
            category = line.split(':', 1)[-1].split('：', 1)[-1].strip()
        elif line.startswith('見出し:') or line.startswith('見出し：'):
            title = line.split(':', 1)[-1].split('：', 1)[-1].strip()
        elif line.startswith('・'):
            keys.append(line.lstrip('・').strip())

    if not (category or title or keys):
        return None
    return {'category': category, 'title': title, 'keys': keys}
