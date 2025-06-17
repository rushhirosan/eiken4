from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [
    path('reading/', views.reading_comprehension_list_view, name='reading_comprehension_list'),
    path('reading/<int:passage_id>/', views.reading_comprehension_view, name='reading_comprehension'),
    path('reading-comprehension/<int:passage_id>/', views.reading_comprehension_detail_view, name='reading_comprehension_detail'),
    path('listening/', views.listening_question_list, name='listening_question_list'),
    path('listening/<int:question_id>/', views.listening_question_detail, name='listening_question_detail'),
    # ... existing code ...
] 