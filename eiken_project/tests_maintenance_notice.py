from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

FOOTER_NOTE = 'まだ直すべきところは残っているはずです'
ABOUT_NOTE = '練習問題は制作者1人で作っています'
OLD_BANNER = '問題は公開中。品質は上げていきます。'


class QualityNoticeTest(TestCase):
    def test_landing_puts_short_note_in_footer_not_a_banner(self):
        response = Client().get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, FOOTER_NOTE)
        self.assertNotContains(response, OLD_BANNER)
        self.assertNotContains(response, ABOUT_NOTE)
        self.assertNotContains(response, 'maintenance-notice')

    def test_about_has_the_longer_note(self):
        response = Client().get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ABOUT_NOTE)
        self.assertContains(response, 'そこを優先して直します')
        self.assertContains(response, FOOTER_NOTE)

    def test_exam_list_does_not_show_the_top_banner(self):
        user = get_user_model().objects.create_user(
            username='notice_user', password='x', preferred_exam_level='5'
        )
        client = Client()
        client.force_login(user)
        response = client.get(reverse('exams:exam_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, FOOTER_NOTE)
        self.assertNotContains(response, OLD_BANNER)
        self.assertNotContains(response, 'maintenance-notice')
