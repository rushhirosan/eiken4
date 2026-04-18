from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('', views.exam_list, name='exam_list'),
    path('level/<str:level>/', views.question_list, name='question_list_by_level'),
    path('exam/<int:exam_id>/', views.question_list, name='question_list_by_exam'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('submit/<int:question_id>/', views.submit_answer, name='submit_answer'),
    path('submit-reading/<str:level>/', views.submit_reading_comprehension, name='submit_reading_comprehension'),
    path('submit-answers/<str:level>/', views.submit_answers, name='submit_answers'),
    path('results/<str:level>/<str:question_type>/', views.answer_results, name='answer_results'),
    path('progress/', views.progress_view, name='progress'),
    path('clear-progress/', views.clear_progress, name='clear_progress'),
    path('feedback/', views.feedback_form, name='feedback_form'),
    path('feedback/success/', views.feedback_success, name='feedback_success'),
] 