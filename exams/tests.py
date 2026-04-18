from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Question, Choice, UserProgress, UserAnswer, ReadingUserAnswer
from questions.models import (
    ReadingPassage,
    ReadingQuestion,
    ReadingChoice,
    ListeningQuestion,
    ListeningChoice,
    ListeningUserAnswer,
)
from django.utils import timezone

User = get_user_model()


class QuestionModelTest(TestCase):
    """Questionモデルのテスト"""
    
    def setUp(self):
        """テストデータの準備"""
        self.question = Question.objects.create(
            level='4',
            question_type='grammar_fill',
            question_text='テスト問題文',
            explanation='テスト解説'
        )
    
    def test_resolved_audio_file_listening_conversation_fallback(self):
        """audio_file が空でも会話リスニングは規約パスを返す"""
        q = Question.objects.create(
            level='4',
            question_type='listening_conversation',
            question_text='Q1',
            question_number=7,
            audio_file='',
        )
        self.assertEqual(q.resolved_audio_file(), 'audio/part2/listening_conversation_question7.mp3')

    def test_resolved_audio_file_prefers_db_when_set(self):
        """audio_file があればその値を優先する"""
        custom = 'audio/custom/foo.mp3'
        q = Question.objects.create(
            level='4',
            question_type='listening_conversation',
            question_text='Q',
            question_number=1,
            audio_file=custom,
        )
        self.assertEqual(q.resolved_audio_file(), custom)

    def test_resolved_audio_file_strips_whitespace_empty_means_fallback(self):
        """空白のみの audio_file は未設定とみなしてフォールバックする"""
        q = Question.objects.create(
            level='4',
            question_type='listening_passage',
            question_text='P1',
            question_number=3,
            audio_file='   ',
        )
        self.assertEqual(q.resolved_audio_file(), 'audio/part3/listening_passage_question3.mp3')

    def test_resolved_audio_file_listening_illustration_on_question_model(self):
        """共通 Question でイラスト型のとき part1 の規約パスを返す"""
        q = Question.objects.create(
            level='4',
            question_type='listening_illustration',
            question_text='Ill',
            question_number=12,
            audio_file='',
        )
        self.assertEqual(q.resolved_audio_file(), 'audio/part1/listening_illustration_question12.mp3')

    def test_question_creation(self):
        """Questionが正しく作成されるかテスト"""
        self.assertEqual(self.question.level, '4')
        self.assertEqual(self.question.question_type, 'grammar_fill')
        self.assertEqual(self.question.question_text, 'テスト問題文')
        self.assertTrue(isinstance(self.question, Question))
    
    def test_question_str(self):
        """Questionの__str__メソッドのテスト"""
        expected = '文法・語彙問題 - Grade 4'
        self.assertEqual(str(self.question), expected)
    
    def test_question_get_question_type_display(self):
        """問題タイプの表示名を取得できるかテスト"""
        self.assertEqual(self.question.get_question_type_display(), '文法・語彙問題')


class ChoiceModelTest(TestCase):
    """Choiceモデルのテスト"""
    
    def setUp(self):
        """テストデータの準備"""
        self.question = Question.objects.create(
            level='4',
            question_type='grammar_fill',
            question_text='テスト問題'
        )
        self.choice = Choice.objects.create(
            question=self.question,
            choice_text='選択肢1',
            is_correct=True,
            order=1
        )
    
    def test_choice_creation(self):
        """Choiceが正しく作成されるかテスト"""
        self.assertEqual(self.choice.choice_text, '選択肢1')
        self.assertTrue(self.choice.is_correct)
        self.assertEqual(self.choice.question, self.question)
    
    def test_choice_str(self):
        """Choiceの__str__メソッドのテスト"""
        self.assertIn('選択肢1', str(self.choice))


