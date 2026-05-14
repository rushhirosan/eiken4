import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

# ライティング問題文: データ側は <u>...</u> で下線範囲を記述（|linebreaks ではタグが生かせない）
# 出力は <span class="writing-q-underline"> にし、Bootstrap / ブラウザ既定でも下線が確実に見えるようにする
_WRITING_U_TOKEN = re.compile(r'(<\s*u\s*>|<\s*/\s*u\s*>)', re.IGNORECASE)
_WRITING_PARA_SPLIT = re.compile(r'\r?\n\r?\n')


@register.filter
def writing_prompt_html(value):
    """
    ライティングの問題文を HTML 化する。改行は段落／<br>、<u>...</u> のみ許可（他はエスケープ）。
    <u> は表示用に span.writing-q-underline に置き換える。
    """
    if value is None or value == '':
        return ''
    parts = _WRITING_U_TOKEN.split(str(value))
    buf: list[str] = []
    u_depth = 0
    for part in parts:
        if not part:
            continue
        norm = re.sub(r'\s+', '', part).lower()
        if norm == '<u>':
            buf.append(
                '<span class="writing-q-underline" style="text-decoration:underline;'
                'text-decoration-skip-ink:none;text-underline-offset:0.18em;'
                'text-decoration-thickness:0.11em">'
            )
            u_depth += 1
        elif norm == '</u>':
            if u_depth > 0:
                buf.append('</span>')
                u_depth -= 1
        else:
            buf.append(escape(part))
    if u_depth:
        buf.extend('</span>' * u_depth)
    html = ''.join(buf)
    paras = []
    for block in _WRITING_PARA_SPLIT.split(html):
        block = block.strip()
        if not block:
            continue
        paras.append('<p>' + block.replace('\n', '<br>') + '</p>')
    return mark_safe(''.join(paras)) if paras else mark_safe('')


@register.filter
def strip_question_no(value):
    """
    リスニング問題文に含まれる「Question No.12:」のような行を、
    読み上げ・表示では意味のない番号を読まないよう「Question」に置き換える。
    （ランダム出題時はマスタ番号が画面上の問いと一致しないため）
    """
    if value is None:
        return ''
    s = str(value)
    s = re.sub(r'Question No\.\s*\d+:\s*', 'Question ', s, flags=re.IGNORECASE)
    return s.strip()

@register.filter
def get_item(dictionary, key):
    """辞書から指定されたキーの値を取得する"""
    return dictionary.get(key)

@register.filter
def split(value, delimiter='\n'):
    """文字列を指定された区切り文字で分割する"""
    return value.split(delimiter)

@register.filter
def multiply(value, arg):
    """掛け算を行うフィルター"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """割り算を行うフィルター"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0 