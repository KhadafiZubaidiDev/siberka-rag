"""
auth/database.py — SQLite Database Layer untuk SiberkaRAG Auth
==============================================================
Mengelola tabel users, activity_log, dan doc_stats.
"""
from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional

import bcrypt

import config
from auth.models import User, ActivityLog

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCHEMA SQL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_SCHEMA = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    email         TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL DEFAULT 'user' CHECK(role IN ('admin','user')),
    is_active     INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT    NOT NULL,
    last_login    TEXT,
    doc_quota     INTEGER NOT NULL DEFAULT 20,
    total_queries INTEGER NOT NULL DEFAULT 0
);

-- Activity log table
CREATE TABLE IF NOT EXISTS activity_log (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    username  TEXT    NOT NULL,
    action    TEXT    NOT NULL,
    detail    TEXT    NOT NULL DEFAULT '',
    timestamp TEXT    NOT NULL
);

-- Document stats per user
CREATE TABLE IF NOT EXISTS doc_stats (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename  TEXT    NOT NULL,
    file_type TEXT    NOT NULL,
    chunks    INTEGER NOT NULL DEFAULT 0,
    pages     INTEGER NOT NULL DEFAULT 0,
    chars     INTEGER NOT NULL DEFAULT 0,
    uploaded_at TEXT  NOT NULL,
    UNIQUE(user_id, filename)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_time  ON activity_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_docstats_user  ON doc_stats(user_id);
"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATABASE CLASS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Database:
    """
    SQLite database manager untuk auth SiberkaRAG.

    Menggunakan context manager untuk koneksi agar thread-safe.
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path or config.DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._ensure_admin()

    # ── Connection ────────────────────────────────────────────────

    @contextmanager
    def _conn(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager untuk koneksi SQLite."""
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ── Init ──────────────────────────────────────────────────────

    def _init_db(self) -> None:
        """Buat schema jika belum ada."""
        with self._conn() as conn:
            conn.executescript(_SCHEMA)
        logger.info("Database initialized at '%s'.", self.db_path)

    def _ensure_admin(self) -> None:
        """Buat akun admin default jika belum ada user sama sekali."""
        with self._conn() as conn:
            count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            if count == 0:
                hashed = bcrypt.hashpw(
                    config.DEFAULT_ADMIN_PASSWORD.encode(),
                    bcrypt.gensalt(rounds=12),
                ).decode()
                now = datetime.utcnow().isoformat()
                conn.execute(
                    """INSERT INTO users
                       (username, email, password_hash, role, is_active, created_at, doc_quota)
                       VALUES (?, ?, ?, 'admin', 1, ?, 100)""",
                    (config.ADMIN_USERNAME, f"{config.ADMIN_USERNAME}@siberka.local", hashed, now),
                )
                logger.warning(
                    "Default admin created: username='%s' password='%s'. "
                    "Segera ganti password setelah login pertama!",
                    config.ADMIN_USERNAME,
                    config.DEFAULT_ADMIN_PASSWORD,
                )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # USER CRUD
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _row_to_user(self, row: sqlite3.Row) -> User:
        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            role=row["role"],
            is_active=bool(row["is_active"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            last_login=(datetime.fromisoformat(row["last_login"])
                        if row["last_login"] else None),
            doc_quota=row["doc_quota"],
            total_queries=row["total_queries"],
        )

    def get_user_by_username(self, username: str) -> Optional[User]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ? COLLATE NOCASE",
                (username,),
            ).fetchone()
        return self._row_to_user(row) if row else None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        return self._row_to_user(row) if row else None

    def get_all_users(self) -> list[User]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM users ORDER BY created_at DESC"
            ).fetchall()
        return [self._row_to_user(r) for r in rows]

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "user",
        doc_quota: int | None = None,
    ) -> User:
        """
        Buat user baru.

        Raises:
            ValueError: Jika username/email sudah digunakan.
        """
        quota = doc_quota if doc_quota is not None else config.DEFAULT_DOC_QUOTA
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
        now = datetime.utcnow().isoformat()

        try:
            with self._conn() as conn:
                conn.execute(
                    """INSERT INTO users
                       (username, email, password_hash, role, is_active, created_at, doc_quota)
                       VALUES (?, ?, ?, ?, 1, ?, ?)""",
                    (username, email, hashed, role, now, quota),
                )
        except sqlite3.IntegrityError as e:
            if "username" in str(e).lower():
                raise ValueError(f"Username '{username}' sudah digunakan.")
            if "email" in str(e).lower():
                raise ValueError(f"Email '{email}' sudah digunakan.")
            raise ValueError(str(e))

        user = self.get_user_by_username(username)
        logger.info("User created: %s (role=%s)", username, role)
        return user  # type: ignore[return-value]

    def update_last_login(self, user_id: int) -> None:
        now = datetime.utcnow().isoformat()
        with self._conn() as conn:
            conn.execute(
                "UPDATE users SET last_login = ? WHERE id = ?", (now, user_id)
            )

    def update_password(self, user_id: int, new_password: str) -> None:
        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt(rounds=12)).decode()
        with self._conn() as conn:
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (hashed, user_id),
            )

    def set_active(self, user_id: int, is_active: bool) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE users SET is_active = ? WHERE id = ?",
                (int(is_active), user_id),
            )

    def set_role(self, user_id: int, role: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE users SET role = ? WHERE id = ?", (role, user_id)
            )

    def set_quota(self, user_id: int, quota: int) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE users SET doc_quota = ? WHERE id = ?", (quota, user_id)
            )

    def increment_queries(self, user_id: int) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE users SET total_queries = total_queries + 1 WHERE id = ?",
                (user_id,),
            )

    def delete_user(self, user_id: int) -> None:
        """Hapus user + semua data terkait (CASCADE)."""
        with self._conn() as conn:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        logger.info("User id=%d deleted.", user_id)

    def verify_password(self, username: str, password: str) -> Optional[User]:
        """
        Verifikasi password user.

        Returns:
            User jika valid dan aktif, None jika tidak.
        """
        user = self.get_user_by_username(username)
        if not user or not user.is_active:
            return None
        if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return user
        return None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ACTIVITY LOG
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def log_activity(
        self,
        user_id: int,
        username: str,
        action: str,
        detail: str = "",
    ) -> None:
        now = datetime.utcnow().isoformat()
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO activity_log (user_id, username, action, detail, timestamp)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, username, action, detail, now),
            )

    def get_user_activity(
        self,
        user_id: int,
        limit: int = 50,
    ) -> list[ActivityLog]:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT * FROM activity_log
                   WHERE user_id = ?
                   ORDER BY timestamp DESC LIMIT ?""",
                (user_id, limit),
            ).fetchall()
        return [self._row_to_activity(r) for r in rows]

    def get_all_activity(self, limit: int = 100) -> list[ActivityLog]:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT * FROM activity_log
                   ORDER BY timestamp DESC LIMIT ?""",
                (limit,),
            ).fetchall()
        return [self._row_to_activity(r) for r in rows]

    def get_query_stats_by_day(self, user_id: int, days: int = 30) -> list[dict]:
        """Kembalikan jumlah query per hari (30 hari terakhir)."""
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT DATE(timestamp) as day, COUNT(*) as count
                   FROM activity_log
                   WHERE user_id = ? AND action = 'query'
                     AND timestamp >= DATE('now', ?)
                   GROUP BY day ORDER BY day""",
                (user_id, f"-{days} days"),
            ).fetchall()
        return [{"day": r["day"], "count": r["count"]} for r in rows]

    def _row_to_activity(self, row: sqlite3.Row) -> ActivityLog:
        return ActivityLog(
            id=row["id"],
            user_id=row["user_id"],
            username=row["username"],
            action=row["action"],
            detail=row["detail"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
        )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # DOC STATS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def add_doc_stat(
        self,
        user_id: int,
        filename: str,
        chunks: int,
        pages: int,
        chars: int,
    ) -> None:
        ext = filename.rsplit(".", 1)[-1].upper() if "." in filename else "FILE"
        now = datetime.utcnow().isoformat()
        with self._conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO doc_stats
                   (user_id, filename, file_type, chunks, pages, chars, uploaded_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, filename, ext, chunks, pages, chars, now),
            )

    def remove_doc_stat(self, user_id: int, filename: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "DELETE FROM doc_stats WHERE user_id = ? AND filename = ?",
                (user_id, filename),
            )

    def get_doc_stats(self, user_id: int) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM doc_stats WHERE user_id = ? ORDER BY uploaded_at DESC",
                (user_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def get_doc_type_distribution(self, user_id: int) -> list[dict]:
        """Distribusi tipe file untuk pie chart."""
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT file_type, COUNT(*) as count
                   FROM doc_stats WHERE user_id = ?
                   GROUP BY file_type""",
                (user_id,),
            ).fetchall()
        return [{"type": r["file_type"], "count": r["count"]} for r in rows]

    def get_system_stats(self) -> dict:
        """Statistik global untuk admin dashboard."""
        with self._conn() as conn:
            total_users   = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            active_users  = conn.execute("SELECT COUNT(*) FROM users WHERE is_active=1").fetchone()[0]
            total_docs    = conn.execute("SELECT COUNT(*) FROM doc_stats").fetchone()[0]
            total_queries = conn.execute("SELECT SUM(total_queries) FROM users").fetchone()[0] or 0
            total_chunks  = conn.execute("SELECT SUM(chunks) FROM doc_stats").fetchone()[0] or 0
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_docs": total_docs,
            "total_queries": total_queries,
            "total_chunks": total_chunks,
        }
