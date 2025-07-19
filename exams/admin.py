from django.contrib import admin
from .models import Question, Choice, UserAnswer, ReadingUserAnswer, Feedback

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'level', 'question_type', 'created_at')
    list_filter = ('level', 'question_type', 'created_at')
    search_fields = ('question_text',)
    inlines = [ChoiceInline]

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'choice_text', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('choice_text',)

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'selected_choice', 'is_correct', 'answered_at')
    list_filter = ('user', 'answered_at', 'is_correct')
    search_fields = ('user__username', 'question__question_text')

@admin.register(ReadingUserAnswer)
class ReadingUserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'reading_question', 'selected_reading_choice', 'is_correct', 'answered_at')
    list_filter = ('user', 'answered_at', 'is_correct')
    search_fields = ('user__username', 'reading_question__question_text')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('feedback_type', 'title', 'user', 'email', 'created_at', 'is_resolved')
    list_filter = ('feedback_type', 'is_resolved', 'created_at')
    search_fields = ('title', 'content', 'user__username', 'email')
    readonly_fields = ('created_at',)
    list_editable = ('is_resolved',)
    
    fieldsets = (
        ('基本情報', {
            'fields': ('feedback_type', 'title', 'user', 'email')
        }),
        ('内容', {
            'fields': ('content',)
        }),
        ('管理', {
            'fields': ('is_resolved', 'created_at')
        }),
    )
