from django import template

register = template.Library()

@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def get_correct_choice(choices):
    for choice in choices:
        if choice.is_correct:
            return choice.choice_text
    return '' 