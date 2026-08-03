import json
from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe

from eiken_project.guide_topics import get_guide_topic, iter_guide_topics
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
        'guide_topics_by_level': {
            '5': [t for t in iter_guide_topics() if t['level'] == '5'],
            '4': [t for t in iter_guide_topics() if t['level'] == '4'],
            '3': [t for t in iter_guide_topics() if t['level'] == '3'],
        },
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


def guide_topic(request, slug: str):
    """級×パートの公開ガイド詳細（SEO用）"""
    topic = get_guide_topic(slug)
    if topic is None:
        raise Http404('ガイドが見つかりません。')

    related_topics = []
    for related_slug in topic['related_slugs']:
        related = get_guide_topic(related_slug)
        if related is not None:
            related_topics.append(related)

    if request.user.is_authenticated:
        cta_url = f"{reverse('exams:exam_list')}?level={topic['level']}"
        cta_label = f"{topic['level_label']}の練習を続ける"
    else:
        cta_url = reverse('signup')
        cta_label = '無料で練習を始める'

    page_url = f"{CANONICAL_ORIGIN}/guides/{topic['slug']}/"
    article_json_ld = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': topic['h1'],
        'description': topic['meta_description'],
        'inLanguage': 'ja',
        'mainEntityOfPage': page_url,
        'author': {'@type': 'Organization', 'name': 'Eiken Practice'},
        'publisher': {
            '@type': 'Organization',
            'name': 'Eiken Practice',
            'url': CANONICAL_ORIGIN,
        },
    }
    breadcrumb_json_ld = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {
                '@type': 'ListItem',
                'position': 1,
                'name': 'トップ',
                'item': f'{CANONICAL_ORIGIN}/',
            },
            {
                '@type': 'ListItem',
                'position': 2,
                'name': '学習の進め方',
                'item': f'{CANONICAL_ORIGIN}/guides/',
            },
            {
                '@type': 'ListItem',
                'position': 3,
                'name': f"{topic['level_label']} {topic['topic_label']}",
                'item': page_url,
            },
        ],
    }
    faq_json_ld = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {
                '@type': 'Question',
                'name': faq['question'],
                'acceptedAnswer': {
                    '@type': 'Answer',
                    'text': faq['answer'],
                },
            }
            for faq in topic['faqs']
        ],
    }

    return render(
        request,
        'guide_topic.html',
        {
            'topic': topic,
            'related_topics': related_topics,
            'cta_url': cta_url,
            'cta_label': cta_label,
            'article_json_ld': mark_safe(json.dumps(article_json_ld, ensure_ascii=False)),
            'breadcrumb_json_ld': mark_safe(json.dumps(breadcrumb_json_ld, ensure_ascii=False)),
            'faq_json_ld': mark_safe(json.dumps(faq_json_ld, ensure_ascii=False)),
        },
    )


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


def guide_topic_slashless_redirect(request, slug: str):
    """級×パートガイドの末尾スラッシュ無し URL を正規 URL へ 301。"""
    target_path = f'/guides/{slug}/'
    host = request.META.get('HTTP_HOST', '').split(':')[0].lower()
    if host in _CANONICAL_REDIRECT_HOSTS:
        return HttpResponsePermanentRedirect(f'{CANONICAL_ORIGIN}{target_path}')
    return HttpResponsePermanentRedirect(target_path)
