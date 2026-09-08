"""
auth/models.py — User data model untuk SiberkaRAG
==================================================
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Representasi satu user dalam sistem."""

    id: int
    username: str
    email: str
    password_hash: str
    role: str                        # "admin" | "user"
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    doc_quota: int                   # Maks jumlah dokumen yang bisa diupload
    total_queries: int = 0

    # ── Helper Properties ────────────────────────────────────────

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def display_name(self) -> str:
        return self.username.capitalize()

    @property
    def avatar_emoji(self) -> str:
        return "👑" if self.is_admin else "👤"

    @property
    def collection_name(self) -> str:
        """ChromaDB collection name unik per user."""
        # Sanitize username: hanya alfanumerik + underscore
        safe = "".join(c if c.isalnum() else "_" for c in self.username.lower())
        return f"siberka_{safe}_{self.id}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "doc_quota": self.doc_quota,
            "total_queries": self.total_queries,
        }


@dataclass
class ActivityLog:
    """Satu entry log aktivitas user."""

    id: int
    user_id: int
    username: str
    action: str           # "login", "logout", "upload", "query", "delete_doc"
    detail: str
    timestamp: datetime

    @property
    def action_emoji(self) -> str:
        icons = {
            "login": "🔐",
            "logout": "🚪",
            "upload": "📤",
            "query": "💬",
            "delete_doc": "🗑️",
            "register": "✨",
            "change_password": "🔑",
        }
        return icons.get(self.action, "📌")
