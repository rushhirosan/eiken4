"""回答結果向け next-learning 出し分けの単体テスト。"""

from django.test import SimpleTestCase, override_settings

from eiken_project.next_learning import (
    NEXT_LEARNING_WEEK_SESSION_KEY,
    affiliate_url,
    mark_next_learning_tip_shown,
    next_learning_weekly_cap_allows,
    select_answer_result_tip,
)


class AffiliateUrlTest(SimpleTestCase):
    def test_adds_tag_when_configured(self):
        base = 'https://www.amazon.co.jp/s?k=%E8%8B%B1%E6%A4%9C+4%E7%B4%9A'
        with override_settings(AMAZON_ASSOCIATE_TAG='eikenpractice-22'):
            out = affiliate_url(base)
        self.assertIn('tag=eikenpractice-22', out)
        self.assertIn('k=', out)

    def test_leaves_url_when_tag_empty(self):
        base = 'https://www.amazon.co.jp/s?k=test'
        with override_settings(AMAZON_ASSOCIATE_TAG=''):
            self.assertEqual(affiliate_url(base), base)


class SelectAnswerResultTipTest(SimpleTestCase):
    def test_mock_exam_always_on_completion(self):
        tip = select_answer_result_tip(
            level='4',
            question_type='mock_exam',
            correct_count=10,
            total_count=10,
        )
        self.assertIsNotNone(tip)
        self.assertIn('過去問', tip['resource_title'])

    def test_reading_when_accuracy_low(self):
        tip = select_answer_result_tip(
            level='4',
            question_type='reading_comprehension',
            correct_count=3,
            total_count=10,
        )
        self.assertIsNotNone(tip)
        self.assertIn('長文', tip['resource_title'])

    def test_reading_skipped_when_accuracy_high(self):
        tip = select_answer_result_tip(
            level='4',
            question_type='reading_comprehension',
            correct_count=8,
            total_count=10,
        )
        self.assertIsNone(tip)

    def test_grammar_mid_band(self):
        tip = select_answer_result_tip(
            level='5',
            question_type='grammar_fill',
            correct_count=6,
            total_count=10,
        )
        self.assertIsNotNone(tip)
        self.assertIn('単語帳', tip['resource_title'])

    def test_grammar_mid_band_level3(self):
        tip = select_answer_result_tip(
            level='3',
            question_type='grammar_fill',
            correct_count=6,
            total_count=10,
        )
        self.assertIsNotNone(tip)
        self.assertIn('単語帳', tip['resource_title'])

    def test_grammar_outside_band(self):
        self.assertIsNone(
            select_answer_result_tip(
                level='5',
                question_type='grammar_fill',
                correct_count=9,
                total_count=10,
            )
        )
        self.assertIsNone(
            select_answer_result_tip(
                level='5',
                question_type='grammar_fill',
                correct_count=2,
                total_count=10,
            )
        )

    def test_listening_when_low(self):
        tip = select_answer_result_tip(
            level='3',
            question_type='listening_conversation',
            correct_count=2,
            total_count=5,
        )
        self.assertIsNotNone(tip)
        self.assertIn('過去問', tip['resource_title'])

    def test_writing_on_submit(self):
        tip = select_answer_result_tip(
            level='3',
            question_type='writing',
            correct_count=1,
            total_count=1,
        )
        self.assertIsNotNone(tip)
        self.assertIn('ライティング', tip['resource_title'])

    def test_conversation_and_random_skipped(self):
        self.assertIsNone(
            select_answer_result_tip(
                level='4',
                question_type='conversation_fill',
                correct_count=1,
                total_count=5,
            )
        )
        self.assertIsNone(
            select_answer_result_tip(
                level='4',
                question_type='word_order',
                correct_count=1,
                total_count=5,
            )
        )
        self.assertIsNone(
            select_answer_result_tip(
                level='4',
                question_type='random',
                correct_count=1,
                total_count=5,
            )
        )


class WeeklyCapTest(SimpleTestCase):
    def test_weekly_cap_blocks_second_show(self):
        class Sess(dict):
            modified = False

        session = Sess()
        self.assertTrue(next_learning_weekly_cap_allows(session))
        mark_next_learning_tip_shown(session)
        self.assertIn(NEXT_LEARNING_WEEK_SESSION_KEY, session)
        self.assertTrue(session.modified)
        self.assertFalse(next_learning_weekly_cap_allows(session))
