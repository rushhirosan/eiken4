from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch

from .recovery import (
    check_recovery_code,
    format_recovery_code,
    generate_recovery_code,
    hash_recovery_code,
    normalize_recovery_code,
)

User = get_user_model()


class CustomUserModelTest(TestCase):
    """CustomUserモデルのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_creation(self):
        """ユーザーが正しく作成されるかテスト"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertTrue(isinstance(self.user, User))

    def test_user_str(self):
        """ユーザーの__str__メソッドのテスト"""
        self.assertEqual(str(self.user), 'testuser')

    def test_user_is_active_default(self):
        """ユーザーがデフォルトでアクティブかテスト"""
        self.assertTrue(self.user.is_active)

    def test_set_and_check_recovery_code(self):
        plain = self.user.set_recovery_code()
        self.user.refresh_from_db()
        self.assertTrue(self.user.has_recovery_code())
        self.assertTrue(self.user.check_recovery_code(plain))
        self.assertTrue(self.user.check_recovery_code(plain.lower().replace('-', '')))
        self.assertFalse(self.user.check_recovery_code('AAAA-AAAA'))


class RecoveryHelpersTest(TestCase):
    def test_generate_format(self):
        code = generate_recovery_code()
        self.assertRegex(code, r'^[A-Z2-9]{4}-[A-Z2-9]{4}$')
        self.assertEqual(len(normalize_recovery_code(code)), 8)

    def test_hash_roundtrip(self):
        code = 'AB2C-DE3F'
        digest = hash_recovery_code(code)
        self.assertTrue(check_recovery_code('ab2cde3f', digest))
        self.assertEqual(format_recovery_code('ab2c de3f'), 'AB2C-DE3F')


class LoginViewTest(TestCase):
    """ログインビューのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user.set_recovery_code('ABCD-EFGH')
        self.url = reverse('login')

    def test_login_view_accessible(self):
        """ログインページにアクセスできるかテスト"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertContains(response, reverse('recover_password'))

    def test_login_success(self):
        """正しい認証情報でログインできるかテスト"""
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        # ログイン成功後はリダイレクト
        self.assertEqual(response.status_code, 302)

    def test_login_failure(self):
        """間違った認証情報でログインできないかテスト"""
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        # ログイン失敗時は同じページに留まる
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_issues_recovery_code_when_missing(self):
        self.user.recovery_code_hash = ''
        self.user.save(update_fields=['recovery_code_hash'])
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'testpass123'
        }, follow=False)
        self.assertRedirects(response, reverse('recovery_code_reveal'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.has_recovery_code())


class SignupViewTest(TestCase):
    """新規登録ビューのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.client = Client()
        self.url = reverse('signup')

    def test_signup_view_accessible(self):
        """新規登録ページにアクセスできるかテスト"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_signup_success(self):
        """新規登録が成功するかテスト"""
        with patch('accounts.views.notify_user_registered') as mock_notify:
            response = self.client.post(self.url, {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password1': 'testpass123',
                'password2': 'testpass123'
            })
            self.assertRedirects(response, reverse('recovery_code_reveal'))
            user = User.objects.get(username='newuser')
            self.assertTrue(user.has_recovery_code())
            mock_notify.assert_called_once()
            self.assertEqual(mock_notify.call_args.kwargs['username'], 'newuser')

            # 復元コード表示後に級選択へ
            reveal = self.client.get(reverse('recovery_code_reveal'))
            self.assertEqual(reveal.status_code, 200)
            self.assertContains(reveal, '復元コードは')
            continue_resp = self.client.post(reverse('recovery_code_reveal'))
            self.assertRedirects(continue_resp, reverse('exams:choose_exam_level'))


class RecoverPasswordViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='recoveruser',
            password='oldpass12345',
        )
        self.plain_code = self.user.set_recovery_code('WXYZ-2345')
        self.url = reverse('recover_password')

    def test_recover_page_accessible(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '復元コード')

    def test_recover_success_rotates_code(self):
        response = self.client.post(self.url, {
            'username': 'recoveruser',
            'recovery_code': self.plain_code,
            'new_password1': 'brandnewpass99',
            'new_password2': 'brandnewpass99',
        })
        self.assertRedirects(response, reverse('recovery_code_reveal'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('brandnewpass99'))
        self.assertFalse(self.user.check_recovery_code(self.plain_code))

        reveal = self.client.get(reverse('recovery_code_reveal'))
        self.assertContains(reveal, '新しい復元コード')

    def test_recover_wrong_code(self):
        response = self.client.post(self.url, {
            'username': 'recoveruser',
            'recovery_code': 'AAAA-AAAA',
            'new_password1': 'brandnewpass99',
            'new_password2': 'brandnewpass99',
        })
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('oldpass12345'))
