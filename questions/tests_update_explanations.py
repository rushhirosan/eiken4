from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from exams.models import Choice, Question, UserAnswer, UserProgress
from questions.models import (
    ListeningChoice,
    ListeningQuestion,
    ListeningUserAnswer,
    ReadingChoice,
    ReadingPassage,
    ReadingQuestion,
)

User = get_user_model()


class UpdateExplanationsCommandTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='exp_user', password='x')

        self.grammar = Question.objects.create(
            level='4',
            question_type='grammar_fill',
            question_text='old',
            question_number=1,
            explanation='古い文法解説',
        )
        Choice.objects.create(
            question=self.grammar, choice_text='win', is_correct=True, order=4
        )
        UserAnswer.objects.create(
            user=self.user,
            question=self.grammar,
            selected_choice=self.grammar.choices.first(),
            is_correct=True,
        )
        UserProgress.objects.create(
            user=self.user,
            level='4',
            question_type='grammar_fill',
            correct_answers=1,
            total_attempts=1,
        )

        self.lq = ListeningQuestion.objects.create(
            question_text='',
            image='images/part1/listening_illustration_image1.png',
            audio='audio/part1/listening_illustration_question1.mp3',
            correct_answer='1',
            explanation='古いイラスト解説',
            level='4',
        )
        ListeningChoice.objects.create(
            question=self.lq, choice_text='1', is_correct=True, order=1
        )
        ListeningUserAnswer.objects.create(
            user=self.user, question=self.lq, selected_answer='1', is_correct=True
        )

        self.passage = ReadingPassage.objects.create(
            text='Summer Camp',
            level='4',
            identifier='a',
        )
        self.rq = ReadingQuestion.objects.create(
            passage=self.passage,
            question_text='What will students do at the camp?',
            question_number=1,
            explanation='古い読解解説',
        )
        ReadingChoice.objects.create(
            question=self.rq, choice_text='Go fishing.', is_correct=True, order=3
        )

    def test_grammar_fill_updates_without_deleting_answers(self):
        call_command('update_explanations', level='4', category='grammar_fill')
        self.grammar.refresh_from_db()
        self.assertIn('win', self.grammar.explanation)
        self.assertEqual(UserAnswer.objects.filter(user=self.user).count(), 1)
        self.assertEqual(
            UserProgress.objects.filter(
                user=self.user, question_type='grammar_fill'
            ).count(),
            1,
        )
        self.assertEqual(Question.objects.filter(pk=self.grammar.pk).count(), 1)

    def test_listening_category_updates_illustration(self):
        call_command('update_explanations', level='4', category='listening')
        self.lq.refresh_from_db()
        self.assertTrue(self.lq.explanation.startswith('放送文'))
        self.assertEqual(ListeningUserAnswer.objects.filter(user=self.user).count(), 1)

    def test_reading_updates_without_deleting_passage(self):
        call_command(
            'update_explanations', level='4', category='reading_comprehension'
        )
        self.rq.refresh_from_db()
        self.assertIn('go fishing', self.rq.explanation.lower())
        self.assertEqual(ReadingPassage.objects.filter(pk=self.passage.pk).count(), 1)
        self.assertEqual(ReadingQuestion.objects.filter(pk=self.rq.pk).count(), 1)

    def test_listening_wrapper_command(self):
        call_command('update_listening_explanations', level='4')
        self.lq.refresh_from_db()
        self.assertTrue(self.lq.explanation.startswith('放送文'))
