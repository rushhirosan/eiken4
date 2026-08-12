"""provenance=blocked の問題は公開面に出ないことの確認。"""

from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import CustomUser
from exams.models import Choice, Question
from exams.provenance import PROVENANCE_BLOCKED, PROVENANCE_ORIGINAL
from questions.models import ListeningQuestion, ReadingPassage, ReadingQuestion


class ProvenancePublicZeroTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='prov_user', password='testpass123'
        )
        self.blocked = Question.objects.create(
            level='5',
            question_type='grammar_fill',
            question_text='Blocked grammar (official-derived)',
            question_number=1,
            provenance=PROVENANCE_BLOCKED,
        )
        Choice.objects.create(
            question=self.blocked, choice_text='a', is_correct=True, order=1
        )
        Choice.objects.create(
            question=self.blocked, choice_text='b', is_correct=False, order=2
        )
        ListeningQuestion.objects.create(
            question_text='Blocked listening',
            image='images/x.png',
            audio='audio/x.mp3',
            correct_answer='1',
            level='5',
            provenance=PROVENANCE_BLOCKED,
        )
        passage = ReadingPassage.objects.create(
            text='Blocked passage',
            level='4',
            identifier='a',
            provenance=PROVENANCE_BLOCKED,
        )
        ReadingQuestion.objects.create(
            passage=passage, question_text='Blocked RQ', question_number=1
        )

    def test_published_manager_excludes_blocked(self):
        self.assertEqual(Question.objects.published().count(), 0)
        self.assertEqual(Question.objects.filter(provenance=PROVENANCE_BLOCKED).count(), 1)
        self.assertEqual(ListeningQuestion.objects.published().count(), 0)
        self.assertEqual(ReadingPassage.objects.published().count(), 0)

    def test_try_level_has_no_samples_when_all_blocked(self):
        response = Client().get(reverse('try_level', kwargs={'level': '5'}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['show_form'])
        self.assertEqual(list(response.context['samples']), [])

    def test_grammar_list_empty_when_blocked(self):
        self.client.login(username='prov_user', password='testpass123')
        response = self.client.get(
            reverse('exams:question_list_by_level', kwargs={'level': '5'}),
            {'type': 'grammar_fill', 'status': 'unanswered', 'num_questions': 'all'},
        )
        self.assertEqual(response.status_code, 200)
        questions = response.context.get('questions') or []
        self.assertEqual(len(questions), 0)

    def test_original_appears_on_try_level(self):
        original = Question.objects.create(
            level='5',
            question_type='grammar_fill',
            question_text='Original practice item',
            question_number=2,
            provenance=PROVENANCE_ORIGINAL,
        )
        Choice.objects.create(
            question=original, choice_text='yes', is_correct=True, order=1
        )
        Choice.objects.create(
            question=original, choice_text='no', is_correct=False, order=2
        )
        response = Client().get(reverse('try_level', kwargs={'level': '5'}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_form'])
        self.assertEqual(len(response.context['samples']), 1)
        self.assertIn('Original practice item', response.context['samples'][0].question_text)
