from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


def _uid() -> str:
    return str(uuid.uuid4())

def _now() -> datetime:
    return datetime.utcnow()


@dataclass
class User:
    name: str
    email: str
    id: str              = field(default_factory=_uid)
    role: str            = "user"
    active: bool         = True
    created_at: datetime = field(default_factory=_now)

    def deactivate(self) -> None:
        self.active = False

    def promote(self, role: str = "admin") -> None:
        self.role = role

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "email": self.email,
            "role": self.role, "active": self.active,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> User:
        return cls(
            id=d.get("id", _uid()), name=d["name"], email=d["email"],
            role=d.get("role", "user"), active=d.get("active", True),
        )


@dataclass
class Record:
    title: str
    owner_id: str
    id: str                        = field(default_factory=_uid)
    tags: list[str]                = field(default_factory=list)
    active: bool                   = True
    created_at: datetime           = field(default_factory=_now)
    updated_at: Optional[datetime] = None

    def touch(self) -> None:
        self.updated_at = _now()

    def add_tag(self, tag: str) -> None:
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        self.tags = [t for t in self.tags if t != tag]

    def update(self, **kw) -> None:
        for k, v in kw.items():
            if hasattr(self, k):
                setattr(self, k, v)
        self.touch()

    def to_dict(self) -> dict:
        return {
            "id": self.id, "title": self.title, "owner_id": self.owner_id,
            "tags": self.tags, "active": self.active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
