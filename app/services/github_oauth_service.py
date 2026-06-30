"""
app/services/github_oauth_service.py
─────────────────────────────────────
GitHub OAuth2 connector for the Outreach Platform.
Handles: OAuth flow · token refresh · profile fetch · repo stats.
"""
from __future__ import annotations

import base64
import json
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx
import structlog

log = structlog.get_logger()

SCOPES = [
    "read:user",
    "repo",
    "read:org",
]

_GITHUB_API = "https://api.github.com"
_AUTH_URI = "https://github.com/login/oauth/authorize"
_TOKEN_URI = "https://github.com/login/oauth/access_token"


def get_auth_url(client_id: str, redirect_uri: str, state: str) -> str:
    """Return a GitHub OAuth2 authorization URL."""
    import urllib.parse
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(SCOPES),
        "state": state,
        "allow_signup": "true",
    }
    return f"{_AUTH_URI}?{urllib.parse.urlencode(params)}"


def exchange_code(
    code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> dict:
    """Exchange authorization code for access token."""
    resp = httpx.post(
        _TOKEN_URI,
        headers={"Accept": "application/json"},
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
    
    # GitHub tokens don't expire by default, but handle if they do
    expires_in = data.get("expires_in")
    expires_at = None
    if expires_in:
        expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()
    
    return {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token"),
        "expires_at": expires_at,
        "scopes": data.get("scope", "").split(","),
        "token_type": data.get("token_type", "bearer"),
    }


def get_user_profile(access_token: str) -> dict:
    """Fetch the authenticated user's GitHub profile."""
    resp = httpx.get(
        f"{_GITHUB_API}/user",
        headers={
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
        },
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


def get_user_repos(access_token: str, per_page: int = 100) -> list:
    """Fetch the user's public repos."""
    resp = httpx.get(
        f"{_GITHUB_API}/user/repos?type=owner&sort=updated&per_page={per_page}",
        headers={
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
        },
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


def calculate_repo_stats(repos: list) -> dict:
    """Calculate aggregate stats from repos."""
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    languages = {}
    for r in repos:
        lang = r.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    
    top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "repo_count": len(repos),
        "star_count": total_stars,
        "fork_count": total_forks,
        "top_languages": [lang for lang, _ in top_languages],
    }


async def get_valid_token(connector, enc) -> str:
    """Return a valid access token, refreshing if necessary."""
    from app.services.encryption import EncryptionService
    
    access_token = enc.decrypt(connector.access_token_enc)
    
    # GitHub tokens typically don't expire, but check just in case
    if connector.token_expires and connector.token_expires < datetime.now(timezone.utc):
        if connector.refresh_token_enc:
            refresh_token = enc.decrypt(connector.refresh_token_enc)
            # Note: GitHub doesn't support refresh tokens by default for OAuth apps
            # This is a placeholder for future implementation
            log.warning("GitHub token expired but refresh not supported", user_id=connector.user_id)
            raise ValueError("GitHub token expired. Please reconnect your GitHub account.")
        else:
            raise ValueError("GitHub token expired. Please reconnect your GitHub account.")
    
    return access_token
