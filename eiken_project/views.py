from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from eiken_project.next_learning import (
    decorated_next_learning_by_level,
    resources_page_sections,
)

CANONICAL_ORIGIN = 'https://eiken-practice.com'
_CANONICAL_REDIRECT_HOSTS = frozenset({
    'eiken-practice.com',
    'www.eiken-practice.com',
    'eiken-app.fly.dev',
})


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
    show_next_learning = getattr(settings, 'SHOW_NEXT_LEARNING', False)
    context = {
        'show_next_learning': show_next_learning,
    }
    if show_next_learning:
        if request.user.is_authenticated:
            primary_url = reverse('exams:exam_list')
            primary_label = 'このサイトで練習を続ける'
        else:
            primary_url = reverse('signup')
            primary_label = 'このサイトで練習を始める'
        context.update({
            'next_learning_by_level': decorated_next_learning_by_level(),
            'next_learning_primary_url': primary_url,
            'next_learning_primary_label': primary_label,
        })
    return render(request, 'guides.html', context)


def resources(request):
    """級別の学習リソース一覧（Phase B）。ローカル確認用フラグがオフなら 404。"""
    if not getattr(settings, 'SHOW_NEXT_LEARNING', False):
        raise Http404('学習リソースページは現在公開していません。')

    if request.user.is_authenticated:
        primary_url = reverse('exams:exam_list')
        primary_label = 'このサイトで練習を続ける'
    else:
        primary_url = reverse('signup')
        primary_label = 'このサイトで練習を始める'

    return render(
        request,
        'resources.html',
        {
            'sections': resources_page_sections(),
            'primary_internal_url': primary_url,
            'primary_internal_label': primary_label,
            'show_next_learning': True,
        },
    )


def privacy_policy(request):
    """プライバシーポリシー（アフィリエイト表記の表示可否を渡す）"""
    return render(
        request,
        'privacy_policy.html',
        {
            'show_next_learning': getattr(settings, 'SHOW_NEXT_LEARNING', False),
        },
    )


def slashless_canonical_redirect(target_path: str):
    """末尾スラッシュ無し → 正規 URL への 301。

    本番ホストでは絶対 URL（GSC Redirect error 対策）。
    ローカルは相対 Location のまま（本番ドメインへ飛ばさない）。
    """

    def _view(request):
        host = request.META.get('HTTP_HOST', '').split(':')[0].lower()
        if host in _CANONICAL_REDIRECT_HOSTS:
            return HttpResponsePermanentRedirect(f'{CANONICAL_ORIGIN}{target_path}')
        return HttpResponsePermanentRedirect(target_path)

    return _view
