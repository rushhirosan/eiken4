import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

# ライティング問題文: データ側は <u>...</u> で下線範囲を記述（|linebreaks ではタグが生かせない）
# 出力は <span class="writing-q-underline"> にし、Bootstrap / ブラウザ既定でも下線が確実に見えるようにする
_WRITING_U_TOKEN = re.compile(r'(<\s*u\s*>|<\s*/\s*u\s*>)', re.IGNORECASE)
_WRITING_PARA_SPLIT = re.compile(r'\r?\n\r?\n')
_EMAIL_FORM_START = '[[email-form-start]]'
_EMAIL_FORM_END = '[[email-form-end]]'
_EMAIL_ANSWER_BOX = '[[email-answer-box]]'
_EMAIL_ANSWER_BOX_HTML = (
    '<div class="writing-email-answer-box" style="border:1px solid #222;'
    'padding:0.85rem 1rem;margin:0.75rem 0;text-align:center;line-height:1.8;">'
    '返信の本文は、この枠の位置に入ります。<br>'
    '入力は、下の「あなたの英文」にしてください。'
    '</div>'
)
_EMAIL_FORM_OPEN = (
    '<div class="writing-email-form" style="border:1px solid #222;'
    'padding:0.9rem 1rem;margin:0.75rem 0;">'
)
# 3級など、目印なしで「Hi, 名前! / Thank you / Best wishes,」だけが入っている返信欄。
# 段落分割後なので、挨拶と Thank you のあいだは改行のまま。
_REPLY_GREETING_RE = re.compile(
    r'^Hi, [^!\n]+!\nThank you for your e-mail\.?$',
    re.IGNORECASE,
)


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
    blocks = [
        block.strip()
        for block in _WRITING_PARA_SPLIT.split(html)
        if block.strip()
    ]
    paras = []
    in_email_form = False
    i = 0
    while i < len(blocks):
        block = blocks[i]
        nxt = blocks[i + 1] if i + 1 < len(blocks) else ''
        if block == _EMAIL_FORM_START:
            paras.append(_EMAIL_FORM_OPEN)
            in_email_form = True
            i += 1
            continue
        if block == _EMAIL_FORM_END:
            if in_email_form:
                paras.append('</div>')
                in_email_form = False
            i += 1
            continue
        if block == _EMAIL_ANSWER_BOX:
            paras.append(_EMAIL_ANSWER_BOX_HTML)
            i += 1
            continue
        if (
            not in_email_form
            and _REPLY_GREETING_RE.match(block)
            and nxt.lower() == 'best wishes,'
        ):
            paras.append(_EMAIL_FORM_OPEN)
            paras.append('<p>' + block.replace('\n', '<br>') + '</p>')
            paras.append(_EMAIL_ANSWER_BOX_HTML)
            paras.append('<p>' + nxt.replace('\n', '<br>') + '</p>')
            paras.append('</div>')
            i += 2
            continue
        paras.append('<p>' + block.replace('\n', '<br>') + '</p>')
        i += 1
    if in_email_form:
        paras.append('</div>')
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


@register.simple_tag
def answer_field_name(question):
    """Typed answer_* name so Question / ListeningQuestion / ReadingQuestion PKs never collide."""
    from exams.answer_keys import answer_field_name as build_name, kind_for_model_instance

    return build_name(kind_for_model_instance(question), question.id)


@register.simple_tag
def choice_input_id(question, choice):
    """Typed choice_* HTML id paired with answer_field_name."""
    from exams.answer_keys import choice_dom_id, kind_for_model_instance

    return choice_dom_id(kind_for_model_instance(question), choice.id)
