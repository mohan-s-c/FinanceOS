"""Auth + RBAC (Phase 4).

Dependency-free for the research build: a seeded user directory, opaque in-memory
bearer tokens, and FastAPI dependencies for role gating. Roles: analyst (default,
least-privilege but functional) and controller (governance — tunes autonomy and
signs off high-value items). Swap for a real IdP/JWT before pilot (see SECURITY.md).
"""
from __future__ import annotations

import secrets
from typing import Optional

from fastapi import Depends, Header, HTTPException

USERS: dict[str, dict] = {
    "dana": {"username": "dana", "name": "Dana Okafor", "role": "analyst", "initials": "DO"},
    "morgan": {"username": "morgan", "name": "Morgan Reyes", "role": "controller", "initials": "MR"},
}

_tokens: dict[str, str] = {}  # token -> username


def login(username: str) -> tuple[str, dict]:
    user = USERS.get(username)
    if not user:
        raise KeyError(username)
    tok = secrets.token_hex(16)
    _tokens[tok] = username
    return tok, user


def _user_for_token(tok: str) -> Optional[dict]:
    un = _tokens.get(tok)
    return USERS.get(un) if un else None


def current_user(authorization: Optional[str] = Header(None), x_role: Optional[str] = Header(None)) -> dict:
    """Resolve the caller. Bearer token wins; X-Role is a dev fallback; otherwise the
    default least-privilege analyst so the app stays usable without a login step."""
    if authorization and authorization.lower().startswith("bearer "):
        u = _user_for_token(authorization.split(" ", 1)[1])
        if u:
            return u
    if x_role in ("analyst", "controller"):
        return {"username": x_role, "name": x_role.title(), "role": x_role, "initials": x_role[:2].upper()}
    return USERS["dana"]


def require_controller(user: dict = Depends(current_user)) -> dict:
    if user["role"] != "controller":
        raise HTTPException(status_code=403, detail="This action requires the Controller role.")
    return user
