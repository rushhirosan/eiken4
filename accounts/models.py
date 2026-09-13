from django.contrib.auth.models import AbstractUser
from django.db import models

from .recovery import (
    check_recovery_code,
    generate_recovery_code,
    hash_recovery_code,
)


class CustomUser(AbstractUser):
    preferred_exam_level = models.CharField(
        max_length=10,
        blank=True,
        default='',
        help_text='問題一覧で最後に選んだ級（5 / 4 / 3）。ログイン後の表示に使う。',
    )
    recovery_code_hash = models.CharField(
        max_length=128,
        blank=True,
        default='',
        help_text='パスワード再設定用の復元コード（ハッシュ保存）。平文は保存しない。',
    )
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_set",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set",
        related_query_name="customuser",
    )

    def has_recovery_code(self) -> bool:
        return bool(self.recovery_code_hash)

    def set_recovery_code(self, code: str | None = None, *, save: bool = True) -> str:
        """復元コードを発行してハッシュ保存し、平文を返す（画面表示用・一度きり）。"""
        plain = code or generate_recovery_code()
        self.recovery_code_hash = hash_recovery_code(plain)
        if save:
            self.save(update_fields=['recovery_code_hash'])
        return plain

    def check_recovery_code(self, code: str) -> bool:
        return check_recovery_code(code, self.recovery_code_hash)
