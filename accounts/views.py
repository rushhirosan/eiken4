from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
import logging
from .forms import CustomUserCreationForm

logger = logging.getLogger(__name__)

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f'新規ユーザー登録成功: username={user.username}, ip={get_client_ip(request)}')
            return redirect('exams:exam_list')
        else:
            # デバッグ情報をログに出力
            logger.warning(f'新規登録失敗: errors={form.errors}, ip={get_client_ip(request)}')
            print("Form errors:", form.errors)
            print("Form data:", request.POST)
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


def get_client_ip(request):
    """クライアントのIPアドレスを取得"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


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
        
        # ログイン処理
        response = super().form_valid(form)
        
        # 成功ログを記録
        logger.info(
            f'ログイン成功: username={username}, ip={ip_address}, '
            f'user_agent={self.request.META.get("HTTP_USER_AGENT", "Unknown")}'
        )
        
        return response
    
    def form_invalid(self, form):
        """ログイン失敗時の処理"""
        username = form.data.get('username', 'unknown')
        ip_address = get_client_ip(self.request)
        
        # 失敗ログを記録
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
            
            # レート制限超過ログを記録
            logger.warning(
                f'ログイン試行レート制限超過: username={username}, ip={ip_address}, '
                f'user_agent={request.META.get("HTTP_USER_AGENT", "Unknown")}'
            )
            
            # エラーメッセージを追加
            form = self.get_form()
            form.add_error(None, 'ログイン試行回数が多すぎます。しばらく時間をおいてから再度お試しください。')
            return self.form_invalid(form)
