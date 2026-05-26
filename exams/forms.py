from django import forms
from .models import Feedback

FEEDBACK_CONTENT_MAX_LENGTH = 5000

class FeedbackForm(forms.ModelForm):
    """フィードバックフォーム"""

    # ボット向け（人間は触らない想定）
    website = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'tabindex': '-1',
        }),
    )

    class Meta:
        model = Feedback
        fields = ['feedback_type', 'title', 'content', 'email']
        widgets = {
            'feedback_type': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'フィードバックの種類を選択してください'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'タイトルを入力してください（例：問題が表示されない）'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'maxlength': FEEDBACK_CONTENT_MAX_LENGTH,
                'placeholder': '詳細な内容を入力してください。問題の状況や改善したい点を具体的にお聞かせください。',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': '返信が必要な場合はメールアドレスを入力してください（任意）'
            })
        }
        labels = {
            'feedback_type': 'フィードバック種別',
            'title': 'タイトル',
            'content': '内容',
            'email': 'メールアドレス（任意）'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].max_length = FEEDBACK_CONTENT_MAX_LENGTH

    def clean_website(self):
        value = (self.cleaned_data.get('website') or '').strip()
        if value:
            raise forms.ValidationError('送信できませんでした。')
        return value

    def clean_title(self):
        return (self.cleaned_data.get('title') or '').strip()

    def clean_content(self):
        return (self.cleaned_data.get('content') or '').strip()