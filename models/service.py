import logging
from datetime import datetime, timezone
from typing import Any, Optional

from models import Record, User
import database as db
from exceptions import NotFoundError, ConflictError, ValidationError
from validators import validate, required, is_email, min_len, max_len

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_user(name: str, email: str, role: str = "user") -> User:
    errs = validate({"name": name, "email": email}, {
        "name":  [required, min_len(2), max_len(80)],
        "email": [required, is_email],
    })
    if errs:
        raise ValidationError("input", "; ".join(errs))
    if db.fetch_one("SELECT id FROM users WHERE email = ?", (email,)):
        raise ConflictError(f"Email already registered: {email}")
    user = User(name=name, email=email, role=role)
    db.execute(
        "INSERT INTO users (id, name, email, role, active, created_at) VALUES (?,?,?,?,?,?)",
        (user.id, user.name, user.email, user.role, int(user.active),
         user.created_at.isoformat()),
    )
    logger.info("Created user %s (%s)", user.id, email)
    return user


def get_user(user_id: str) -> User:
    row = db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
    if not row:
        raise NotFoundError("User", user_id)
    return User.from_dict(dict(row))


def list_users(page: int = 1, size: int = 20,
               active_only: bool = True) -> dict[str, Any]:
    sql    = "SELECT * FROM users" + (" WHERE active = 1" if active_only else "")
    sql   += " ORDER BY created_at DESC"
    return db.paginate(sql, page=page, size=size)


def deactivate_user(user_id: str) -> None:
    if not db.execute("UPDATE users SET active = 0 WHERE id = ?", (user_id,)):
        raise NotFoundError("User", user_id)
    logger.info("Deactivated user %s", user_id)


def create_record(title: str, owner_id: str,
                  tags: Optional[list[str]] = None) -> Record:
    errs = validate({"title": title}, {"title": [required, max_len(200)]})
    if errs:
        raise ValidationError("title", errs[0])
    get_user(owner_id)
    rec = Record(title=title, owner_id=owner_id, tags=tags or [])
    db.execute(
        "INSERT INTO records (id, title, owner_id, active, created_at) VALUES (?,?,?,?,?)",
        (rec.id, rec.title, rec.owner_id, 1, rec.created_at.isoformat()),
    )
    if rec.tags:
        db.execute_many(
            "INSERT OR IGNORE INTO tags (record_id, tag) VALUES (?,?)",
            [(rec.id, t) for t in rec.tags],
        )
    logger.info("Created record %s", rec.id)
    return rec


def get_record(record_id: str) -> Record:
    row = db.fetch_one("SELECT * FROM records WHERE id = ?", (record_id,))
    if not row:
        raise NotFoundError("Record", record_id)
    tags = [r["tag"] for r in
            db.fetch_all("SELECT tag FROM tags WHERE record_id = ?", (record_id,))]
    return Record(**{k: row[k] for k in ("id","title","owner_id","active")}, tags=tags)


def delete_record(record_id: str) -> None:
    if not db.execute("UPDATE records SET active = 0 WHERE id = ?", (record_id,)):
        raise NotFoundError("Record", record_id)


def list_records(owner_id: Optional[str] = None,
                 page: int = 1, size: int = 20) -> dict[str, Any]:
    sql = "SELECT * FROM records WHERE active = 1"
    params: tuple = ()
    if owner_id:
        sql += " AND owner_id = ?"
        params = (owner_id,)
    return db.paginate(sql, params, page=page, size=size)
