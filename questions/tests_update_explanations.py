from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from exams.models import Choice, Question, UserAnswer, UserProgress
from exams.provenance import PROVENANCE_ORIGINAL
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
            provenance=PROVENANCE_ORIGINAL,
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
            provenance=PROVENANCE_ORIGINAL,
            question_text='',
            image='images/level4/part1/listening_illustration_image1.png',
            audio='audio/level4/part1/listening_illustration_question1.mp3',
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
            provenance=PROVENANCE_ORIGINAL,
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

    def test_listening_illustration_syncs_correct_answer_without_deleting(self):
        q22 = ListeningQuestion.objects.create(
            provenance=PROVENANCE_ORIGINAL,
            question_text='',
            image='images/level4/part1/listening_illustration_image22.png',
            audio='audio/level4/part1/listening_illustration_question22.mp3',
            correct_answer='2',
            explanation='古い解説',
            level='4',
        )
        c1 = ListeningChoice.objects.create(
            question=q22, choice_text='1', is_correct=False, order=1
        )
        c2 = ListeningChoice.objects.create(
            question=q22, choice_text='2', is_correct=True, order=2
        )
        c3 = ListeningChoice.objects.create(
            question=q22, choice_text='3', is_correct=False, order=3
        )
        ListeningUserAnswer.objects.create(
            user=self.user, question=q22, selected_answer='2', is_correct=True
        )

        call_command(
            'update_explanations', level='4', category='listening_illustration'
        )
        q22.refresh_from_db()
        c1.refresh_from_db()
        c2.refresh_from_db()
        c3.refresh_from_db()

        self.assertEqual(q22.correct_answer, '3')
        self.assertIn('You\'re lucky', q22.explanation)
        self.assertFalse(c1.is_correct)
        self.assertFalse(c2.is_correct)
        self.assertTrue(c3.is_correct)
        self.assertEqual(
            ListeningUserAnswer.objects.filter(user=self.user, question=q22).count(),
            1,
        )
        self.assertEqual(ListeningQuestion.objects.filter(pk=q22.pk).count(), 1)

    def test_original_flag_updates_only_original_and_keeps_progress(self):
        """--original は original 行だけを original txt から更新する。"""
        blocked = Question.objects.create(
            provenance='blocked',
            level='4',
            question_type='listening_conversation',
            question_text='blocked old',
            question_number=1,
            explanation='blocked解説のまま',
        )
        original = Question.objects.create(
            provenance=PROVENANCE_ORIGINAL,
            level='4',
            question_type='listening_conversation',
            question_text='original old',
            question_number=1,
            explanation='古いoriginal解説',
        )
        Choice.objects.create(
            question=original, choice_text='To the bookstore.', is_correct=True, order=1
        )
        UserAnswer.objects.create(
            user=self.user,
            question=original,
            selected_choice=original.choices.first(),
            is_correct=True,
        )

        call_command(
            'update_explanations',
            level='4',
            category='listening_conversation',
            original=True,
        )
        blocked.refresh_from_db()
        original.refresh_from_db()

        self.assertEqual(blocked.explanation, 'blocked解説のまま')
        self.assertIn('To the bookstore', original.explanation)
        self.assertIn('To a zoo', original.explanation)
        self.assertEqual(
            UserAnswer.objects.filter(user=self.user, question=original).count(),
            1,
        )
        self.assertEqual(Question.objects.filter(pk=original.pk).count(), 1)
