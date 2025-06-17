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
        ('listening_passage', 'リスニング第3部: 文章問題'),
        ('listening_illustration', 'リスニング第2部: イラスト問題'),
        ('listening_conversation', 'リスニング第1部: 会話問題'),
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
