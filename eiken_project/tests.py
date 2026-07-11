from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class LandingPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='landing_user', password='testpass123')

    def test_landing_page_is_public(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '英検合格へ')
        self.assertContains(response, '無料アカウント作成')

    def test_authenticated_user_redirects_to_exam_list(self):
        self.client.login(username='landing_user', password='testpass123')
        response = self.client.get(reverse('landing'))
        self.assertRedirects(response, reverse('exams:exam_list'))


class RobotsTxtTest(TestCase):
    def test_robots_txt_served_at_root(self):
        response = Client().get(reverse('robots_txt'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertContains(response, 'Disallow: /accounts/')
        self.assertContains(response, 'Disallow: /exams/')
        self.assertContains(response, 'Allow: /about/')
        self.assertContains(response, 'Allow: /llms.txt')
        self.assertContains(response, 'Sitemap: https://eiken-app.fly.dev/sitemap.xml')


class LlmsTxtTest(TestCase):
    def test_llms_txt_served_at_root(self):
        response = Client().get(reverse('llms_txt'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Eiken Practice')
        self.assertContains(response, '英検5級・4級・3級')
        self.assertContains(response, 'https://eiken-app.fly.dev/about/')


class AboutPageTest(TestCase):
    def test_about_page_is_public(self):
        response = Client().get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'サービス概要')
        self.assertContains(response, 'よくある質問')
        self.assertContains(response, 'FAQPage')


class SitemapXmlTest(TestCase):
    def test_sitemap_lists_only_public_pages(self):
        response = Client().get(reverse('sitemap_xml'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'https://eiken-app.fly.dev/')
        self.assertContains(response, 'https://eiken-app.fly.dev/about/')
        self.assertContains(response, 'https://eiken-app.fly.dev/privacy-policy/')
        self.assertNotContains(response, '/exams/')
        self.assertNotContains(response, '/accounts/')


class LandingFaqJsonLdTest(TestCase):
    def test_landing_includes_faq_json_ld(self):
        response = Client().get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"@type": "FAQPage"')
        self.assertContains(response, '無料で使えますか')


class LoginSeoTest(TestCase):
    def test_login_page_has_noindex(self):
        response = Client().get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'noindex, follow')

    def test_signup_page_has_noindex(self):
        response = Client().get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'noindex, follow')
