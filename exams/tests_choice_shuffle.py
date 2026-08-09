from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from unittest.mock import patch

from exams.choice_shuffle import (
    apply_choice_shuffle_to_items,
    choice_order_session_key,
    order_choices_for_display,
    remap_explanation_choice_numbers,
    should_shuffle_choices,
)
from exams.models import Choice, Question
from questions.models import ReadingChoice, ReadingPassage, ReadingQuestion

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

        passage = ReadingPassage.objects.create(level='3', identifier='a', text='本文')
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
