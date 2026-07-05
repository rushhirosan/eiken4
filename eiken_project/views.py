from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render


def landing(request):
    """公開ランディングページ（ログイン済みユーザーは試験一覧へ）"""
    if request.user.is_authenticated:
        return redirect('exams:exam_list')
    return render(request, 'landing.html')


def robots_txt(request):
    """ルートで robots.txt を配信"""
    path = Path(settings.BASE_DIR) / 'static' / 'robots.txt'
    return HttpResponse(path.read_text(encoding='utf-8'), content_type='text/plain')
