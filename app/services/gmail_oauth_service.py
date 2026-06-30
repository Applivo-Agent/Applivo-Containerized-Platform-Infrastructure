"""
app/services/gmail_oauth_service.py
─────────────────────────────────────
Gmail OAuth2 connector for the Outreach Platform.
Handles: OAuth flow · token refresh · email sending · reply polling.
"""
from __future__ import annotations

import base64
import json
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import httpx
import structlog

log = structlog.get_logger()

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
]

_GMAIL_API = "https://gmail.googleapis.com/gmail/v1/users/me"
_TOKEN_URI  = "https://oauth2.googleapis.com/token"
_AUTH_URI   = "https://accounts.google.com/o/oauth2/v2/auth"


# ── OAuth flow ─────────────────────────────────────────────────────────────────

def get_auth_url(client_id: str, redirect_uri: str, state: str) -> str:
    """Return a Gmail OAuth2 consent-page URL."""
    import urllib.parse
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
        "include_granted_scopes": "true",
    }
    return f"{_AUTH_URI}?{urllib.parse.urlencode(params)}"


def exchange_code(
    code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> dict:
    """Exchange authorization code for access + refresh tokens."""
    resp = httpx.post(
        _TOKEN_URI,
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    expires_in = int(data.get("expires_in", 3600))
    return {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token"),
        "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat(),
        "scopes": data.get("scope", "").split(),
    }


def refresh_access_token(
    refresh_token: str,
    client_id: str,
    client_secret: str,
) -> tuple[str, datetime]:
    """Refresh a Gmail access token. Returns (new_access_token, new_expiry)."""
    resp = httpx.post(
        _TOKEN_URI,
        data={
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
        },
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    expires_in = int(data.get("expires_in", 3600))
    expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    return data["access_token"], expiry


def get_userinfo(access_token: str) -> dict:
    """Fetch the authenticated user's Google profile (email, name)."""
    resp = httpx.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


# ── Gmail profile / history ────────────────────────────────────────────────────

def get_profile(access_token: str) -> dict:
    """Return Gmail profile: {emailAddress, historyId, messagesTotal, ...}."""
    resp = httpx.get(
        f"{_GMAIL_API}/profile",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def get_history(access_token: str, start_history_id: str) -> list[dict]:
    """Fetch Gmail history records (messageAdded) since start_history_id."""
    resp = httpx.get(
        f"{_GMAIL_API}/history",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"startHistoryId": start_history_id, "historyTypes": "messageAdded"},
        timeout=20,
    )
    if resp.status_code == 404:
        return []
    resp.raise_for_status()
    return resp.json().get("history", [])


def get_thread(access_token: str, thread_id: str) -> dict:
    """Fetch all messages in a Gmail thread (metadata only)."""
    resp = httpx.get(
        f"{_GMAIL_API}/threads/{thread_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"format": "metadata", "metadataHeaders": ["Subject", "From", "Date", "To"]},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def get_message_body(access_token: str, message_id: str) -> str:
    """Fetch plain-text body of a Gmail message."""
    resp = httpx.get(
        f"{_GMAIL_API}/messages/{message_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"format": "full"},
        timeout=15,
    )
    resp.raise_for_status()
    payload = resp.json().get("payload", {})
    return _extract_body(payload)


def _extract_body(payload: dict) -> str:
    """Recursively extract plain-text body from a Gmail message payload."""
    mime_type = payload.get("mimeType", "")
    if mime_type == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
    for part in payload.get("parts", []):
        result = _extract_body(part)
        if result:
            return result
    return ""


# ── Email sending ──────────────────────────────────────────────────────────────

def _build_mime(
    to: str,
    subject: str,
    body: str,
    from_email: Optional[str] = None,
) -> bytes:
    msg = MIMEMultipart("alternative")
    msg["To"] = to
    msg["Subject"] = subject
    if from_email:
        msg["From"] = from_email
    msg.attach(MIMEText(body, "plain"))
    return msg.as_bytes()


def send_email(
    access_token: str,
    to: str,
    subject: str,
    body: str,
    thread_id: Optional[str] = None,
    from_email: Optional[str] = None,
) -> dict:
    """Send an email via Gmail API. Returns {message_id, thread_id}."""
    raw = base64.urlsafe_b64encode(_build_mime(to, subject, body, from_email)).decode()
    payload: dict = {"raw": raw}
    if thread_id:
        payload["threadId"] = thread_id

    resp = httpx.post(
        f"{_GMAIL_API}/messages/send",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return {"message_id": data.get("id"), "thread_id": data.get("threadId")}


# ── Token helpers ──────────────────────────────────────────────────────────────

def is_token_expired(expires_at: Optional[datetime], buffer_minutes: int = 5) -> bool:
    """True if the token expires within buffer_minutes from now."""
    if not expires_at:
        return True
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) >= (expires_at - timedelta(minutes=buffer_minutes))


async def get_valid_token(connector, enc_service) -> str:
    """
    Return a valid access token for the given OutreachEmailConnector.
    Refreshes automatically if the token is expired.
    Persists the new token to the connector object (caller must commit the session).
    """
    from app.core.config import settings

    access_token = enc_service.decrypt(connector.access_token_enc) if connector.access_token_enc else None
    refresh_token_str = enc_service.decrypt(connector.refresh_token_enc) if connector.refresh_token_enc else None

    if not access_token or is_token_expired(connector.token_expires):
        if not refresh_token_str:
            raise ValueError("No refresh token available — user must reconnect Gmail")
        new_token, new_expiry = refresh_access_token(
            refresh_token_str,
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
        )
        connector.access_token_enc = enc_service.encrypt(new_token)
        connector.token_expires = new_expiry
        return new_token

    return access_token
