"""リスニングイラスト問題の級別・部別フィルタ（5級 Part1/Part3 分割）。"""
import re

LISTENING_ILLUSTRATION_PART1_MAX = 30
LISTENING_ILLUSTRATION_PART3_MIN = 31


def listening_illustration_number(question):
    match = re.search(r'listening_illustration_image(\d+)\.png', question.image or '')
    return int(match.group(1)) if match else 0


def filter_listening_illustrations(questions, part=None):
    items = list(questions)
    if part == 1:
        return [
            question for question in items
            if 1 <= listening_illustration_number(question) <= LISTENING_ILLUSTRATION_PART1_MAX
        ]
    if part == 3:
        return [
            question for question in items
            if listening_illustration_number(question) >= LISTENING_ILLUSTRATION_PART3_MIN
        ]
    return items
