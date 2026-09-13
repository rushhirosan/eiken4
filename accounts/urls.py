from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('recovery-code/', views.recovery_code_reveal, name='recovery_code_reveal'),
    path('recover/', views.recover_password, name='recover_password'),
]
