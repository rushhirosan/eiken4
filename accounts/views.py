from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
import logging
from eiken_project.discord_notify import notify_user_registered
from .forms import CustomUserCreationForm, RecoverPasswordForm

logger = logging.getLogger(__name__)

SESSION_RECOVERY_CODE = 'pending_recovery_code'
SESSION_RECOVERY_NEXT = 'recovery_code_next'
SESSION_RECOVERY_CONTEXT = 'recovery_code_context'


def get_client_ip(request):
    """クライアントのIPアドレスを取得"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def _stash_recovery_code(request, plain_code, *, next_url, context='signup'):
    """平文復元コードをセッションに一時保存し、表示ページへ誘導する。"""
    request.session[SESSION_RECOVERY_CODE] = plain_code
    request.session[SESSION_RECOVERY_NEXT] = next_url
    request.session[SESSION_RECOVERY_CONTEXT] = context


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            plain_code = user.set_recovery_code()
            login(request, user)
            ip_address = get_client_ip(request)
            logger.info(f'新規ユーザー登録成功: username={user.username}, ip={ip_address}')
            notify_user_registered(username=user.username, ip=ip_address)
            _stash_recovery_code(
                request,
                plain_code,
                next_url=reverse('exams:choose_exam_level'),
                context='signup',
            )
            return redirect('recovery_code_reveal')
        else:
            logger.warning(f'新規登録失敗: errors={form.errors}, ip={get_client_ip(request)}')
            print("Form errors:", form.errors)
            print("Form data:", request.POST)
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def recovery_code_reveal(request):
    """登録・再設定後に復元コードを一度だけ表示する。"""
    plain_code = request.session.get(SESSION_RECOVERY_CODE)
    if not plain_code:
        return redirect('login')

    next_url = request.session.get(SESSION_RECOVERY_NEXT) or reverse('login')
    context_key = request.session.get(SESSION_RECOVERY_CONTEXT, 'signup')

    if request.method == 'POST':
        for key in (SESSION_RECOVERY_CODE, SESSION_RECOVERY_NEXT, SESSION_RECOVERY_CONTEXT):
            request.session.pop(key, None)
        return redirect(next_url)

    return render(request, 'accounts/recovery_code_reveal.html', {
        'recovery_code': plain_code,
        'next_url': next_url,
        'context_key': context_key,
    })


@ratelimit(key='ip', rate='5/m', method='POST', block=False)
@require_http_methods(['GET', 'POST'])
def recover_password(request):
    """復元コードでパスワードを再設定する。"""
    if request.user.is_authenticated:
        return redirect('exams:exam_list')

    if request.method == 'POST' and getattr(request, 'limited', False):
        ip_address = get_client_ip(request)
        username = request.POST.get('username', 'unknown')
        logger.warning(
            f'パスワード再設定レート制限超過: username={username}, ip={ip_address}'
        )
        form = RecoverPasswordForm(request.POST)
        form.add_error(
            None,
            '試行回数が多すぎます。しばらく時間をおいてから再度お試しください。',
        )
        return render(request, 'accounts/recover_password.html', {'form': form})

    if request.method == 'POST':
        form = RecoverPasswordForm(request.POST)
        if form.is_valid():
            user, new_code = form.save()
            ip_address = get_client_ip(request)
            logger.info(
                f'復元コードでパスワード再設定: username={user.username}, ip={ip_address}'
            )
            _stash_recovery_code(
                request,
                new_code,
                next_url=reverse('login'),
                context='reset',
            )
            return redirect('recovery_code_reveal')
    else:
        form = RecoverPasswordForm()

    return render(request, 'accounts/recover_password.html', {'form': form})


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class CustomLoginView(LoginView):
    """カスタムログインビュー（ログ記録とレート制限付き）

    レート制限: IPアドレスごとに5分間に5回まで
    ログ記録: 成功/失敗/レート制限超過をすべて記録
    """
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        """ログイン成功時の処理"""
        username = form.cleaned_data.get('username')
        ip_address = get_client_ip(self.request)

        response = super().form_valid(form)

        logger.info(
            f'ログイン成功: username={username}, ip={ip_address}, '
            f'user_agent={self.request.META.get("HTTP_USER_AGENT", "Unknown")}'
        )

        user = self.request.user
        if user.is_authenticated and not user.has_recovery_code():
            plain_code = user.set_recovery_code()
            _stash_recovery_code(
                self.request,
                plain_code,
                next_url=self.get_success_url(),
                context='missing',
            )
            return redirect('recovery_code_reveal')

        return response

    def form_invalid(self, form):
        """ログイン失敗時の処理"""
        username = form.data.get('username', 'unknown')
        ip_address = get_client_ip(self.request)

        logger.warning(
            f'ログイン失敗: username={username}, ip={ip_address}, '
            f'user_agent={self.request.META.get("HTTP_USER_AGENT", "Unknown")}, '
            f'errors={form.errors}'
        )

        return super().form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        """レート制限エラーを処理"""
        try:
            return super().dispatch(request, *args, **kwargs)
        except Ratelimited:
            ip_address = get_client_ip(request)
            username = request.POST.get('username', 'unknown')

            logger.warning(
                f'ログイン試行レート制限超過: username={username}, ip={ip_address}, '
                f'user_agent={request.META.get("HTTP_USER_AGENT", "Unknown")}'
            )

            form = self.get_form()
            form.add_error(None, 'ログイン試行回数が多すぎます。しばらく時間をおいてから再度お試しください。')
            return self.form_invalid(form)
