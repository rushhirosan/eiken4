from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from exams.provenance import (
    PROVENANCE_BLOCKED,
    PROVENANCE_CHOICES,
    PROVENANCE_ORIGINAL,
    ProvenanceManager,
)

class ReadingPassage(models.Model):
    LEVELS = [
        ('5', 'Grade 5'),
        ('4', 'Grade 4'),
        ('3', 'Grade 3'),
        ('2', 'Grade 2'),
        ('1', 'Grade 1'),
        ('pre1', 'Pre-Grade 1'),
    ]
    
    text = models.TextField()
    level = models.CharField(max_length=10, choices=LEVELS, default='4')
    identifier = models.CharField(max_length=1, default='a', help_text='Passage identifier (a, b, c)')
    provenance = models.CharField(
        max_length=20,
        choices=PROVENANCE_CHOICES,
        default=PROVENANCE_BLOCKED,
        db_index=True,
        help_text='公開は original のみ。既定は blocked（明示した新規自作だけ original）',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ProvenanceManager()

    def __str__(self):
        return f"Passage {self.identifier}"

class ReadingQuestion(models.Model):
    passage = models.ForeignKey(ReadingPassage, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_number = models.IntegerField()  # a1, a2, ... の順番
    explanation = models.TextField(blank=True, default='')
    study_points = models.JSONField(
        null=True,
        blank=True,
        help_text='学習ポイント（category / title / keys のdict）。ノート・振り返り用',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question {self.question_number} for Passage {self.passage.id}"

    def study_point_badge_class(self):
        from exams.models import Question

        category = (self.study_points or {}).get('category', '')
        return Question.STUDY_POINT_BADGE_CLASSES.get(category, 'bg-secondary')

class ReadingChoice(models.Model):
    question = models.ForeignKey(ReadingQuestion, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField()

    def __str__(self):
        return f"Choice {self.order} for Question {self.question.id}"

class GrammarFillQuestion(models.Model):
    LEVELS = [
        ('5', 'Grade 5'),
        ('4', 'Grade 4'),
        ('3', 'Grade 3'),
        ('2', 'Grade 2'),
        ('1', 'Grade 1'),
        ('pre1', 'Pre-Grade 1'),
    ]
    
    question_text = models.TextField()
    level = models.CharField(max_length=10, choices=LEVELS, default='4')
    question_number = models.IntegerField()
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Grammar Fill Question {self.question_number}"

class GrammarFillChoice(models.Model):
    question = models.ForeignKey(GrammarFillQuestion, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField()

    def __str__(self):
        return f"Choice {self.order} for Question {self.question.id}"

class ListeningQuestion(models.Model):
    LEVELS = [
        ('5', 'Grade 5'),
        ('4', 'Grade 4'),
        ('3', 'Grade 3'),
        ('2', 'Grade 2'),
        ('1', 'Grade 1'),
        ('pre1', 'Pre-Grade 1'),
    ]
    
    question_text = models.CharField(max_length=200)
    image = models.CharField(max_length=200)  # 静的ファイルのパスを保存
    audio = models.CharField(max_length=200)  # 静的ファイルのパスを保存
    correct_answer = models.CharField(max_length=200)
    explanation = models.TextField(blank=True, default='')
    level = models.CharField(max_length=10, choices=LEVELS, default='4')
    provenance = models.CharField(
        max_length=20,
        choices=PROVENANCE_CHOICES,
        default=PROVENANCE_BLOCKED,
        db_index=True,
        help_text='公開は original のみ。既定は blocked（明示した新規自作だけ original）',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ProvenanceManager()

    def __str__(self):
        return self.question_text

class ListeningChoice(models.Model):
    question = models.ForeignKey(ListeningQuestion, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField()

    def __str__(self):
        return f"Choice {self.order} for Question {self.question.id}"

class ListeningUserAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(ListeningQuestion, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=200)
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return f"{self.user.username}'s answer to {self.question.question_text}" 