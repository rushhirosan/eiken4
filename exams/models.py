from django.db import models
from accounts.models import CustomUser
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

class Exam(models.Model):
    """試験モデル"""
    title = models.CharField(max_length=200, verbose_name='試験タイトル')
    description = models.TextField(blank=True, verbose_name='説明')
    exam_type = models.CharField(max_length=50, choices=[
        ('regular', '通常問題'),
        ('listening', 'リスニング問題'),
    ], default='regular')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class Question(models.Model):
    LEVELS = [
        ('4', 'Grade 4'),
        ('3', 'Grade 3'),
        ('2', 'Grade 2'),
        ('1', 'Grade 1'),
        ('pre1', 'Pre-Grade 1'),
    ]
    QUESTION_TYPES = [
        ('grammar_fill', '文法・語彙問題'),
        ('conversation_fill', '会話補充問題'),
        ('word_order', '語順選択問題'),
        ('reading_comprehension', '長文読解問題'),
        ('listening_conversation', 'リスニング第2部: 会話問題'),
        ('listening_illustration', 'リスニング第1部: イラスト問題'),
        ('listening_passage', 'リスニング第3部: 文章問題'),
    ]
    
    level = models.CharField(max_length=10, choices=LEVELS)
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES)
    question_text = models.TextField()
    listening_text = models.TextField(blank=True, null=True, help_text="リスニング問題の音声内容")
    explanation = models.TextField(blank=True, default='')
    passage = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='related_questions')
    identifier = models.CharField(max_length=10, blank=True, help_text='本文の識別子（a, bなど）または問題の識別子（a1, b1など）')
    audio_file = models.CharField(max_length=255, blank=True)  # 音声ファイルのパス
    image_file = models.CharField(max_length=255, blank=True)  # 画像ファイルのパス
    question_number = models.IntegerField(default=1)  # 問題番号
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='question_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.get_question_type_display()} - {self.get_level_display()}"

    def get_question_type_display(self):
        return dict(self.QUESTION_TYPES).get(self.question_type, self.question_type)

    def get_level_display(self):
        return dict(self.LEVELS).get(self.level, self.level)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200, verbose_name='選択肢')
    is_correct = models.BooleanField(default=False, verbose_name='正解')
    order = models.IntegerField(default=0, verbose_name='表示順')

    def __str__(self):
        return f"{self.question.question_text[:30]}... - {self.choice_text}"

class UserAnswer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-answered_at']

    def __str__(self):
        return f"{self.user.username} - {self.question} - {self.selected_choice}"

class ReadingUserAnswer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reading_question = models.ForeignKey('questions.ReadingQuestion', on_delete=models.CASCADE)
    selected_reading_choice = models.ForeignKey('questions.ReadingChoice', on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-answered_at']

    def __str__(self):
        return f"{self.user.username} - {self.reading_question} - {self.selected_reading_choice}"

class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    level = models.IntegerField()
    question_type = models.CharField(max_length=50)
    total_attempts = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    last_attempted = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user', 'level', 'question_type')
    
    @property
    def accuracy_rate(self):
        if self.total_attempts == 0:
            return 0
        return round((self.correct_answers / self.total_attempts) * 100, 1)
    
    def update_progress(self, is_correct):
        self.total_attempts += 1
        if is_correct:
            self.correct_answers += 1
        self.last_attempted = timezone.now()
        self.save()

class DailyProgress(models.Model):
    """日々の学習進捗を記録するモデル"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    level = models.IntegerField()
    question_type = models.CharField(max_length=50)
    questions_attempted = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'date', 'level', 'question_type')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.question_type} - {self.questions_attempted}問"
    
    @property
    def accuracy_rate(self):
        if self.questions_attempted == 0:
            return 0
        return round((self.correct_answers / self.questions_attempted) * 100, 1)

class Feedback(models.Model):
    """ユーザーからのフィードバックを保存するモデル"""
    FEEDBACK_TYPES = [
        ('bug', 'バグ報告'),
        ('feature', '機能要望'),
        ('improvement', '改善提案'),
        ('other', 'その他'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES, verbose_name='フィードバック種別')
    title = models.CharField(max_length=200, verbose_name='タイトル')
    content = models.TextField(verbose_name='内容')
    email = models.EmailField(verbose_name='メールアドレス', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    is_resolved = models.BooleanField(default=False, verbose_name='解決済み')
    
    class Meta:
        verbose_name = 'フィードバック'
        verbose_name_plural = 'フィードバック'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_feedback_type_display()} - {self.title}"