class UserProgressModelTest(TestCase):
    """UserProgressモデルのテスト"""
    
    def setUp(self):
        """テストデータの準備"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.progress = UserProgress.objects.create(
            user=self.user,
            level='4',
            question_type='grammar_fill',
            total_attempts=10,
            correct_answers=8
        )
    
    def test_progress_creation(self):
        """UserProgressが正しく作成されるかテスト"""
        self.assertEqual(self.progress.user, self.user)
        self.assertEqual(self.progress.level, '4')
        self.assertEqual(self.progress.total_attempts, 10)
        self.assertEqual(self.progress.correct_answers, 8)
        self.assertEqual(self.progress.accuracy_rate, 80.0)
    
    def test_progress_accuracy_calculation(self):
        """正答率の計算が正しいかテスト"""
        expected_accuracy = (8 / 10) * 100
        self.assertEqual(self.progress.accuracy_rate, expected_accuracy)


class ExamListViewTest(TestCase):
    """試験一覧ビューのテスト"""
    
    def setUp(self):
        """テストデータの準備"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.url = reverse('exams:exam_list')
    
    def test_exam_list_view_requires_login(self):
        """試験一覧ページがログイン必須かテスト"""
        response = self.client.get(self.url)
        # ログイン必須なのでリダイレクト
        self.assertEqual(response.status_code, 302)
    
    def test_exam_list_view_accessible(self):
        """ログイン後の試験一覧ページにアクセスできるかテスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exams/exam_list.html')
    
    def test_exam_list_view_contains_title(self):
        """試験一覧ページにタイトルが含まれているかテスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertContains(response, '英検試験対策')


class ProgressViewTest(TestCase):
    """進捗ページビューのテスト"""
    
    def setUp(self):
        """テストデータの準備"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.url = reverse('exams:progress')
    
    def test_progress_view_requires_login(self):
        """進捗ページがログイン必須かテスト"""
        response = self.client.get(self.url)
        # リダイレクトされる（ログインページへ）
        self.assertEqual(response.status_code, 302)
    
    def test_progress_view_with_login(self):
        """ログイン後の進捗ページアクセステスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exams/progress.html')


