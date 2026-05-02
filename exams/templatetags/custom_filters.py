import re

from django import template

register = template.Library()


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