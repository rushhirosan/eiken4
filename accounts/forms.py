from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import CustomUser
from .recovery import format_recovery_code, normalize_recovery_code

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # emailフィールドをオプションにする
        if 'email' in self.fields:
            self.fields['email'].required = False


class RecoverPasswordForm(forms.Form):
    """ユーザー名 + 復元コード + 新しいパスワードで再設定する。"""

    username = forms.CharField(
        label='ユーザー名',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ユーザー名',
            'autocomplete': 'username',
        }),
    )
    recovery_code = forms.CharField(
        label='復元コード',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ABCD-EFGH',
            'autocomplete': 'off',
            'autocapitalize': 'characters',
            'spellcheck': 'false',
        }),
        help_text='登録時に控えた XXXX-XXXX 形式のコードです。',
    )
    new_password1 = forms.CharField(
        label='新しいパスワード',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '新しいパスワード',
            'autocomplete': 'new-password',
        }),
    )
    new_password2 = forms.CharField(
        label='新しいパスワード（確認）',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '新しいパスワード（確認）',
            'autocomplete': 'new-password',
        }),
    )

    error_messages = {
        'invalid_credentials': 'ユーザー名または復元コードが正しくありません。',
        'password_mismatch': '新しいパスワードが一致しません。',
        'no_recovery_code': 'このアカウントには復元コードが設定されていません。管理者にお問い合わせください。',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def clean_recovery_code(self):
        code = self.cleaned_data.get('recovery_code', '')
        normalized = normalize_recovery_code(code)
        if len(normalized) != 8:
            raise forms.ValidationError('復元コードは8文字（XXXX-XXXX）です。')
        return format_recovery_code(normalized)

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get('username')
        recovery_code = cleaned.get('recovery_code')
        password1 = cleaned.get('new_password1')
        password2 = cleaned.get('new_password2')

        if password1 and password2 and password1 != password2:
            self.add_error('new_password2', self.error_messages['password_mismatch'])

        if not username or not recovery_code:
            return cleaned

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(self.error_messages['invalid_credentials'])

        if not user.has_recovery_code():
            raise forms.ValidationError(self.error_messages['no_recovery_code'])

        if not user.check_recovery_code(recovery_code):
            raise forms.ValidationError(self.error_messages['invalid_credentials'])

        if password1:
            try:
                validate_password(password1, user=user)
            except DjangoValidationError as exc:
                self.add_error('new_password1', exc)

        self.user = user
        return cleaned

    def save(self):
        """パスワードを更新し、復元コードを再発行して平文を返す。"""
        if self.user is None:
            raise ValueError('フォームが未検証です')
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        new_code = self.user.set_recovery_code(save=False)
        self.user.save(update_fields=['password', 'recovery_code_hash'])
        return self.user, new_code
