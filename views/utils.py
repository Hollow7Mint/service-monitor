import hashlib
import hmac
import re
import secrets
import string
from datetime import datetime, timezone
from typing import Any, Optional

EMAIL_RE = re.compile(r'^[\w.+-]+@[\w-]+\.[\w.-]+$')


def hash_password(pw: str, salt: Optional[str] = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 200_000)
    return digest.hex(), salt


def verify_password(pw: str, digest: str, salt: str) -> bool:
    computed, _ = hash_password(pw, salt)
    return hmac.compare_digest(computed, digest)


def generate_token(n: int = 32) -> str:
    return "".join(secrets.choice(string.ascii_letters + string.digits)
                   for _ in range(n))


def slugify(text: str, max_len: int = 60) -> str:
    text = text.lower().replace(" ", "-")
    text = re.sub(r"[^\w-]", "", text)
    return text[:max_len].strip("-")


def truncate(text: str, n: int = 120) -> str:
    return text if len(text) <= n else text[:n - 3] + "..."


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("1", "true", "yes", "on")


def chunk(lst: list, size: int) -> list[list]:
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def flatten(nested: list) -> list:
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out
