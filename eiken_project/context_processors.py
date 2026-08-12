from django.conf import settings


def google_analytics(request):
    """
    Google Analytics 4の測定IDをテンプレートに渡す
    """
    return {
        'GA_MEASUREMENT_ID': getattr(settings, 'GA_MEASUREMENT_ID', 'G-XXXXXXXXXX'),
    }


def maintenance_notice(request):
    """問題ゼロ公開中など、既存ユーザー向けのメンテ案内。"""
    enabled = getattr(settings, 'MAINTENANCE_NOTICE_ENABLED', False)
    if not enabled:
        return {'maintenance_notice_enabled': False}
    return {
        'maintenance_notice_enabled': True,
        'maintenance_notice_title': getattr(
            settings, 'MAINTENANCE_NOTICE_TITLE', 'ただいまメンテナンス中です'
        ),
        'maintenance_notice_body': getattr(settings, 'MAINTENANCE_NOTICE_BODY', ''),
        'maintenance_official_exams_url': getattr(
            settings, 'MAINTENANCE_OFFICIAL_EXAMS_URL', ''
        ),
        'maintenance_official_exams_label': getattr(
            settings,
            'MAINTENANCE_OFFICIAL_EXAMS_LABEL',
            '公式の過去問・試験内容はこちら',
        ),
    }
