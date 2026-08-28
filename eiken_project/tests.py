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
from exams.provenance import PROVENANCE_ORIGINAL

User = get_user_model()


class LandingPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='landing_user', password='testpass123')

    def test_landing_page_is_public(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'えいごごはん')
        self.assertContains(response, '無料アカウント作成')
        self.assertContains(response, reverse('try_index'))
        self.assertContains(response, '登録なしでお試し')
        self.assertContains(response, reverse('guides'))
        self.assertContains(response, '本サイトは公益財団法人 日本英語検定協会の公式サイトではありません。')
        self.assertContains(response, '英検®は、公益財団法人 日本英語検定協会の登録商標です。')
        self.assertContains(response, '級の目安は、一般的な英語検定の5・4・3級レベルです。')
        # マーケ文言では「英検」を使わず、フッターの®表記のみ
        body = response.content.decode()
        body_without_notice = body.replace('英検®は、公益財団法人 日本英語検定協会の登録商標です。', '')
        self.assertNotIn('英検', body_without_notice)

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


class FaviconTest(TestCase):
    def test_favicon_ico_served_at_root(self):
        response = Client().get(reverse('favicon_ico'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/x-icon')
        body = b''.join(response.streaming_content)
        self.assertGreater(len(body), 100)

    def test_landing_links_favicon(self):
        response = Client().get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'favicon.svg')
        self.assertContains(response, 'favicon.ico')
        self.assertContains(response, 'apple-touch-icon.png')

    def test_login_links_favicon(self):
        response = Client().get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'favicon.svg')


