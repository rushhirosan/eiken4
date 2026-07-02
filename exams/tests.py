from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from unittest.mock import patch
from datetime import timedelta

from .models import (
    Question,
    Choice,
    UserProgress,
    UserAnswer,
    ReadingUserAnswer,
    Feedback,
    UserStreak,
    UserBadge,
)
from .forms import FeedbackForm, FEEDBACK_CONTENT_MAX_LENGTH
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

    def test_exam_list_defaults_to_level_4(self):
        """初回は4級にフォーカスする"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertContains(response, '現在の試験級')
        self.assertContains(response, '英検4級')
        self.assertContains(response, '英検3級に切り替える')
        self.assertNotContains(response, 'exam-level-tab')
        self.assertContains(response, '長文は別メニュー')
        self.assertNotContains(response, 'ライティングは別メニュー')

    def test_exam_list_level_query_switches_focus(self):
        """?level= で級を切り替え、セッションに保存する"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url, {'level': '3'})
        self.assertContains(response, 'id="level-panel-3"')
        self.assertContains(response, '英検4級に切り替える')
        self.assertContains(response, 'ライティング問題')
        self.assertContains(response, '長文・ライティングは別メニュー')
        self.assertEqual(self.client.session.get('preferred_exam_level'), '3')

        response = self.client.get(self.url)
        self.assertContains(response, 'id="level-panel-3"')
        self.assertContains(response, 'ライティング問題')
        self.assertNotContains(response, 'type=word_order')

    def test_exam_list_shows_daily_missions(self):
        """問題一覧に今日のミッションカードが表示される"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertContains(response, '今日のミッション')
        self.assertContains(response, '今日3問解く')

    def test_exam_list_daily_goal_query_updates_session(self):
        """daily_goal クエリで目標問題数を級別セッションに保存する"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url, {'daily_goal': '10'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get('daily_mission_goal_4'), 10)
        self.assertContains(response, '今日10問解く')

    def test_exam_list_daily_goal_is_scoped_per_level(self):
        """級ごとにミッション目標を保持する"""
        self.client.login(username='testuser', password='testpass123')
        self.client.get(self.url, {'level': '4', 'daily_goal': '10'})
        self.client.get(self.url, {'level': '3', 'daily_goal': '5'})
        session = self.client.session
        self.assertEqual(session.get('daily_mission_goal_4'), 10)
        self.assertEqual(session.get('daily_mission_goal_3'), 5)

        response = self.client.get(self.url, {'level': '3'})
        self.assertContains(response, '今日5問解く')
        response = self.client.get(self.url, {'level': '4'})
        self.assertContains(response, '今日10問解く')

    def test_exam_list_shows_habit_status(self):
        """問題一覧にストリークとバッジ数のコンパクト表示がある"""
        UserStreak.objects.create(
            user=self.user,
            current_streak=4,
            longest_streak=4,
            last_active_date=timezone.localdate(),
        )
        UserBadge.objects.create(user=self.user, badge_id='first_reading')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertContains(response, '4日')
        self.assertContains(response, '集めたバッジ 1個')
        self.assertContains(response, 'badgeCollectionModal')
        self.assertContains(response, 'exam-habit-streak-btn')
        self.assertContains(response, '1日1問で連続記録')

    def test_exam_list_shows_grace_notice_during_streak_grace(self):
        """1日お休みした翌々日は維持チャンスの案内を表示する"""
        UserStreak.objects.create(
            user=self.user,
            current_streak=7,
            longest_streak=7,
            last_active_date=timezone.localdate() - timedelta(days=2),
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertContains(response, '今週の維持チャンスが残り1回')
        self.assertContains(response, '7日連続をキープ')

    def test_exam_list_badge_modal_shows_unlock_hint_for_unearned(self):
        """未獲得バッジにも獲得条件を表示する"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertContains(response, '累計50問に到達した')
        self.assertContains(response, 'まだ獲得していません')

    def test_question_list_sets_preferred_level(self):
        """問題一覧に入ると選択中の級がセッションに保存される"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('exams:question_list_by_level', kwargs={'level': '3'})
        self.client.get(url, {'type': 'grammar_fill'})
        self.assertEqual(self.client.session.get('preferred_exam_level'), '3')

        response = self.client.get(self.url)
        self.assertContains(response, '英検3級')


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

    def test_progress_level3_hides_word_order(self):
        """3級の進捗表示に語順選択問題を含めない"""
        self.client.login(username='testuser', password='testpass123')
        Question.objects.create(
            level='3',
            question_type='grammar_fill',
            question_text='3級テスト',
        )
        response = self.client.get(self.url)
        self.assertContains(response, '英検3級')
        self.assertNotContains(response, '<td>語順選択問題</td>')
        self.assertNotContains(response, '<i class="fas fa-sort me-2"></i>語順選択問題')

    def test_clear_progress_only_clears_requested_level(self):
        """進捗クリアは指定級のみ削除し、他級とリスニング回答は残さない/残す"""
        self.client.login(username='testuser', password='testpass123')
        q4 = Question.objects.create(
            level='4',
            question_type='grammar_fill',
            question_text='4級',
        )
        q3 = Question.objects.create(
            level='3',
            question_type='grammar_fill',
            question_text='3級',
        )
        choice = Choice.objects.create(
            question=q4,
            choice_text='A',
            is_correct=True,
            order=1,
        )
        UserProgress.objects.create(
            user=self.user,
            level='4',
            question_type='grammar_fill',
            total_attempts=1,
            correct_answers=1,
        )
        UserProgress.objects.create(
            user=self.user,
            level='3',
            question_type='grammar_fill',
            total_attempts=2,
            correct_answers=1,
        )
        UserAnswer.objects.create(
            user=self.user,
            question=q4,
            selected_choice=choice,
            is_correct=True,
        )
        UserAnswer.objects.create(
            user=self.user,
            question=q3,
            selected_choice=Choice.objects.create(
                question=q3,
                choice_text='B',
                is_correct=True,
                order=1,
            ),
            is_correct=True,
        )
        listening_q3 = ListeningQuestion.objects.create(
            question_text='Level3 listening',
            image='images/l3.png',
            audio='audio/l3.mp3',
            correct_answer='1',
            explanation='',
            level='3',
        )
        ListeningUserAnswer.objects.create(
            user=self.user,
            question=listening_q3,
            selected_answer='1',
            is_correct=True,
        )

        response = self.client.post(
            reverse('exams:clear_progress'),
            {'level': '3'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            UserProgress.objects.filter(user=self.user, level='3').exists()
        )
        self.assertTrue(
            UserProgress.objects.filter(user=self.user, level='4').exists()
        )
        self.assertFalse(
            UserAnswer.objects.filter(user=self.user, question__level='3').exists()
        )
        self.assertTrue(
            UserAnswer.objects.filter(user=self.user, question__level='4').exists()
        )
        self.assertFalse(
            ListeningUserAnswer.objects.filter(
                user=self.user,
                question__level='3',
            ).exists()
        )

        follow = self.client.get(response.url)
        self.assertContains(follow, '英検3級の学習進捗をクリアしました')

    def test_clear_progress_rejects_invalid_level(self):
        """不正な級指定では進捗を削除しない"""
        self.client.login(username='testuser', password='testpass123')
        Question.objects.create(
            level='4',
            question_type='grammar_fill',
            question_text='4級',
        )
        UserProgress.objects.create(
            user=self.user,
            level='4',
            question_type='grammar_fill',
            total_attempts=1,
            correct_answers=1,
        )

        response = self.client.post(
            reverse('exams:clear_progress'),
            {'level': '99'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            UserProgress.objects.filter(user=self.user, level='4').exists()
        )


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


class EmptySubmissionTest(TestCase):
    """問題0件のまま回答提出できないことのテスト"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='empty_submit_user',
            email='empty@example.com',
            password='testpass123',
        )
        self.client.login(username='empty_submit_user', password='testpass123')

        self.question = Question.objects.create(
            level='4',
            question_type='conversation_fill',
            question_text='A: Hello.\nB: (  )',
            question_number=1,
        )
        self.choice = Choice.objects.create(
            question=self.question,
            choice_text='Hi.',
            is_correct=True,
            order=1,
        )
        UserAnswer.objects.create(
            user=self.user,
            question=self.question,
            selected_choice=self.choice,
            is_correct=True,
            answered_at=timezone.now(),
        )

    def test_unanswered_filter_shows_no_questions_when_all_answered(self):
        response = self.client.get(
            reverse('exams:question_list_by_level', kwargs={'level': '4'}),
            {
                'type': 'conversation_fill',
                'status': 'unanswered',
                'num_questions': '5',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['questions']), 0)

    def test_submit_without_answers_redirects_to_question_list(self):
        response = self.client.post(
            reverse('exams:submit_answers', kwargs={'level': '4'}),
            {
                'question_type': 'conversation_fill',
                'num_questions': '5',
                'status': 'unanswered',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('type=conversation_fill', response.url)
        self.assertNotIn('answer_results', response.url)

    def test_submit_without_answers_does_not_create_session_results(self):
        self.client.post(
            reverse('exams:submit_answers', kwargs={'level': '4'}),
            {
                'question_type': 'conversation_fill',
                'num_questions': '5',
                'status': 'unanswered',
            },
        )
        session = self.client.session
        self.assertNotIn('answered_questions_conversation_fill_4', session)


class FeedbackFormTest(TestCase):
    """フィードバックフォームのバリデーション"""

    def test_content_max_length(self):
        form = FeedbackForm(data={
            'feedback_type': 'bug',
            'title': 'タイトル',
            'content': 'x' * (FEEDBACK_CONTENT_MAX_LENGTH + 1),
            'email': '',
            'website': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_honeypot_rejects_submission(self):
        form = FeedbackForm(data={
            'feedback_type': 'bug',
            'title': 'タイトル',
            'content': '内容',
            'email': '',
            'website': 'http://spam.example/',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('website', form.errors)


@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
)
class FeedbackViewTest(TestCase):
    """フィードバック送信ビュー"""

    def setUp(self):
        cache.clear()
        self.client = Client()
        self.user = User.objects.create_user(username='feedback_user', password='testpass123')
        self.client.login(username='feedback_user', password='testpass123')
        self.url = reverse('exams:feedback_form')
        self.payload = {
            'feedback_type': 'bug',
            'title': 'テスト',
            'content': 'テスト内容',
            'email': '',
            'website': '',
        }

    def test_submit_success(self):
        response = self.client.post(self.url, self.payload)
        self.assertRedirects(response, reverse('exams:feedback_success'))
        self.assertEqual(Feedback.objects.filter(user=self.user).count(), 1)

    @patch('exams.views.get_client_ip', return_value='127.0.0.1')
    def test_rate_limit_blocks_excess_submissions(self, _mock_ip):
        for _ in range(5):
            response = self.client.post(self.url, self.payload)
            self.assertEqual(response.status_code, 302)

        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Feedback.objects.filter(user=self.user).count(), 5)
        messages = list(response.context['messages'])
        self.assertTrue(any('上限' in str(m) for m in messages))


class WritingPromptHtmlFilterTest(TestCase):
    """writing_prompt_html テンプレートフィルター"""

    def test_underline_preserved_and_script_escaped(self):
        from exams.templatetags.custom_filters import writing_prompt_html

        html = writing_prompt_html('A <u>B</u> C <script>x</script>')
        self.assertIn('writing-q-underline', html)
        self.assertIn('>B</span>', html)
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_unclosed_u_is_closed(self):
        from exams.templatetags.custom_filters import writing_prompt_html

        html = writing_prompt_html('<u>open')
        compact = html.replace('\n', '')
        self.assertIn('writing-q-underline', compact)
        self.assertIn('>open</span>', compact)


class GamificationTest(TestCase):
    """Gamification helper tests."""

    def test_build_session_achievements_perfect_score(self):
        from exams.gamification import build_session_achievements

        unlock_status = {
            'random': {'is_unlocked': False},
            'mock_exam': {'is_unlocked': False, 'remaining_categories': []},
        }
        messages = build_session_achievements(
            user=None,
            level='4',
            question_type='grammar_fill',
            correct_count=5,
            total_count=5,
            unlock_status=unlock_status,
            session_count=5,
        )
        self.assertTrue(any('ぜんぶ正解' in m['text'] for m in messages))
        self.assertLessEqual(len(messages), 3)

    def test_build_session_achievements_low_score_still_encourages(self):
        from exams.gamification import ACHIEVEMENT_COPY, build_session_achievements

        unlock_status = {
            'random': {'is_unlocked': False},
            'mock_exam': {'is_unlocked': False, 'remaining_categories': []},
        }
        messages = build_session_achievements(
            user=None,
            level='4',
            question_type='grammar_fill',
            correct_count=1,
            total_count=5,
            unlock_status=unlock_status,
            session_count=5,
        )
        self.assertTrue(
            any(ACHIEVEMENT_COPY['score_low'] in m['text'] for m in messages)
        )

    def test_build_session_achievements_unlock_random(self):
        from exams.gamification import build_session_achievements

        unlock_status = {
            'random': {'is_unlocked': True},
            'mock_exam': {'is_unlocked': False, 'remaining_categories': []},
        }
        messages = build_session_achievements(
            user=None,
            level='4',
            question_type='grammar_fill',
            correct_count=2,
            total_count=5,
            unlock_status=unlock_status,
            pre_unlock={'random': False, 'mock_exam': False},
            session_count=5,
        )
        self.assertTrue(any('ランダム10問' in m['text'] for m in messages))
        self.assertTrue(any('長文は別メニュー' in m['text'] for m in messages))

    def test_random_scope_description_by_level(self):
        from exams.gamification import random_scope_description, random_unlock_help_text

        self.assertIn('語順', random_scope_description('4'))
        self.assertIn('長文は別メニュー', random_scope_description('4'))
        self.assertNotIn('ライティング', random_scope_description('4'))
        self.assertIn('長文・ライティングは別メニュー', random_scope_description('3'))
        self.assertNotIn('読解・リスニング', random_unlock_help_text())

    def test_build_adventure_summary(self):
        from exams.gamification import build_adventure_summary

        unlock_status = {
            'random': {
                'is_unlocked': False,
                'ready_count': 1,
                'required_count': 3,
                'required_rate': 20,
            },
            'mock_exam': {
                'is_unlocked': False,
                'required_rate': 80,
                'remaining_categories': [
                    {
                        'display_name': '文法・語彙問題',
                        'remaining_rate': 37,
                        'progress_rate': 43,
                    }
                ],
            },
            'foundation_progress': [
                {'question_type': 'grammar_fill', 'progress_rate': 43},
            ],
        }
        summary = build_adventure_summary(unlock_status)
        self.assertFalse(summary['random_unlocked'])
        self.assertEqual(summary['random_ready_count'], 1)
        self.assertEqual(summary['nearest_remaining']['display_name'], '文法・語彙問題')

    def test_enrich_foundation_progress(self):
        from exams.gamification import enrich_foundation_progress

        enriched = enrich_foundation_progress([
            {'question_type': 'grammar_fill', 'progress_rate': 43, 'display_name': '文法'},
        ])
        self.assertEqual(enriched[0]['remaining_to_mock'], 37)
        self.assertTrue(enriched[0]['meets_random_threshold'])

    def test_enrich_foundation_progress_writing_excluded_from_mock(self):
        from exams.gamification import enrich_foundation_progress

        enriched = enrich_foundation_progress([
            {
                'question_type': 'writing',
                'progress_rate': 0,
                'display_name': 'ライティング',
                'counts_toward_mock': False,
            },
        ])
        self.assertIsNone(enriched[0]['remaining_to_mock'])
        self.assertFalse(enriched[0]['counts_toward_mock'])

    def test_build_daily_missions_includes_daily_goal_and_categories(self):
        from exams.gamification import build_daily_missions

        unlock_status = {
            'mock_exam': {
                'is_unlocked': False,
                'remaining_categories': [
                    {
                        'question_type': 'grammar_fill',
                        'display_name': '文法・語彙問題',
                        'remaining_rate': 80,
                        'progress_rate': 0,
                        'total_questions': 100,
                    },
                    {
                        'question_type': 'conversation_fill',
                        'display_name': '会話補充問題',
                        'remaining_rate': 80,
                        'progress_rate': 0,
                        'total_questions': 50,
                    },
                ],
            },
        }
        foundation_progress_by_type = {
            'grammar_fill': {'question_type': 'grammar_fill', 'display_name': '文法・語彙問題'},
            'conversation_fill': {'question_type': 'conversation_fill', 'display_name': '会話補充問題'},
        }
        missions = build_daily_missions(
            user=None,
            level='4',
            unlock_status=unlock_status,
            foundation_progress_by_type=foundation_progress_by_type,
            daily_goal=3,
        )
        self.assertEqual(missions['daily_goal'], 3)
        self.assertEqual(missions['daily_goal_options'], [3, 5, 10])
        self.assertFalse(missions['all_complete'])
        self.assertEqual(missions['items'][0]['label'], '今日3問解く')
        self.assertEqual(missions['items'][0]['progress_text'], '0/3')
        self.assertEqual(missions['items'][1]['label'], '文法・語彙問題を進めよう')
        self.assertIn('模擬まで', missions['items'][1]['progress_text'])
        self.assertIn('grammar_fill', missions['items'][1]['url'])
        self.assertEqual(missions['items'][2]['label'], '会話補充を3問')
        self.assertEqual(missions['items'][2]['progress_text'], '0/3')

    def test_normalize_daily_mission_goal_defaults_invalid(self):
        from exams.gamification import normalize_daily_mission_goal

        self.assertEqual(normalize_daily_mission_goal(5), 5)
        self.assertEqual(normalize_daily_mission_goal('10'), 10)
        self.assertEqual(normalize_daily_mission_goal(7), 3)
        self.assertEqual(normalize_daily_mission_goal(None), 3)

    def test_record_streak_activity_increments_on_consecutive_day(self):
        from exams.gamification import record_streak_activity

        user = User.objects.create_user(username='streakuser', password='pass')
        yesterday = timezone.localdate() - timedelta(days=1)
        UserStreak.objects.create(
            user=user,
            current_streak=2,
            longest_streak=2,
            last_active_date=yesterday,
        )
        streak, incremented = record_streak_activity(user)
        self.assertTrue(incremented)
        self.assertEqual(streak.current_streak, 3)
        self.assertEqual(streak.last_active_date, timezone.localdate())

        _, incremented_again = record_streak_activity(user)
        self.assertFalse(incremented_again)

    def test_record_streak_activity_uses_weekly_freeze_once(self):
        from exams.gamification import record_streak_activity

        user = User.objects.create_user(username='freezeuser', password='pass')
        two_days_ago = timezone.localdate() - timedelta(days=2)
        UserStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=5,
            last_active_date=two_days_ago,
        )
        streak, incremented = record_streak_activity(user)
        self.assertTrue(incremented)
        self.assertEqual(streak.current_streak, 6)
        self.assertIsNotNone(streak.freeze_week_start)

    def test_build_session_achievements_shows_streak_on_first_session_today(self):
        from exams.gamification import build_session_achievements

        unlock_status = {
            'random': {'is_unlocked': False},
            'mock_exam': {'is_unlocked': False, 'remaining_categories': []},
        }
        messages = build_session_achievements(
            user=None,
            level='4',
            question_type='grammar_fill',
            correct_count=2,
            total_count=3,
            unlock_status=unlock_status,
            session_count=3,
            streak_incremented=True,
            streak_count=2,
        )
        self.assertTrue(any('2日連続' in m['text'] for m in messages))

    def test_build_session_achievements_shows_mock_near_when_remaining_within_threshold(self):
        from exams.gamification import build_session_achievements

        unlock_status = {
            'random': {'is_unlocked': False},
            'mock_exam': {
                'is_unlocked': False,
                'remaining_categories': [
                    {
                        'display_name': '文法・語彙問題',
                        'remaining_rate': 55,
                        'progress_rate': 25,
                        'question_type': 'grammar_fill',
                    },
                ],
            },
        }
        messages = build_session_achievements(
            user=None,
            level='4',
            question_type='grammar_fill',
            correct_count=1,
            total_count=5,
            unlock_status=unlock_status,
            session_count=5,
        )
        self.assertTrue(any('模擬試験まであと55%' in m['text'] for m in messages))
        self.assertFalse(any('あと少し' in m['text'] for m in messages))

    def test_build_session_achievements_mock_near_prefers_current_question_type(self):
        from exams.gamification import build_session_achievements

        unlock_status = {
            'random': {'is_unlocked': False},
            'mock_exam': {
                'is_unlocked': False,
                'remaining_categories': [
                    {
                        'display_name': '文法・語彙問題',
                        'remaining_rate': 60,
                        'progress_rate': 20,
                        'question_type': 'grammar_fill',
                    },
                    {
                        'display_name': '会話補充問題',
                        'remaining_rate': 55,
                        'progress_rate': 25,
                        'question_type': 'conversation_fill',
                    },
                ],
            },
        }
        messages = build_session_achievements(
            user=None,
            level='4',
            question_type='grammar_fill',
            correct_count=5,
            total_count=5,
            unlock_status=unlock_status,
            session_count=5,
        )
        mock_messages = [m['text'] for m in messages if '模擬試験まで' in m['text']]
        self.assertEqual(len(mock_messages), 1)
        self.assertIn('文法・語彙問題', mock_messages[0])
        self.assertIn('あと60%', mock_messages[0])
        self.assertNotIn('会話補充問題', mock_messages[0])

    def test_format_mock_remaining_message_tiers(self):
        from exams.gamification import format_mock_remaining_message

        self.assertEqual(
            format_mock_remaining_message(10, '会話補充問題'),
            'あと少し！模擬試験まであと10%（会話補充問題）',
        )
        self.assertEqual(
            format_mock_remaining_message(30, '文法・語彙問題'),
            'この調子！模擬試験まであと30%（文法・語彙問題）',
        )
        self.assertEqual(
            format_mock_remaining_message(70, '会話補充問題'),
            '模擬試験まであと70%（会話補充問題）',
        )

    def test_get_daily_mission_goal_legacy_session_key_for_level_4(self):
        from exams.gamification import get_daily_mission_goal

        class FakeSession(dict):
            modified = False

        session = FakeSession({'daily_mission_goal': 10})
        request = type('R', (), {'session': session})()
        self.assertEqual(get_daily_mission_goal(request, level='4'), 10)
        self.assertEqual(get_daily_mission_goal(request, level='3'), 3)

    def test_build_session_achievements_shows_mission_complete(self):
        from exams.gamification import ACHIEVEMENT_COPY, build_session_achievements

        user = User.objects.create_user(username='missionuser', password='pass')
        question = Question.objects.create(
            level='4',
            question_type='grammar_fill',
            question_text='Mission test',
        )
        choice = Choice.objects.create(
            question=question,
            choice_text='A',
            is_correct=True,
            order=1,
        )
        now = timezone.now()
        for _ in range(3):
            UserAnswer.objects.create(
                user=user,
                question=question,
                selected_choice=choice,
                is_correct=True,
                answered_at=now,
            )

        unlock_status = {
            'random': {'is_unlocked': False},
            'mock_exam': {'is_unlocked': False, 'remaining_categories': []},
        }
        messages = build_session_achievements(
            user=user,
            level='4',
            question_type='grammar_fill',
            correct_count=1,
            total_count=1,
            unlock_status=unlock_status,
            session_count=1,
            daily_goal=3,
        )
        self.assertTrue(
            any(ACHIEVEMENT_COPY['mission_complete'] in m['text'] for m in messages)
        )

    def test_build_streak_summary_hides_streak_after_long_gap(self):
        from exams.gamification import build_streak_summary

        user = User.objects.create_user(username='gapuser', password='pass')
        UserStreak.objects.create(
            user=user,
            current_streak=8,
            longest_streak=8,
            last_active_date=timezone.localdate() - timedelta(days=4),
        )
        summary = build_streak_summary(user)
        self.assertEqual(summary['current_streak'], 0)
        self.assertIn('スタート', summary['hint'])

    def test_build_streak_summary_hides_streak_during_grace_period(self):
        from exams.gamification import build_streak_summary

        user = User.objects.create_user(username='graceuser', password='pass')
        UserStreak.objects.create(
            user=user,
            current_streak=7,
            longest_streak=7,
            last_active_date=timezone.localdate() - timedelta(days=2),
        )
        summary = build_streak_summary(user)
        self.assertEqual(summary['current_streak'], 0)
        self.assertIn('7日連続をキープ', summary['hint'])
        self.assertFalse(summary['studied_today'])
        self.assertTrue(summary['grace_available'])
        self.assertEqual(summary['grace_notice'], '今週の維持チャンスが残り1回')
        self.assertIn('お休み', summary['rule_tooltip'])

    def test_build_streak_summary_grace_unavailable_after_weekly_use(self):
        from exams.gamification import build_streak_summary, _week_start

        user = User.objects.create_user(username='usedgrace', password='pass')
        today = timezone.localdate()
        UserStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=5,
            last_active_date=today - timedelta(days=2),
            freeze_week_start=_week_start(today),
        )
        summary = build_streak_summary(user)
        self.assertFalse(summary['grace_available'])
        self.assertIsNone(summary['grace_notice'])
        self.assertIn('スタート', summary['hint'])

    def test_award_new_badges_grants_first_reading_once(self):
        from exams.gamification import award_new_badges

        user = User.objects.create_user(username='badgeuser', password='pass')
        earned = award_new_badges(user, question_type='reading_comprehension')
        self.assertEqual(len(earned), 1)
        self.assertEqual(earned[0]['id'], 'first_reading')
        self.assertFalse(
            award_new_badges(user, question_type='reading_comprehension')
        )

    def test_build_badge_collection_marks_earned_badges(self):
        from exams.gamification import build_badge_collection

        user = User.objects.create_user(username='collectionuser', password='pass')
        UserBadge.objects.create(user=user, badge_id='total_50')
        collection = build_badge_collection(user)
        self.assertEqual(collection['earned_count'], 1)
        earned_item = next(item for item in collection['items'] if item['id'] == 'total_50')
        self.assertTrue(earned_item['earned'])

    def test_build_badge_collection_excludes_writing_for_level_4(self):
        from exams.gamification import BADGE_DEFINITIONS, build_badge_collection

        user = User.objects.create_user(username='badgeleveluser', password='pass')
        collection = build_badge_collection(user, level='4')
        badge_ids = [item['id'] for item in collection['items']]
        self.assertNotIn('first_writing', badge_ids)
        self.assertEqual(collection['total_count'], len(BADGE_DEFINITIONS) - 1)

    def test_build_badge_collection_includes_writing_for_level_3(self):
        from exams.gamification import build_badge_collection

        user = User.objects.create_user(username='badgelevel3user', password='pass')
        collection = build_badge_collection(user, level='3')
        badge_ids = [item['id'] for item in collection['items']]
        self.assertIn('first_writing', badge_ids)


class WritingFeedbackTests(TestCase):
    """Phase-1 writing self-check (exams/writing_feedback.py)."""

    def test_parse_rubric_email_reply(self):
        from exams.writing_feedback import parse_writing_rubric

        text = (
            'James の 2 つの質問（下線部）に答えること。\n'
            '●語数の目安は 15～25 語です。'
        )
        rubric = parse_writing_rubric(text)
        self.assertEqual(rubric['kind'], 'email_reply')
        self.assertEqual(rubric['word_min'], 15)
        self.assertEqual(rubric['word_max'], 25)
        self.assertTrue(rubric['count_body_only'])

    def test_parse_rubric_opinion(self):
        from exams.writing_feedback import parse_writing_rubric

        text = '2 つの英文で書きなさい。語数の目安は 25～35語。'
        rubric = parse_writing_rubric(text)
        self.assertEqual(rubric['kind'], 'opinion')
        self.assertEqual(rubric['sentence_min'], 2)

    def test_extract_email_body_excludes_greeting(self):
        from exams.writing_feedback import count_english_words, extract_email_body

        text = (
            'Hi, James!\n'
            'Thank you for your e-mail.\n\n'
            'I planted the potatoes this March. I am growing about twenty carrots.\n\n'
            'Best wishes,\n'
        )
        body = extract_email_body(text)
        self.assertIn('planted', body)
        self.assertNotIn('Hi', body.split()[0])
        self.assertEqual(count_english_words(body), 12)

    def test_analyze_email_reply_word_count_ok(self):
        from exams.writing_feedback import analyze_writing_response

        rubric = {
            'kind': 'email_reply',
            'word_min': 15,
            'word_max': 25,
            'count_body_only': True,
        }
        text = (
            'Hi, James!\n'
            'Thank you for your e-mail.\n\n'
            'I planted them last March. I am growing about twenty carrots in my garden now.\n\n'
            'Best wishes,\n'
        )
        result = analyze_writing_response(text, rubric)
        messages = [item['message'] for item in result['items']]
        self.assertTrue(any('語数:' in msg and '✅' not in msg for msg in messages))
        self.assertTrue(any(item['level'] == 'ok' and '語数:' in item['message'] for item in result['items']))

    def test_analyze_opinion_warns_short_sentences(self):
        from exams.writing_feedback import analyze_writing_response

        rubric = {
            'kind': 'opinion',
            'word_min': 25,
            'word_max': 35,
            'sentence_min': 2,
            'sentence_max': 2,
            'count_body_only': False,
        }
        text = 'English is more interesting for me because I like reading books.'
        result = analyze_writing_response(text, rubric)
        self.assertTrue(
            any(item['level'] == 'warn' and '文数' in item['message'] for item in result['items'])
        )

    def test_get_writing_rubric_falls_back_to_question_text(self):
        from exams.models import Question
        from exams.writing_feedback import get_writing_rubric

        question = Question(
            question_text='2 つの英文で書きなさい。語数の目安は 25～35語。',
            question_type='writing',
            level='3',
        )
        rubric = get_writing_rubric(question)
        self.assertEqual(rubric['kind'], 'opinion')