class UserAnswerModelTest(TestCase):
    """UserAnswerモデルのテスト"""
    
    def setUp(self):
        """テストデータの準備"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.question = Question.objects.create(
            level='4',
            question_type='grammar_fill',
            question_text='テスト問題'
        )
        self.choice = Choice.objects.create(
            question=self.question,
            choice_text='選択肢1',
            is_correct=True
        )
        self.user_answer = UserAnswer.objects.create(
            user=self.user,
            question=self.question,
            selected_choice=self.choice,
            is_correct=True,
            answered_at=timezone.now()
        )
    
    def test_user_answer_creation(self):
        """UserAnswerが正しく作成されるかテスト"""
        self.assertEqual(self.user_answer.user, self.user)
        self.assertEqual(self.user_answer.question, self.question)
        self.assertEqual(self.user_answer.selected_choice, self.choice)
        self.assertTrue(self.user_answer.is_correct)
        self.assertIsNotNone(self.user_answer.answered_at)
    
    def test_user_answer_str(self):
        """UserAnswerの__str__メソッドのテスト"""
        self.assertIn('testuser', str(self.user_answer))
        self.assertIn('選択肢1', str(self.user_answer))


class QuestionListViewTest(TestCase):
    """問題一覧ビューのテスト"""
    
    def setUp(self):
        """テストデータの準備"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.question = Question.objects.create(
            level='4',
            question_type='grammar_fill',
            question_text='テスト問題'
        )
    
    def test_question_list_requires_login(self):
        """問題一覧ページがログイン必須かテスト"""
        url = reverse('exams:question_list_by_level', kwargs={'level': '4'})
        response = self.client.get(url)
        # リダイレクトされる
        self.assertEqual(response.status_code, 302)
    
    def test_question_list_with_login(self):
        """ログイン後の問題一覧ページアクセステスト"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('exams:question_list_by_level', kwargs={'level': '4'})
        response = self.client.get(url + '?type=grammar_fill')
        self.assertEqual(response.status_code, 200)


class ReadingComprehensionBehaviorTest(TestCase):
    """長文読解のフィルターと進捗のテスト"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='reading_user',
            email='reading@example.com',
            password='testpass123'
        )
        self.client.login(username='reading_user', password='testpass123')

        # progress_view の level 一覧は Question モデル由来のため、最低1件作成しておく
        Question.objects.create(level='4', question_type='grammar_fill', question_text='dummy')

        self.passage_a = ReadingPassage.objects.create(level='4', identifier='a', text='本文A')
        self.passage_b = ReadingPassage.objects.create(level='4', identifier='b', text='本文B')

        self.a_q1 = ReadingQuestion.objects.create(passage=self.passage_a, question_text='A-1', question_number=1)
        self.a_q2 = ReadingQuestion.objects.create(passage=self.passage_a, question_text='A-2', question_number=2)
        self.b_q1 = ReadingQuestion.objects.create(passage=self.passage_b, question_text='B-1', question_number=1)
        self.b_q2 = ReadingQuestion.objects.create(passage=self.passage_b, question_text='B-2', question_number=2)

        self.a_q1_correct = ReadingChoice.objects.create(question=self.a_q1, choice_text='A1正解', is_correct=True, order=1)
        self.a_q2_correct = ReadingChoice.objects.create(question=self.a_q2, choice_text='A2正解', is_correct=True, order=1)
        self.b_q1_correct = ReadingChoice.objects.create(question=self.b_q1, choice_text='B1正解', is_correct=True, order=1)
        self.b_q2_correct = ReadingChoice.objects.create(question=self.b_q2, choice_text='B2正解', is_correct=True, order=1)

        self.a_q1_wrong = ReadingChoice.objects.create(question=self.a_q1, choice_text='A1誤答', is_correct=False, order=2)
        self.a_q2_wrong = ReadingChoice.objects.create(question=self.a_q2, choice_text='A2誤答', is_correct=False, order=2)
        self.b_q1_wrong = ReadingChoice.objects.create(question=self.b_q1, choice_text='B1誤答', is_correct=False, order=2)
        self.b_q2_wrong = ReadingChoice.objects.create(question=self.b_q2, choice_text='B2誤答', is_correct=False, order=2)

    def test_reading_correct_filter_returns_only_all_correct_passages(self):
        ReadingUserAnswer.objects.create(
            user=self.user,
            reading_question=self.a_q1,
            selected_reading_choice=self.a_q1_correct,
            is_correct=True,
            answered_at=timezone.now(),
        )
        ReadingUserAnswer.objects.create(
            user=self.user,
            reading_question=self.a_q2,
            selected_reading_choice=self.a_q2_correct,
            is_correct=True,
            answered_at=timezone.now(),
        )
        ReadingUserAnswer.objects.create(
            user=self.user,
            reading_question=self.b_q1,
            selected_reading_choice=self.b_q1_correct,
            is_correct=True,
            answered_at=timezone.now(),
        )
        ReadingUserAnswer.objects.create(
            user=self.user,
            reading_question=self.b_q2,
            selected_reading_choice=self.b_q2_wrong,
            is_correct=False,
            answered_at=timezone.now(),
        )

        url = reverse('exams:question_list_by_level', kwargs={'level': '4'})
        response = self.client.get(url, {'type': 'reading_comprehension', 'status': 'correct'})

        self.assertEqual(response.status_code, 200)
        passages = response.context['passages']
        self.assertEqual(len(passages), 1)
        self.assertEqual(passages[0]['passage'].id, self.passage_a.id)

    def test_reading_progress_counts_completed_passages(self):
        ReadingUserAnswer.objects.create(
            user=self.user,
            reading_question=self.a_q1,
            selected_reading_choice=self.a_q1_correct,
            is_correct=True,
            answered_at=timezone.now(),
        )
        ReadingUserAnswer.objects.create(
            user=self.user,
            reading_question=self.a_q2,
            selected_reading_choice=self.a_q2_correct,
            is_correct=True,
            answered_at=timezone.now(),
        )
        # 本文Bは未完了（1問のみ回答）
        ReadingUserAnswer.objects.create(
            user=self.user,
            reading_question=self.b_q1,
            selected_reading_choice=self.b_q1_correct,
            is_correct=True,
            answered_at=timezone.now(),
        )

        response = self.client.get(reverse('exams:progress'))
        self.assertEqual(response.status_code, 200)

        reading_progress = response.context['progress_data']['4']['reading_comprehension']
        self.assertEqual(reading_progress['answered_questions'], 1)
        self.assertEqual(reading_progress['total_questions'], 2)


