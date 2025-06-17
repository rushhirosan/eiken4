from django import template

register = template.Library()

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