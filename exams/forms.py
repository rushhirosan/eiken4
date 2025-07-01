from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    """フィードバックフォーム"""
    
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
                'placeholder': '詳細な内容を入力してください。問題の状況や改善したい点を具体的にお聞かせください。'
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