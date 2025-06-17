from django import template

register = template.Library()

@register.filter
def get_correct_choice(choices):
    """正解の選択肢を取得する"""
    return choices.filter(is_correct=True).first().choice_text 