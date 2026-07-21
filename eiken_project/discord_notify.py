"""Discord webhook notifications for operational events."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 5
_CONTENT_PREVIEW_CHARS = 500


def send_discord_message(
    content: str | None = None,
    *,
    embeds: list[dict[str, Any]] | None = None,
) -> bool:
    """Post a message to the configured Discord webhook.

    Returns True on success. Missing webhook or network errors are logged
    and do not raise — callers must not break user flows on notify failure.
    """
    webhook_url = getattr(settings, 'DISCORD_WEBHOOK_URL', '') or ''
    if not webhook_url:
        return False

    payload: dict[str, Any] = {}
    if content:
        payload['content'] = content
    if embeds:
        payload['embeds'] = embeds
    if not payload:
        return False

    data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        webhook_url,
        data=data,
        headers={'Content-Type': 'application/json', 'User-Agent': 'eiken-practice/1.0'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
            # Discord returns 204 No Content on success
            return 200 <= getattr(response, 'status', 200) < 300
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        logger.warning('Discord webhook notify failed: %s', exc)
        return False


def notify_user_registered(*, username: str, ip: str | None = None) -> bool:
    """Notify that a new user registered in production."""
    fields = [
        {'name': 'ユーザー名', 'value': username, 'inline': True},
    ]
    if ip:
        fields.append({'name': 'IP', 'value': ip, 'inline': True})

    return send_discord_message(
        embeds=[
            {
                'title': '新規ユーザー登録',
                'color': 0x57F287,  # green
                'fields': fields,
            }
        ]
    )


def notify_feedback_created(
    *,
    username: str,
    feedback_type_label: str,
    title: str,
    content: str,
    email: str | None = None,
) -> bool:
    """Notify that user feedback was submitted."""
    preview = content.strip()
    if len(preview) > _CONTENT_PREVIEW_CHARS:
        preview = preview[:_CONTENT_PREVIEW_CHARS] + '…'

    fields = [
        {'name': 'ユーザー', 'value': username or '(不明)', 'inline': True},
        {'name': '種別', 'value': feedback_type_label, 'inline': True},
        {'name': 'タイトル', 'value': title[:200] or '(無題)'},
        {'name': '内容', 'value': preview or '(空)'},
    ]
    if email:
        fields.append({'name': '連絡先メール', 'value': email, 'inline': True})

    return send_discord_message(
        embeds=[
            {
                'title': 'フィードバック起票',
                'color': 0x5865F2,  # blurple
                'fields': fields,
            }
        ]
    )
