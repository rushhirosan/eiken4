"""復元コードの生成・検証ヘルパー。"""
import secrets

from django.contrib.auth.hashers import check_password, make_password

# 0/O, 1/I/L を除いた読みやすい文字セット
_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'


def generate_recovery_code() -> str:
    """XXXX-XXXX 形式の復元コードを生成する。"""
    raw = ''.join(secrets.choice(_ALPHABET) for _ in range(8))
    return f'{raw[:4]}-{raw[4:]}'


def normalize_recovery_code(code: str) -> str:
    """入力の空白・ハイフンを除き大文字に揃える。"""
    return ''.join(ch for ch in (code or '').upper() if ch.isalnum())


def hash_recovery_code(code: str) -> str:
    return make_password(normalize_recovery_code(code))


def check_recovery_code(plain_code: str, code_hash: str) -> bool:
    if not code_hash:
        return False
    return check_password(normalize_recovery_code(plain_code), code_hash)


def format_recovery_code(code: str) -> str:
    """正規化したコードを表示用 XXXX-XXXX に整える。"""
    normalized = normalize_recovery_code(code)
    if len(normalized) == 8:
        return f'{normalized[:4]}-{normalized[4:]}'
    return code.strip().upper()
