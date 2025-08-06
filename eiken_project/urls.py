"""
URL configuration for eiken_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.static import serve

def healthz(request):
    return HttpResponse("ok", status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('exams/', include('exams.urls')),
    path('', RedirectView.as_view(url='/exams/', permanent=True)),
    # Google Search Console verification file
    path('google41829dffd897ace8.html', lambda request: serve(request, 'google41829dffd897ace8.html', document_root='.')),
    # Sitemap
    path('sitemap.xml', lambda request: serve(request, 'sitemap.xml', document_root='.')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    path("healthz/", healthz),
]
