from django.test import Client, TestCase, override_settings
from django.urls import reverse


@override_settings(MAINTENANCE_NOTICE_ENABLED=True)
class MaintenanceNoticeTest(TestCase):
    def test_landing_shows_maintenance_notice(self):
        response = Client().get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ただいまメンテナンス中です')
        self.assertContains(response, '公式の過去問・試験内容はこちら')

    @override_settings(MAINTENANCE_NOTICE_ENABLED=False)
    def test_landing_hides_notice_when_disabled(self):
        response = Client().get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'ただいまメンテナンス中です')
