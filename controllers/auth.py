import logging
import secrets
import time
from typing import Optional

from utils import hash_password, verify_password
from exceptions import AuthError

logger = logging.getLogger(__name__)

_SESSION_TTL  = 3600
_MAX_ATTEMPTS = 5
_LOCKOUT      = 300

_sessions: dict[str, dict] = {}
_failures: dict[str, list[float]] = {}


def _prune() -> None:
    now  = time.time()
    dead = [t for t, s in _sessions.items() if now - s["ts"] > _SESSION_TTL]
    for t in dead:
        del _sessions[t]


def _locked(username: str) -> bool:
    cutoff = time.time() - _LOCKOUT
    recent = [t for t in _failures.get(username, []) if t > cutoff]
    _failures[username] = recent
    return len(recent) >= _MAX_ATTEMPTS


def login(username: str, password: str,
          stored_digest: str, stored_salt: str) -> str:
    if _locked(username):
        raise AuthError("Account temporarily locked")
    if not verify_password(password, stored_digest, stored_salt):
        _failures.setdefault(username, []).append(time.time())
        raise AuthError("Invalid credentials")
    _prune()
    token = secrets.token_hex(32)
    _sessions[token] = {"username": username, "ts": time.time()}
    logger.info("Login: %s", username)
    return token


def logout(token: str) -> None:
    s = _sessions.pop(token, None)
    if s:
        logger.info("Logout: %s", s["username"])


def whoami(token: str) -> Optional[str]:
    s = _sessions.get(token)
    if not s:
        return None
    if time.time() - s["ts"] > _SESSION_TTL:
        del _sessions[token]
        return None
    return s["username"]


def require_auth(token: str) -> str:
    user = whoami(token)
    if user is None:
        raise AuthError()
    return user


def refresh(token: str) -> str:
    user = require_auth(token)
    logout(token)
    new = secrets.token_hex(32)
    _sessions[new] = {"username": user, "ts": time.time()}
    return new


def session_count() -> int:
    _prune()
    return len(_sessions)
