from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from unittest.mock import MagicMock, patch
import json
import urllib.error

from eiken_project.discord_notify import (
    notify_feedback_created,
    notify_user_registered,
    send_discord_message,
)

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
        self.assertContains(response, reverse('guides'))

    def test_landing_avoids_render_blocking_third_party_assets(self):
        """公開トップは LCP のため外部フォント/アイコンCDNに依存しない。"""
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('vendor/bootstrap/bootstrap.min.css', content)
        self.assertNotIn('fonts.googleapis.com', content)
        self.assertNotIn('fonts.gstatic.com', content)
        self.assertNotIn('cdnjs.cloudflare.com', content)
        self.assertNotIn('font-awesome', content)
        self.assertNotIn('bootstrap.bundle.min.js', content)
        # GTM は load 後に動的挿入（初期 HTML に同期 script タグを置かない）
        self.assertNotIn('<script async src="https://www.googletagmanager.com/gtag/js', content)
        self.assertIn("window.addEventListener('load'", content)
        self.assertIn('<main>', content)
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
        self.assertContains(response, 'Allow: /guides/')
        self.assertContains(response, 'Allow: /llms.txt')
        self.assertContains(response, 'Sitemap: https://eiken-practice.com/sitemap.xml')


class LlmsTxtTest(TestCase):
    def test_llms_txt_served_at_root(self):
        response = Client().get(reverse('llms_txt'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
        content = response.content.decode()
        self.assertTrue(content.startswith('# Eiken Practice\n'))
        self.assertIn('> 英検5級・4級・3級', content)
        self.assertIn('- [トップ](https://eiken-practice.com/):', content)
        self.assertIn('- [サービス概要・FAQ](https://eiken-practice.com/about/):', content)
        self.assertIn('- [学習の進め方](https://eiken-practice.com/guides/):', content)
        self.assertIn('## Optional', content)
        self.assertIn('- [プライバシーポリシー](https://eiken-practice.com/privacy-policy/):', content)
        # Docs セクションの公開ページは Markdown リンク形式
        self.assertNotIn('- トップ:', content)
        self.assertNotIn('- サービス概要・FAQ:', content)


class GuidesPageTest(TestCase):
    def test_guides_page_is_public(self):
        response = Client().get(reverse('guides'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '学習の進め方')
        self.assertContains(response, '英検5級の進め方')
        self.assertContains(response, '英検4級の進め方')
        self.assertContains(response, '英検3級の進め方')
        self.assertContains(response, 'フィードバックの送り方')
        self.assertContains(response, 'FAQPage')
        self.assertContains(response, 'index, follow')
        self.assertContains(response, 'https://eiken-practice.com/guides/')
        # 5級にも会話補充がある（4級固有ではない）
        self.assertContains(response, 'id="level-5"')
        self.assertRegex(
            response.content.decode(),
            r'id="level-5"[\s\S]*?会話補充[\s\S]*?id="level-4"',
        )
        self.assertContains(response, '5級に加えて<strong>長文読解</strong>があります')
        content = response.content.decode()
        self.assertIn('vendor/bootstrap/bootstrap.min.css', content)
        self.assertNotIn('fonts.googleapis.com', content)
        self.assertNotIn('font-awesome', content)


class AuthenticatedNavLinksTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='nav_user', password='testpass123')
        self.client = Client()
        self.client.login(username='nav_user', password='testpass123')

    def test_exam_list_footer_links_to_guides_and_about(self):
        response = self.client.get(reverse('exams:exam_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('guides'))
        self.assertContains(response, reverse('about'))
        self.assertContains(response, '学習の進め方')
        self.assertContains(response, 'サービス概要')


class AboutPageTest(TestCase):
    def test_about_page_is_public(self):
        response = Client().get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'サービス概要')
        self.assertContains(response, 'よくある質問')
        self.assertContains(response, 'FAQPage')
        self.assertContains(response, reverse('guides'))
        self.assertContains(response, '英検5級</strong> — 文法・語彙、会話補充')
        self.assertContains(response, '英検4級</strong> — 文法・語彙、会話補充、語順選択、長文読解')
        self.assertContains(response, '英検3級</strong> — 文法・語彙、会話補充、ライティング')


class SitemapXmlTest(TestCase):
    def test_sitemap_lists_only_public_pages(self):
        response = Client().get(reverse('sitemap_xml'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'https://eiken-practice.com/')
        self.assertContains(response, 'https://eiken-practice.com/about/')
        self.assertContains(response, 'https://eiken-practice.com/guides/')
        self.assertContains(response, 'https://eiken-practice.com/privacy-policy/')
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


@override_settings(ALLOWED_HOSTS=['eiken-app.fly.dev', 'eiken-practice.com', 'testserver'])
class CanonicalHostRedirectTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_fly_dev_host_redirects_to_custom_domain(self):
        response = self.client.get('/about/', HTTP_HOST='eiken-app.fly.dev')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'https://eiken-practice.com/about/')

    def test_fly_dev_preserves_query_string(self):
        response = self.client.get('/guides/?from=old', HTTP_HOST='eiken-app.fly.dev')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'https://eiken-practice.com/guides/?from=old')

    def test_healthz_is_not_redirected(self):
        response = self.client.get('/healthz/', HTTP_HOST='eiken-app.fly.dev')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ok')

    def test_custom_domain_is_not_redirected(self):
        response = self.client.get('/about/', HTTP_HOST='eiken-practice.com')
        self.assertEqual(response.status_code, 200)


class DiscordNotifyTest(TestCase):
    @override_settings(DISCORD_WEBHOOK_URL='')
    def test_skips_when_webhook_unset(self):
        with patch('eiken_project.discord_notify.urllib.request.urlopen') as mock_open:
            self.assertFalse(send_discord_message(content='hello'))
            mock_open.assert_not_called()

    @override_settings(DISCORD_WEBHOOK_URL='https://discord.example/webhook')
    def test_posts_json_payload(self):
        mock_response = MagicMock()
        mock_response.status = 204
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False

        with patch(
            'eiken_project.discord_notify.urllib.request.urlopen',
            return_value=mock_response,
        ) as mock_open:
            self.assertTrue(notify_user_registered(username='alice', ip='1.2.3.4'))
            request = mock_open.call_args[0][0]
            body = json.loads(request.data.decode('utf-8'))
            self.assertEqual(body['embeds'][0]['title'], '新規ユーザー登録')
            self.assertEqual(body['embeds'][0]['fields'][0]['value'], 'alice')

    @override_settings(DISCORD_WEBHOOK_URL='https://discord.example/webhook')
    def test_network_error_does_not_raise(self):
        with patch(
            'eiken_project.discord_notify.urllib.request.urlopen',
            side_effect=urllib.error.URLError('down'),
        ):
            self.assertFalse(
                notify_feedback_created(
                    username='bob',
                    feedback_type_label='バグ報告',
                    title='落ちる',
                    content='詳細',
                )
            )