class RobotsTxtTest(TestCase):
    def test_robots_txt_served_at_root(self):
        response = Client().get(reverse('robots_txt'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertContains(response, 'Disallow: /accounts/')
        self.assertContains(response, 'Disallow: /exams/')
        self.assertContains(response, 'Allow: /about/')
        self.assertContains(response, 'Allow: /guides/')
        self.assertContains(response, 'Allow: /try/')
        self.assertContains(response, 'Allow: /resources/')
        self.assertContains(response, 'Allow: /llms.txt')
        self.assertContains(response, 'Sitemap: https://eigogohan.com/sitemap.xml')


class LlmsTxtTest(TestCase):
    def test_llms_txt_served_at_root(self):
        response = Client().get(reverse('llms_txt'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
        content = response.content.decode()
        self.assertTrue(content.startswith('# えいごごはん\n'))
        self.assertIn('> 5級・4級・3級向け', content)
        self.assertIn('- [トップ](https://eigogohan.com/):', content)
        self.assertIn('- [サービス概要・FAQ](https://eigogohan.com/about/):', content)
        self.assertIn('- [学習の進め方](https://eigogohan.com/guides/):', content)
        self.assertIn('- [お試し問題](https://eigogohan.com/try/):', content)
        self.assertIn('- [4級 リスニング](https://eigogohan.com/guides/eiken-4-listening/):', content)
        self.assertIn('- [4級 長文読解](https://eigogohan.com/guides/eiken-4-reading/):', content)
        self.assertIn('長文練習問題を無料で解く進め方', content)
        self.assertIn('- [3級 ライティング](https://eigogohan.com/guides/eiken-3-writing/):', content)
        self.assertIn('- [5級 スピーキング](https://eigogohan.com/guides/eiken-5-speaking/):', content)
        self.assertIn('- [3級 スピーキング](https://eigogohan.com/guides/eiken-3-speaking/):', content)
        self.assertIn('- [学習リソース](https://eigogohan.com/resources/):', content)
        self.assertIn('日本英語検定協会の公式サイト・公式アプリではない', content)
        self.assertNotIn('英検', content)
        self.assertIn('## Optional', content)
        self.assertIn('- [プライバシーポリシー](https://eigogohan.com/privacy-policy/):', content)
        # Docs セクションの公開ページは Markdown リンク形式
        self.assertNotIn('- トップ:', content)
        self.assertNotIn('- サービス概要・FAQ:', content)


class GuidesPageTest(TestCase):
    def test_guides_page_is_public(self):
        response = Client().get(reverse('guides'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '学習の進め方')
        self.assertContains(response, '5級の進め方')
        self.assertContains(response, '4級の進め方')
        self.assertContains(response, '3級の進め方')
        self.assertContains(response, 'フィードバックの送り方')
        self.assertContains(response, 'FAQPage')
        self.assertContains(response, 'index, follow')
        self.assertContains(response, 'https://eigogohan.com/guides/')
        # 5級にも会話補充がある（4級固有ではない）
        self.assertContains(response, 'id="level-5"')
        self.assertRegex(
            response.content.decode(),
            r'id="level-5"[\s\S]*?会話補充[\s\S]*?id="level-4"',
        )
        self.assertContains(response, '5級に加えて<strong>長文読解</strong>があります')
        self.assertContains(response, '級×パート別ガイド')
        self.assertContains(response, reverse('guide_topic', kwargs={'slug': 'eiken-4-listening'}))
        self.assertContains(response, reverse('guide_topic', kwargs={'slug': 'eiken-3-writing'}))
        self.assertContains(response, reverse('guide_topic', kwargs={'slug': 'eiken-5-speaking'}))
        self.assertContains(response, reverse('guide_topic', kwargs={'slug': 'eiken-3-speaking'}))
        self.assertContains(response, 'スピーキング（任意）')
        self.assertContains(response, 'スピーキングは合否に関係しますか？')
        content = response.content.decode()
        self.assertIn('vendor/bootstrap/bootstrap.min.css', content)
        self.assertNotIn('fonts.googleapis.com', content)
        self.assertNotIn('font-awesome', content)

    def test_guides_shows_next_learning_when_enabled(self):
        from django.test import override_settings

        with override_settings(SHOW_NEXT_LEARNING=True):
            response = Client().get(reverse('guides'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'このあとの学習')
        self.assertContains(response, '5級の過去問・問題集を見てみる')
        self.assertContains(response, '4級の過去問・問題集を見てみる')
        self.assertContains(response, '3級の過去問・問題集を見てみる')
        self.assertContains(response, 'アフィリエイトを含みます')
        self.assertContains(response, 'rel="noopener noreferrer sponsored"')
        self.assertContains(response, reverse('resources'))
        self.assertContains(response, '学習リソース')

    def test_guides_hides_next_learning_when_disabled(self):
        from django.test import override_settings

        with override_settings(SHOW_NEXT_LEARNING=False):
            response = Client().get(reverse('guides'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'このあとの学習')
        self.assertNotContains(response, '5級の過去問・問題集を見てみる')
        self.assertNotContains(response, reverse('resources'))


class GuideTopicPageTest(TestCase):
    def test_guide_topic_page_is_public(self):
        response = Client().get(
            reverse('guide_topic', kwargs={'slug': 'eiken-4-listening'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '4級のリスニングを無料で練習する')
        self.assertContains(response, 'index, follow')
        self.assertContains(response, 'https://eigogohan.com/guides/eiken-4-listening/')
        self.assertContains(response, 'FAQPage')
        self.assertContains(response, 'BreadcrumbList')
        self.assertContains(response, reverse('signup'))
        self.assertContains(response, reverse('guides'))
        self.assertContains(response, reverse('try_level', kwargs={'level': '4'}))
        self.assertContains(response, '4級をお試し（登録なし）')
        content = response.content.decode()
        self.assertIn('vendor/bootstrap/bootstrap.min.css', content)
        self.assertNotIn('fonts.googleapis.com', content)
        self.assertNotIn('font-awesome', content)

    def test_guide_topic_reading_matches_search_intent(self):
        response = Client().get(
            reverse('guide_topic', kwargs={'slug': 'eiken-4-reading'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '4級の長文練習問題を無料で解く')
        self.assertContains(response, '4級の長文練習問題をブラウザで無料練習')
        self.assertContains(response, reverse('try_level', kwargs={'level': '4'}))
        self.assertContains(response, '4級の長文練習問題は無料で解けますか？')

    def test_guide_topic_unknown_slug_404(self):
        response = Client().get(
            reverse('guide_topic', kwargs={'slug': 'eiken-2-listening'})
        )
        self.assertEqual(response.status_code, 404)

    def test_guide_topic_slashless_redirects(self):
        response = Client().get('/guides/eiken-5-grammar')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], '/guides/eiken-5-grammar/')

    def test_all_guide_topics_render(self):
        from eiken_project.guide_topics import iter_guide_topics

        for topic in iter_guide_topics():
            response = Client().get(
                reverse('guide_topic', kwargs={'slug': topic['slug']})
            )
            self.assertEqual(response.status_code, 200, topic['slug'])
            self.assertContains(response, topic['h1'])
            self.assertContains(response, '無料で練習を始める')


class ResourcesPageTest(TestCase):
    def test_resources_page_when_enabled(self):
        from django.test import override_settings

        with override_settings(SHOW_NEXT_LEARNING=True):
            response = Client().get(reverse('resources'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'あわせて使える学習リソース')
        self.assertContains(response, '5級')
        self.assertContains(response, '4級')
        self.assertContains(response, '3級')
        self.assertContains(response, '5級の過去問・問題集')
        self.assertContains(response, '4級の長文対策')
        self.assertContains(response, '3級の長文対策')
        self.assertContains(response, '3級の英作文・ライティング対策')
        self.assertContains(response, '任意')
        self.assertContains(response, 'アフィリエイト')
        self.assertContains(response, '公式サイトではありません')
        self.assertContains(response, 'https://www.eiken.or.jp/eiken/exam/grade_5/')
        self.assertContains(response, 'https://www.eiken.or.jp/eiken/exam/grade_4/')
        self.assertContains(response, 'https://www.eiken.or.jp/eiken/exam/grade_3/')
        self.assertContains(response, '協会の5級過去問・試験内容ページ（公式）')
        self.assertContains(response, 'https://eigogohan.com/resources/')
        self.assertContains(response, reverse('guides'))
        content = response.content.decode()
        self.assertIn('4%E7%B4%9A+%E9%95%B7%E6%96%87', content)
        self.assertIn('3%E7%B4%9A+%E9%95%B7%E6%96%87', content)

    def test_resources_page_404_when_disabled(self):
        from django.test import override_settings

        with override_settings(SHOW_NEXT_LEARNING=False):
            response = Client().get(reverse('resources'))
        self.assertEqual(response.status_code, 404)


class PrivacyPolicyAffiliateTest(TestCase):
    def test_privacy_shows_affiliate_section_when_enabled(self):
        from django.test import override_settings

        with override_settings(SHOW_NEXT_LEARNING=True):
            response = Client().get(reverse('privacy_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'アフィリエイトリンクについて')

    def test_privacy_hides_affiliate_section_when_disabled(self):
        from django.test import override_settings

        with override_settings(SHOW_NEXT_LEARNING=False):
            response = Client().get(reverse('privacy_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'アフィリエイトリンクについて')


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
        self.assertContains(response, 'えいごごはん')
        self.assertContains(response, '5級</strong> — 文法・語彙、会話補充')
        self.assertContains(response, 'スピーキング（任意）')
        self.assertContains(response, '4級</strong> — 文法・語彙、会話補充、語順選択、長文読解')
        self.assertContains(response, '3級</strong> — 文法・語彙、会話補充、ライティング')
        self.assertContains(response, 'スピーキング（二次面接の流れ）')
        self.assertContains(response, 'スピーキング問題はありますか？')
        self.assertContains(response, '本サイトは公益財団法人 日本英語検定協会の公式サイトではありません。')
        self.assertContains(response, '英検®は、公益財団法人 日本英語検定協会の登録商標です。')
        self.assertContains(
            response,
            'このコンテンツは、公益財団法人 日本英語検定協会の承認や推奨、その他の検討を受けたものではありません。',
        )
        body_without_notice = response.content.decode().replace(
            '英検®は、公益財団法人 日本英語検定協会の登録商標です。',
            '',
        )
        self.assertNotIn('英検', body_without_notice)


class SitemapXmlTest(TestCase):
    def test_sitemap_lists_only_public_pages(self):
        from django.test import override_settings

        with override_settings(SHOW_NEXT_LEARNING=False):
            response = Client().get(reverse('sitemap_xml'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'https://eigogohan.com/')
        self.assertContains(response, 'https://eigogohan.com/about/')
        self.assertContains(response, 'https://eigogohan.com/guides/')
        self.assertContains(response, 'https://eigogohan.com/guides/eiken-4-listening/')
        self.assertContains(response, 'https://eigogohan.com/guides/eiken-3-writing/')
        self.assertContains(response, 'https://eigogohan.com/guides/eiken-5-speaking/')
        self.assertContains(response, 'https://eigogohan.com/guides/eiken-3-speaking/')
        self.assertContains(response, 'https://eigogohan.com/try/')
        self.assertContains(response, 'https://eigogohan.com/try/5/')
        self.assertContains(response, 'https://eigogohan.com/privacy-policy/')
        self.assertNotContains(response, '/resources/')
        self.assertNotContains(response, '/exams/')
        self.assertNotContains(response, '/accounts/')

    def test_sitemap_includes_resources_when_enabled(self):
        from django.test import override_settings

        with override_settings(SHOW_NEXT_LEARNING=True):
            response = Client().get(reverse('sitemap_xml'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'https://eigogohan.com/resources/')


class LandingFaqJsonLdTest(TestCase):
    def test_landing_includes_faq_json_ld(self):
        response = Client().get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"@type": "FAQPage"')
        self.assertContains(response, '無料で使えますか')
        self.assertContains(response, '"@type": "WebSite"')
        self.assertContains(response, '"@type": "Organization"')
        self.assertContains(response, 'eigogohan-og-image.png')


class AppShellSeoTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='seo_user', password='testpass123'
        )
        self.client = Client()
        self.client.login(username='seo_user', password='testpass123')

    def test_exam_pages_are_noindex(self):
        response = self.client.get(reverse('exams:exam_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'noindex, follow')
        self.assertContains(response, 'えいごごはん')
        self.assertContains(response, '5級・4級・3級')
        self.assertContains(response, 'eigogohan-og-image.png')
        self.assertContains(response, 'favicon.svg')
        self.assertNotContains(response, 'eiken-og-image.png')
        self.assertNotContains(response, 'eiken-og-image.jpg')
        self.assertContains(response, '英検®は、公益財団法人 日本英語検定協会の登録商標です。')
        self.assertContains(response, '本サイトは公益財団法人 日本英語検定協会の公式サイトではありません。')

    def test_privacy_policy_remains_indexable(self):
        response = Client().get(reverse('privacy_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'index, follow')
        self.assertContains(response, 'プライバシーポリシー')


class LoginSeoTest(TestCase):
    def test_login_page_has_noindex(self):
        response = Client().get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'noindex, follow')

    def test_signup_page_has_noindex(self):
        response = Client().get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'noindex, follow')


class TrySamplePageTest(TestCase):
    def setUp(self):
        from exams.models import Choice, Question
        from questions.models import (
            ListeningChoice,
            ListeningQuestion,
            ReadingChoice,
            ReadingPassage,
            ReadingQuestion,
        )

        self.grammar = Question.objects.create(
            provenance=PROVENANCE_ORIGINAL,
            level='4',
            question_type='grammar_fill',
            question_text='I ( ) a book.',
            explanation='read が正解です。',
            question_number=1,
        )
        self.grammar_correct = Choice.objects.create(
            question=self.grammar, choice_text='read', is_correct=True, order=1
        )
        Choice.objects.create(
            question=self.grammar, choice_text='reads', is_correct=False, order=2
        )

        self.listening = ListeningQuestion.objects.create(
            provenance=PROVENANCE_ORIGINAL,
            level='4',
            question_text='Choose the correct picture.',
            image='images/level4/part1/listening_illustration_image1.png',
            audio='audio/level4/part1/listening_illustration_question1.mp3',
            correct_answer='1',
            explanation='1が正解です。',
        )
        self.listening_correct = ListeningChoice.objects.create(
            question=self.listening, choice_text='1', is_correct=True, order=1
        )
        ListeningChoice.objects.create(
            question=self.listening, choice_text='2', is_correct=False, order=2
        )

        self.passage = ReadingPassage.objects.create(
            provenance=PROVENANCE_ORIGINAL,
            level='4',
            identifier='a',
            text='Tom has a dog. The dog is brown.',
        )
        self.reading = ReadingQuestion.objects.create(
            passage=self.passage,
            question_text='What color is the dog?',
            question_number=1,
            explanation='本文に brown とあります。',
        )
        self.reading_correct = ReadingChoice.objects.create(
            question=self.reading, choice_text='Brown.', is_correct=True, order=1
        )
        ReadingChoice.objects.create(
            question=self.reading, choice_text='Black.', is_correct=False, order=2
        )

    def test_try_index_is_public(self):
        response = Client().get(reverse('try_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'お試し問題')
        self.assertContains(response, '登録不要')
        self.assertContains(response, reverse('try_level', kwargs={'level': '4'}))
        self.assertContains(response, 'index, follow')

    def test_try_level_shows_grammar_and_listening(self):
        response = Client().get(reverse('try_level', kwargs={'level': '4'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '4級のお試し問題')
        self.assertContains(response, '登録なし・無料')
        self.assertContains(response, '文法・リスニング・長文をお試し')
        self.assertContains(response, 'I ( ) a book.')
        self.assertContains(response, 'Choose the correct picture.')
        self.assertContains(response, 'audio/level4/part1/listening_illustration_question1.mp3')
        self.assertContains(response, 'images/level4/part1/listening_illustration_image1.png')
        self.assertContains(response, 'Tom has a dog.')
        self.assertContains(response, 'What color is the dog?')
        self.assertContains(response, '長文読解（お試し）')
        self.assertContains(response, '回答する')
        self.assertContains(response, '4級の学習ガイド')
        self.assertContains(
            response, reverse('guide_topic', kwargs={'slug': 'eiken-4-reading'})
        )
        self.assertContains(response, '4級の長文練習問題を無料で解く')

    def test_try_level_grades_without_login(self):
        from exams.models import ReadingUserAnswer, UserAnswer
        from questions.models import ListeningUserAnswer

        response = Client().post(
            reverse('try_level', kwargs={'level': '4'}),
            {
                'answer_grammar': str(self.grammar_correct.id),
                'answer_listening': str(self.listening_correct.id),
                'answer_reading': str(self.reading_correct.id),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '3 / 3')
        self.assertContains(response, '無料登録して続きを練習する')
        self.assertEqual(UserAnswer.objects.count(), 0)
        self.assertEqual(ListeningUserAnswer.objects.count(), 0)
        self.assertEqual(ReadingUserAnswer.objects.count(), 0)

    def test_try_level_invalid_404(self):
        response = Client().get(reverse('try_level', kwargs={'level': '2'}))
        self.assertEqual(response.status_code, 404)

    def test_try_level_slashless_redirect(self):
        response = Client().get('/try/4')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], '/try/4/')


@override_settings(ALLOWED_HOSTS=[
    'eiken-app.fly.dev',
    'eigogohan.com',
    'www.eigogohan.com',
    'eiken-practice.com',
    'www.eiken-practice.com',
    'testserver',
])
class CanonicalHostRedirectTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_fly_dev_host_redirects_to_custom_domain(self):
        response = self.client.get('/about/', HTTP_HOST='eiken-app.fly.dev')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'https://eigogohan.com/about/')

    def test_fly_dev_appends_trailing_slash_in_one_hop(self):
        """Avoid fly.dev/about → apex/about → /about/ chains (GSC Redirect error)."""
        response = self.client.get('/about', HTTP_HOST='eiken-app.fly.dev')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'https://eigogohan.com/about/')

    def test_fly_dev_preserves_query_string(self):
        response = self.client.get('/guides/?from=old', HTTP_HOST='eiken-app.fly.dev')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'https://eigogohan.com/guides/?from=old')

    def test_fly_dev_preserves_query_string_when_appending_slash(self):
        response = self.client.get('/guides?from=old', HTTP_HOST='eiken-app.fly.dev')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'https://eigogohan.com/guides/?from=old')

    def test_healthz_is_not_redirected(self):
        response = self.client.get('/healthz/', HTTP_HOST='eiken-app.fly.dev')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ok')

    def test_custom_domain_is_not_redirected(self):
        response = self.client.get('/about/', HTTP_HOST='eigogohan.com')
        self.assertEqual(response.status_code, 200)

    def test_legacy_domain_redirects_to_canonical(self):
        response = self.client.get('/about/', HTTP_HOST='eiken-practice.com')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'https://eigogohan.com/about/')

    def test_www_redirects_to_apex(self):
        response = self.client.get('/guides/', HTTP_HOST='www.eigogohan.com')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], 'https://eigogohan.com/guides/')

    def test_slashless_public_pages_use_absolute_301(self):
        """Relative APPEND_SLASH Location can surface as GSC Redirect error."""
        for path, dest in (
            ('/about', 'https://eigogohan.com/about/'),
            ('/guides', 'https://eigogohan.com/guides/'),
            ('/resources', 'https://eigogohan.com/resources/'),
            ('/privacy-policy', 'https://eigogohan.com/privacy-policy/'),
        ):
            response = self.client.get(path, HTTP_HOST='eigogohan.com')
            self.assertEqual(response.status_code, 301, path)
            self.assertEqual(response['Location'], dest, path)


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
