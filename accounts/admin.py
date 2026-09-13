from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('has_recovery_code_display',)
    readonly_fields = getattr(UserAdmin, 'readonly_fields', ()) + ('has_recovery_code_display',)

    def has_recovery_code_display(self, obj):
        return obj.has_recovery_code()

    has_recovery_code_display.boolean = True
    has_recovery_code_display.short_description = '復元コード'

    fieldsets = UserAdmin.fieldsets + (
        ('復元コード', {
            'fields': ('has_recovery_code_display',),
            'description': '平文の復元コードは保存していません。再発行が必要な場合はユーザーに再ログインしてもらうか、パスワード再設定後に新しいコードが表示されます。',
        }),
    )
