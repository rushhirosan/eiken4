from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

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
        self.url = reverse('login')
    
    def test_login_view_accessible(self):
        """ログインページにアクセスできるかテスト"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
    
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
        response = self.client.post(self.url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        # 登録成功後はリダイレクト
        self.assertEqual(response.status_code, 302)
        # ユーザーが作成されたか確認
        self.assertTrue(User.objects.filter(username='newuser').exists())
