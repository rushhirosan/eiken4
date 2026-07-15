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


def llms_txt(request):
    """AI向けサイト概要（llms.txt）を配信"""
    path = Path(settings.BASE_DIR) / 'static' / 'llms.txt'
    return HttpResponse(path.read_text(encoding='utf-8'), content_type='text/plain; charset=utf-8')


def about(request):
    """公開のサービス概要・FAQページ"""
    return render(request, 'about.html')


def guides(request):
    """公開の級別学習ガイド（5級・4級・3級）"""
    return render(request, 'guides.html')
