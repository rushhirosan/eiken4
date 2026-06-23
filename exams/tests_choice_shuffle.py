from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from unittest.mock import patch

from exams.choice_shuffle import (
    apply_choice_shuffle_to_items,
    choice_order_session_key,
    order_choices_for_display,
    should_shuffle_choices,
)
from exams.models import Choice, Question
from questions.models import ReadingChoice, ReadingPassage, ReadingQuestion

User = get_user_model()


class ChoiceShuffleHelpersTest(TestCase):
    def test_should_shuffle_targets(self):
        self.assertTrue(should_shuffle_choices('grammar_fill'))
        self.assertTrue(should_shuffle_choices('conversation_fill'))
        self.assertTrue(should_shuffle_choices('listening_illustration'))
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

    def test_listening_illustration_display_index_uses_shuffled_order(self):
        from questions.models import ListeningChoice, ListeningQuestion
        from exams.views import _is_correct_listening_illustration_answer

        question = ListeningQuestion.objects.create(
            question_text='Test listening',
            image='images/test.png',
            audio='audio/test.mp3',
            correct_answer='2',
            explanation='',
            level='3',
        )
        wrong = ListeningChoice.objects.create(
            question=question, choice_text='Wrong', is_correct=False, order=1
        )
        right = ListeningChoice.objects.create(
            question=question, choice_text='Right', is_correct=True, order=2
        )

        session = self.client.session
        session[choice_order_session_key('3')] = {
            str(question.id): [wrong.id, right.id],
        }
        session.save()

        factory = RequestFactory()
        request = factory.get('/')
        request.session = session
        self.assertTrue(
            _is_correct_listening_illustration_answer(
                question, '2', request=request, level='3'
            )
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