class ListeningIllustrationScoringTest(TestCase):
    """リスニング第1部の採点ロジックのテスト"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='listening_user',
            email='listening@example.com',
            password='testpass123'
        )
        self.client.login(username='listening_user', password='testpass123')

        self.question = ListeningQuestion.objects.create(
            question_text='Do you have apple juice?',
            image='images/test.png',
            audio='audio/test.mp3',
            correct_answer='1',
            explanation='テスト解説',
            level='4'
        )
        self.choice1 = ListeningChoice.objects.create(
            question=self.question,
            choice_text='Sorry, we only have orange juice.',
            is_correct=True,
            order=1
        )
        self.choice2 = ListeningChoice.objects.create(
            question=self.question,
            choice_text='Yes, I can play soccer.',
            is_correct=False,
            order=2
        )

    def test_submit_answers_scores_by_choice_text_value(self):
        """フォーム値が choice_text の場合でも正しく採点される"""
        response = self.client.post(
            reverse('exams:submit_answers', kwargs={'level': '4'}),
            {
                'question_type': 'listening_illustration',
                'num_questions': '5',
                f'answer_{self.question.id}': self.choice1.choice_text,
            }
        )

        self.assertEqual(response.status_code, 302)
        saved = ListeningUserAnswer.objects.get(user=self.user, question=self.question)
        self.assertEqual(saved.selected_answer, self.choice1.choice_text)
        self.assertTrue(saved.is_correct)

    def test_submit_answers_scores_by_display_index_even_when_order_is_non_sequential(self):
        """表示番号(1,2,3)が送信されても正しく採点される"""
        question = ListeningQuestion.objects.create(
            question_text='Where are you going?',
            image='images/test2.png',
            audio='audio/test2.mp3',
            correct_answer='2',
            explanation='テスト解説2',
            level='4'
        )
        ListeningChoice.objects.create(
            question=question,
            choice_text='To the library.',
            is_correct=False,
            order=10
        )
        ListeningChoice.objects.create(
            question=question,
            choice_text='To the station.',
            is_correct=True,
            order=20
        )
        ListeningChoice.objects.create(
            question=question,
            choice_text='To my school.',
            is_correct=False,
            order=30
        )

        response = self.client.post(
            reverse('exams:submit_answers', kwargs={'level': '4'}),
            {
                'question_type': 'listening_illustration',
                'num_questions': 'all',
                f'answer_{question.id}': '2',
            }
        )

        self.assertEqual(response.status_code, 302)
        saved = ListeningUserAnswer.objects.get(user=self.user, question=question)
        self.assertTrue(saved.is_correct)

    def test_listening_illustration_unanswered_filter_excludes_answered_questions(self):
        """未回答フィルターで回答済み問題が再出題されない"""
        unanswered_question = ListeningQuestion.objects.create(
            question_text='How is the weather?',
            image='images/test3.png',
            audio='audio/test3.mp3',
            correct_answer='1',
            explanation='テスト解説3',
            level='4'
        )
        ListeningChoice.objects.create(question=unanswered_question, choice_text='Sunny.', is_correct=True, order=1)
        ListeningChoice.objects.create(question=unanswered_question, choice_text='Monday.', is_correct=False, order=2)
        ListeningChoice.objects.create(question=unanswered_question, choice_text='At home.', is_correct=False, order=3)

        ListeningUserAnswer.objects.create(
            user=self.user,
            question=self.question,
            selected_answer=self.choice1.choice_text,
            is_correct=True,
            answered_at=timezone.now(),
        )

        response = self.client.get(
            reverse('exams:question_list_by_level', kwargs={'level': '4'}),
            {
                'type': 'listening_illustration',
                'status': 'unanswered',
                'num_questions': 'all',
            }
        )

        self.assertEqual(response.status_code, 200)
        displayed_question_ids = [item['question'].id for item in response.context['questions']]
        self.assertNotIn(self.question.id, displayed_question_ids)
        self.assertIn(unanswered_question.id, displayed_question_ids)
