from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class CustomUser(AbstractUser):
    # 追加のフィールドが必要な場合はここに追加
    pass
