"""validate_original_questions.py の smoke テスト。"""

import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from utils.validate_original_questions import Issue, validate_file


class ValidateOriginalQuestionsTest(SimpleTestCase):
    def test_grammar_block_valid(self):
        text = """問題1:
A : Hi. B : ( )

選択肢1:
1. Hello.
2. Goodbye.
3. Maybe.
4. Often.

【正解1】
1. Hello.

【解説1】
Hello が正解です。

---
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'grammar_fill_questions.txt'
            path.write_text(text, encoding='utf-8')
            issues = validate_file('4', 'grammar_fill', path)
        errors = [i for i in issues if i.severity == 'error']
        self.assertEqual(errors, [])

    def test_grammar_missing_correct_is_error(self):
        text = """問題1:
Test ( )

選択肢1:
1. a
2. b
3. c
4. d

【解説1】
解説のみ。

---
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'grammar_fill_questions.txt'
            path.write_text(text, encoding='utf-8')
            issues = validate_file('4', 'grammar_fill', path)
        self.assertTrue(any(i.message.startswith('【正解') for i in issues))

    def test_study_point_invalid_category(self):
        text = """問題1:
Test ( )

選択肢1:
1. a
2. b
3. c
4. d

【正解1】
1. a

【解説1】
解説。

【ポイント1】
種別: 存在しない種別
見出し: テスト
・メモ

---
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'grammar_fill_questions.txt'
            path.write_text(text, encoding='utf-8')
            issues = validate_file('3', 'grammar_fill', path)
        self.assertTrue(
            any('種別が不正' in i.message for i in issues if isinstance(i, Issue))
        )
