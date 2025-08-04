from django.conf import settings

def google_analytics(request):
    """
    Google Analytics 4の測定IDをテンプレートに渡す
    """
    return {
        'GA_MEASUREMENT_ID': getattr(settings, 'GA_MEASUREMENT_ID', 'G-XXXXXXXXXX'),
    } 