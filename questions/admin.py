from django.contrib import admin
from .models import ReadingPassage, ReadingQuestion, ReadingChoice

@admin.register(ReadingPassage)
class ReadingPassageAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    search_fields = ('text',)

@admin.register(ReadingQuestion)
class ReadingQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'passage', 'question_number', 'created_at')
    list_filter = ('passage',)
    search_fields = ('question_text',)

@admin.register(ReadingChoice)
class ReadingChoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'choice_text', 'is_correct', 'order')
    list_filter = ('question', 'is_correct')
    search_fields = ('choice_text',) 