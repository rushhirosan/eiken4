from django.conf import settings


def google_analytics(request):
    """
    Google Analytics 4の測定IDをテンプレートに渡す
    """
    return {
        'GA_MEASUREMENT_ID': getattr(settings, 'GA_MEASUREMENT_ID', 'G-XXXXXXXXXX'),
    }


def site_brand(request):
    """公開ブランド名・ベースURL・商標注記。"""
    return {
        'SITE_BRAND_NAME': getattr(settings, 'SITE_BRAND_NAME', 'えいごごはん'),
        'SITE_BRAND_FULL_NAME': getattr(settings, 'SITE_BRAND_FULL_NAME', 'EigoGohan'),
        'PUBLIC_BASE_URL': getattr(settings, 'PUBLIC_BASE_URL', 'https://eigogohan.com'),
    }

