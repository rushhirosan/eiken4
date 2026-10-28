import re
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from exams.choice_shuffle import (
    apply_choice_shuffle_to_items,
    choice_order_session_key,
    order_choices_for_display,
    remap_explanation_choice_numbers,
    should_shuffle_choices,
)
from exams.models import Choice, Question
from questions.models import ReadingChoice, ReadingPassage, ReadingQuestion
from exams.provenance import PROVENANCE_ORIGINAL

User = get_user_model()


class ChoiceShuffleHelpersTest(TestCase):
    def test_should_shuffle_targets(self):
        self.assertTrue(should_shuffle_choices('grammar_fill'))
        self.assertTrue(should_shuffle_choices('conversation_fill'))
        self.assertFalse(should_shuffle_choices('listening_illustration'))
        self.assertFalse(should_shuffle_choices('reading_comprehension'))
        self.assertFalse(should_shuffle_choices('word_order'))
        self.assertFalse(should_shuffle_choices(None))

    def test_display_order_is_stable_within_session(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.session = self.client.session

        question = Question.objects.create(
            provenance=PROVENANCE_ORIGINAL,
            level='3',
            question_type='grammar_fill',
            question_text='Shuffle test',
        )
        choices = [
            Choice.objects.create(
                question=question,
                choice_text=f'choice-{index}',
                is_correct=index == 1,
                order=index,
            )
            for index in range(1, 5)
        ]

        with patch('exams.choice_shuffle.random.shuffle', side_effect=lambda items: items.reverse()):
            first = order_choices_for_display(
                request, '3', 'grammar_fill', question.id, choices
            )
            second = order_choices_for_display(
                request, '3', 'grammar_fill', question.id, choices
            )

        self.assertEqual([choice.id for choice in first], [choice.id for choice in second])
        self.assertNotEqual(
            [choice.id for choice in first],
            [choice.id for choice in sorted(choices, key=lambda c: c.order)],
        )

    def test_reading_comprehension_keeps_database_order(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.session = self.client.session

        passage = ReadingPassage.objects.create(
            provenance=PROVENANCE_ORIGINAL,level='3', identifier='a', text='本文')
        reading_question = ReadingQuestion.objects.create(
            passage=passage,
            question_text='Q1',
            question_number=1,
        )
        choices = [
            ReadingChoice.objects.create(
                question=reading_question,
                choice_text=f'reading-{index}',
                is_correct=index == 1,
                order=index,
            )
            for index in range(1, 5)
        ]

        with patch('exams.choice_shuffle.random.shuffle', side_effect=lambda items: items.reverse()):
            ordered = order_choices_for_display(
                request,
                '3',
                'reading_comprehension',
                reading_question.id,
                choices,
            )

        self.assertEqual(
            [choice.choice_text for choice in ordered],
            ['reading-1', 'reading-2', 'reading-3', 'reading-4'],
        )

    def test_create_if_missing_false_does_not_shuffle(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.session = self.client.session

        question = Question.objects.create(
            provenance=PROVENANCE_ORIGINAL,
            level='3',
            question_type='grammar_fill',
            question_text='No create',
        )
        choices = [
            Choice.objects.create(
                question=question,
                choice_text=f'choice-{index}',
                is_correct=index == 1,
                order=index,
            )
            for index in range(1, 5)
        ]

        with patch('exams.choice_shuffle.random.shuffle', side_effect=lambda items: items.reverse()):
            ordered = order_choices_for_display(
                request,
                '3',
                'grammar_fill',
                question.id,
                choices,
                create_if_missing=False,
            )

        self.assertEqual(
            [choice.id for choice in ordered],
            [choice.id for choice in choices],
        )
        self.assertNotIn(str(question.id), request.session.get(choice_order_session_key('3'), {}))


class ChoiceShuffleIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='shuffle_user',
            email='shuffle@example.com',
            password='testpass123',
        )
        self.client.login(username='shuffle_user', password='testpass123')

        self.question = Question.objects.create(
            provenance=PROVENANCE_ORIGINAL,
            level='3',
            question_type='grammar_fill',
            question_text='Visitors ( ) to show their tickets.',
            question_number=83,
        )
        self.correct = Choice.objects.create(
            question=self.question,
            choice_text='have',
            is_correct=True,
            order=1,
        )
        self.wrong_choices = [
            Choice.objects.create(
                question=self.question,
                choice_text=text,
                is_correct=False,
                order=index,
            )
            for index, text in enumerate(['has', 'having', 'had'], start=2)
        ]

    def _grammar_list_url(self):
        return (
            reverse('exams:question_list_by_level', kwargs={'level': '3'})
            + '?type=grammar_fill&num_questions=all&status=all'
        )

    def test_grammar_choices_are_shuffled_on_display(self):
        with patch('exams.choice_shuffle.random.shuffle', side_effect=lambda items: items.reverse()):
            response = self.client.get(self._grammar_list_url())

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        correct_pos = content.find('value="%s"' % self.correct.id)
        has_pos = content.find('value="%s"' % self.wrong_choices[0].id)
        self.assertNotEqual(correct_pos, -1)
        self.assertNotEqual(has_pos, -1)
        self.assertGreater(correct_pos, has_pos)

    def test_submit_still_scores_by_choice_id_after_shuffle(self):
        with patch('exams.choice_shuffle.random.shuffle', side_effect=lambda items: items.reverse()):
            self.client.get(self._grammar_list_url())

        response = self.client.post(
            reverse('exams:submit_answers', kwargs={'level': '3'}),
            {
                'question_type': 'grammar_fill',
                'num_questions': 'all',
                'status': 'all',
                f'answer_{self.question.id}': str(self.correct.id),
            },
        )
        self.assertEqual(response.status_code, 302)

        results = self.client.get(
            reverse('exams:answer_results', kwargs={'level': '3', 'question_type': 'grammar_fill'})
        )
        self.assertEqual(results.status_code, 200)
        self.assertContains(results, '正解です！')
        self.assertContains(results, '選択肢:')
        self.assertContains(results, 'have')
        self.assertContains(results, 'has')
        self.assertContains(results, 'having')
        self.assertContains(results, 'had')
        self.assertContains(results, '正解')
        self.assertContains(results, 'あなたの回答')

    def test_listening_illustration_keeps_database_order(self):
        from questions.models import ListeningChoice, ListeningQuestion

        question = ListeningQuestion.objects.create(
            provenance=PROVENANCE_ORIGINAL,
            question_text='Test listening',
            image='images/test.png',
            audio='audio/test.mp3',
            correct_answer='2',
            explanation='',
            level='3',
        )
        choices = [
            ListeningChoice.objects.create(
                question=question, choice_text='1', is_correct=False, order=1
            ),
            ListeningChoice.objects.create(
                question=question, choice_text='2', is_correct=True, order=2
            ),
            ListeningChoice.objects.create(
                question=question, choice_text='3', is_correct=False, order=3
            ),
        ]

        factory = RequestFactory()
        request = factory.get('/')
        request.session = self.client.session

        with patch('exams.choice_shuffle.random.shuffle', side_effect=lambda items: items.reverse()):
            ordered = order_choices_for_display(
                request,
                '3',
                'listening_illustration',
                question.id,
                choices,
            )

        self.assertEqual(
            [choice.choice_text for choice in ordered],
            ['1', '2', '3'],
        )

    def test_apply_choice_shuffle_skips_word_order_items(self):
        question = Question.objects.create(
            provenance=PROVENANCE_ORIGINAL,
            level='3',
            question_type='word_order',
            question_text='並べ替え',
        )
        choices = [
            Choice.objects.create(
                question=question,
                choice_text=f'word-{index}',
                is_correct=index == 1,
                order=index,
            )
            for index in range(1, 5)
        ]
        item = {'question': question, 'choices': choices}
        factory = RequestFactory()
        request = factory.get('/')
        request.session = self.client.session

        with patch('exams.choice_shuffle.random.shuffle', side_effect=lambda items: items.reverse()):
            apply_choice_shuffle_to_items(request, '3', [item])

        self.assertEqual(
            [choice.id for choice in item['choices']],
            [choice.id for choice in choices],
        )

    def test_remap_explanation_choice_numbers_follows_display_order(self):
        question = Question.objects.create(
            provenance=PROVENANCE_ORIGINAL,
            level='4',
            question_type='listening_conversation',
            question_text='Who was sick?',
        )
        choices = [
            Choice.objects.create(
                question=question,
                choice_text=text,
                is_correct=index == 2,
                order=index,
            )
            for index, text in enumerate(
                ['Ken.', "Ken’s mother.", "Ken’s father.", "Ken’s friend."],
                start=1,
            )
        ]
        # Display order: friend, father, mother, Ken (canonical 4,3,2,1)
        display = [choices[3], choices[2], choices[1], choices[0]]
        explanation = (
            '「My mom was sick」とあるので、2「Ken’s mother.」が正解です。\n'
            '1「Ken.」は話者自身ではなく、3「Ken’s father.」は病院へ連れていった人、'
            '4「Ken’s friend.」は会話に出てきません。'
        )
        remapped = remap_explanation_choice_numbers(explanation, display)
        self.assertIn('3「Ken’s mother.」が正解です', remapped)
        self.assertIn('4「Ken.」は話者自身ではなく', remapped)
        self.assertIn('2「Ken’s father.」は病院へ連れていった人', remapped)
        self.assertIn('1「Ken’s friend.」は会話に出てきません', remapped)
        # Do not rewrite multi-digit question numbers inside other contexts
        self.assertEqual(
            remap_explanation_choice_numbers('No.41 is ready. 2が正解です。', display),
            'No.41 is ready. 3が正解です。',
        )

    def test_apply_choice_shuffle_remaps_listening_explanation_numbers(self):
        question = Question.objects.create(
            provenance=PROVENANCE_ORIGINAL,
            level='4',
            question_type='listening_conversation',
            question_text='Where will they meet tomorrow?',
            explanation=(
                '明日は「meet at school」なので、1「At school.」が正解です。\n'
                '3「At the library.」は今日の予定、2・4の家は会話に出てきません。'
            ),
        )
        choices = [
            Choice.objects.create(
                question=question,
                choice_text=text,
                is_correct=index == 1,
                order=index,
            )
            for index, text in enumerate(
                [
                    'At school.',
                    "At the girl’s house.",
                    'At the library.',
                    "At the boy’s house.",
                ],
                start=1,
            )
        ]
        item = {
            'question': question,
            'choices': choices,
            'explanation': question.explanation,
        }
        factory = RequestFactory()
        request = factory.get('/')
        request.session = self.client.session

        with patch('exams.choice_shuffle.random.shuffle', side_effect=lambda items: items.reverse()):
            apply_choice_shuffle_to_items(request, '4', [item])

        # reverse → display: 4,3,2,1 so canonical 1→4, 3→2, 2→3, 4→1
        self.assertIn('4「At school.」が正解です', item['explanation'])
        self.assertIn('2「At the library.」は今日の予定', item['explanation'])
        self.assertIn('3・1の家は会話に出てきません', item['explanation'])


class _Order:
    def __init__(self, order):
        self.order = order


def _reversed_choices():
    """Display order 4,3,2,1 → canonical 1→4, 2→3, 3→2, 4→1."""
    return [_Order(4), _Order(3), _Order(2), _Order(1)]


class ExplanationChoiceNumberRemapTest(TestCase):
    """Choice labels in explanations follow the shuffled 1–4 shown on screen."""

    def test_pre2_conversation_wa_follows_screen_order(self):
        # Screen order from the reported results: source 1,3,4,2.
        display = [_Order(1), _Order(3), _Order(4), _Order(2)]
        explanation = (
            '残りの6個も見える必要があるので、その窓に出します。\n'
            '2 は、塗装中で空いていない会議室です。'
            '3 は、6個までの棚に残りも載せる、です。'
            '4 は、正面ホールに向いている窓を、ホールから見えない場所にするものです。'
        )
        remapped = remap_explanation_choice_numbers(explanation, display)
        self.assertIn('4 は、塗装中で空いていない会議室です。', remapped)
        self.assertIn('2 は、6個までの棚に残りも載せる、です。', remapped)
        self.assertIn('3 は、正面ホールに向いている窓を、ホールから見えない場所にするものです。', remapped)

    def test_pre2_conversation_correct_choice_is_not_described_as_distractor(self):
        # Screen order: source 4,1,2,3. 「1 は」 must not stay on the correct choice.
        display = [_Order(4), _Order(1), _Order(2), _Order(3)]
        explanation = (
            '足りない10枚を刷ります。\n'
            '1 は、1枚を全員で見る、です。1枚では全員に行き渡りません。'
            '2 は、違う種類の地図をコピーする、です。'
            '3 は、コピー機が直るまで待つ、です。'
        )
        remapped = remap_explanation_choice_numbers(explanation, display)
        self.assertIn('2 は、1枚を全員で見る、です。', remapped)
        self.assertIn('1枚では全員に行き渡りません。', remapped)
        self.assertIn('3 は、違う種類の地図をコピーする、です。', remapped)
        self.assertIn('4 は、コピー機が直るまで待つ、です。', remapped)
        self.assertNotIn('1 は、1枚を全員で見る', remapped)

    def test_pre2_grammar_english_label_and_sentence_counter(self):
        explanation = (
            '2文目が、空所の語の意味を決めています。\n'
            '1 suitcase は旅行かばんです。2 receipt はレシートです。'
            'because の中身と合うのは 1 だけです。'
        )
        remapped = remap_explanation_choice_numbers(explanation, _reversed_choices())
        self.assertIn('2文目が、空所の語の意味を決めています。', remapped)
        self.assertIn('4 suitcase は旅行かばんです。', remapped)
        self.assertIn('3 receipt はレシートです。', remapped)
        self.assertIn('合うのは 4 だけです。', remapped)

    def test_pre2_listening_no_to_and_mo(self):
        explanation = (
            '正午・3人で席を予約しています。\n'
            '1 の家で料理する、とは言っていません。2 の eleven は弟の仕事が終わる時刻です。\n'
            '1 は、一人の読書は残ります。3 と 2 は、食事の規則は変えない、と反対です。\n'
            '1 は、放課後の練習用です。3 も体育館のキットで、1時より前の傷はキットです。'
        )
        remapped = remap_explanation_choice_numbers(explanation, _reversed_choices())
        self.assertIn('正午・3人で席を予約しています。', remapped)
        self.assertIn('4 の家で料理する', remapped)
        self.assertIn('3 の eleven は', remapped)
        self.assertIn('4 は、一人の読書は残ります。2 と 3 は、食事の規則は変えない', remapped)
        self.assertIn('4 は、放課後の練習用です。2 も体育館のキットで、1時より前の傷はキットです。', remapped)

    def test_quantities_and_unrelated_digits_stay(self):
        explanation = (
            'June 2 が、いつまでに出すかを決めています。'
            'Number 3 train to the museum.（3番電車）'
            'B の板は1.20メートルです。11歳から14歳。No.41 is ready。'
            '4 は1時間を返す。3 は20枚を手で書き直す。1 は、2年生の絵を飾る。'
            '事務所は1階。辞書は3段目。'
        )
        remapped = remap_explanation_choice_numbers(explanation, _reversed_choices())
        self.assertIn('June 2 が、いつまでに出すか', remapped)
        self.assertIn('Number 3 train', remapped)
        self.assertIn('3番電車', remapped)
        self.assertIn('1.20メートル', remapped)
        self.assertIn('11歳から14歳', remapped)
        self.assertIn('No.41 is ready', remapped)
        self.assertIn('1 は1時間を返す', remapped)
        self.assertIn('2 は20枚を手で書き直す', remapped)
        self.assertIn('4 は、2年生の絵を飾る', remapped)
        self.assertIn('事務所は1階', remapped)
        self.assertIn('辞書は3段目', remapped)

    def test_original_explanations_keep_non_choice_digits(self):
        root = Path(__file__).resolve().parents[1] / 'data' / 'questions' / 'original'
        names = (
            'grammar_fill_questions.txt',
            'conversation_questions.txt',
            'listening_conversation_questions.txt',
            'listening_passage_questions.txt',
        )
        protected = (
            re.compile(r'(?<!\d)[1-4]文目'),
            re.compile(r'(?<!\d)[1-4]時'),
            re.compile(r'(?<!\d)[1-4]階'),
            re.compile(r'(?<!\d)[1-4]人'),
            re.compile(r'(?<!\d)[1-4]枚'),
            re.compile(r'(?<!\d)[1-4]年生'),
            re.compile(r'(?<!\d)[1-4]回'),
            re.compile(r'(?<!\d)[1-4]月'),
            re.compile(r'(?<!\d)[1-4]分'),
            re.compile(r'(?<!\d)[1-4]本'),
            re.compile(r'(?<!\d)[1-4]段'),
            re.compile(r'(?<!\d)[1-4]つ'),
            re.compile(r'(?<!\d)[1-4]羽'),
            re.compile(r'(?<!\d)[1-4]席'),
            re.compile(r'(?<!\d)[1-4]歳'),
            re.compile(r'・[1-4](?!「|の)'),
            re.compile(r'June [1-4]'),
            re.compile(r'Number [1-4] [A-Za-z]'),
            re.compile(r'[1-4]\.[0-9]+'),
            re.compile(r'(?<![0-9])[1-4][0-9]'),
            re.compile(r'No\.[0-9]+'),
        )
        must_change = {
            'levelpre2/grammar_fill_questions.txt',
            'levelpre2/conversation_questions.txt',
            'levelpre2/listening_conversation_questions.txt',
            'levelpre2/listening_passage_questions.txt',
        }
        must_stay = {
            'level5/grammar_fill_questions.txt',
            'level5/conversation_questions.txt',
            'level4/grammar_fill_questions.txt',
            'level3/grammar_fill_questions.txt',
        }
        display = _reversed_choices()
        for level in ('level5', 'level4', 'level3', 'levelpre2'):
            for name in names:
                path = root / level / name
                if not path.exists():
                    continue
                rel = f'{level}/{name}'
                changed = 0
                total = 0
                for explanation in _explanation_bodies(path.read_text(encoding='utf-8')):
                    total += 1
                    remapped = remap_explanation_choice_numbers(explanation, display)
                    before = _token_counts(explanation, protected)
                    after = _token_counts(remapped, protected)
                    self.assertEqual(
                        before,
                        after,
                        f'{rel} rewrote a non-choice digit',
                    )
                    if remapped != explanation:
                        changed += 1
                if rel in must_change:
                    self.assertEqual(changed, total, rel)
                if rel in must_stay:
                    self.assertEqual(changed, 0, rel)


def _explanation_bodies(text):
    bodies = []
    for part in text.split('\n---\n'):
        match = re.search(r'【解説\d+】\n(.*?)(?:\n【ポイント|\Z)', part, re.S)
        if match:
            bodies.append(match.group(1).strip())
    return bodies


def _token_counts(text, patterns):
    counts = Counter()
    for pattern in patterns:
        counts.update(match.group() for match in pattern.finditer(text))
    return counts
