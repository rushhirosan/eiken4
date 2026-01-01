from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Question, Choice, UserProgress, UserAnswer
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
