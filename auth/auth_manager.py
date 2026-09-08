"""
auth/auth_manager.py — Session & Authentication Manager
========================================================
Mengelola login, logout, register, dan session Streamlit.
"""
from __future__ import annotations

import logging
import re
from functools import lru_cache
from typing import Optional

import streamlit as st

import config
from auth.database import Database
from auth.models import User

logger = logging.getLogger(__name__)

# Regex validasi
_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")
_EMAIL_RE    = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PASSWORD_RE = re.compile(r"^.{8,}$")    # min 8 karakter


@lru_cache(maxsize=1)
def get_db() -> Database:
    """Singleton Database — hanya dibuat sekali per process."""
    return Database()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SESSION HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def init_auth_session() -> None:
    """Inisialisasi session state terkait auth."""
    defaults = {
        "auth_user": None,           # User object jika login
        "auth_page": "chat",         # Halaman aktif: "login"|"chat"|"dashboard"|"admin"
        "auth_error": "",            # Pesan error login/register
        "auth_success": "",          # Pesan sukses
        "first_login_warning": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def get_current_user() -> Optional[User]:
    """Kembalikan user yang sedang login, atau None."""
    return st.session_state.get("auth_user")


def is_logged_in() -> bool:
    return st.session_state.get("auth_user") is not None


def is_admin() -> bool:
    user = get_current_user()
    return user is not None and user.is_admin


def require_login() -> User:
    """
    Pastikan user sudah login. Redirect ke login jika belum.
    Panggil di awal setiap halaman yang butuh auth.

    Returns:
        User yang sedang login.
    """
    user = get_current_user()
    if user is None:
        st.session_state.auth_page = "login"
        st.rerun()
    return user  # type: ignore[return-value]


def require_admin() -> User:
    """
    Pastikan user adalah admin.

    Returns:
        Admin User.
    """
    user = require_login()
    if not user.is_admin:
        st.error("⛔ Akses ditolak. Halaman ini hanya untuk admin.")
        st.stop()
    return user


def navigate_to(page: str) -> None:
    """Navigasi ke halaman tertentu."""
    st.session_state.auth_page = page
    st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AUTH MANAGER CLASS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AuthManager:
    """
    High-level authentication manager.

    Semua aksi auth melewati class ini agar session state
    dan logging konsisten.
    """

    def __init__(self) -> None:
        self._db = get_db()

    # ── Login / Logout ────────────────────────────────────────────

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Proses login user.

        Returns:
            (success, error_message)
        """
        if not username.strip() or not password:
            return False, "Username dan password tidak boleh kosong."

        user = self._db.verify_password(username.strip(), password)
        if user is None:
            # Cek apakah user ada tapi nonaktif
            existing = self._db.get_user_by_username(username.strip())
            if existing and not existing.is_active:
                return False, "Akun Anda telah dinonaktifkan. Hubungi admin."
            return False, "Username atau password salah."

        # Sukses login
        st.session_state.auth_user = user
        st.session_state.auth_page = "dashboard"
        st.session_state.auth_error = ""

        # Update last_login
        self._db.update_last_login(user.id)
        self._db.log_activity(user.id, user.username, "login")

        # Warning jika masih pakai password default
        if (user.is_admin and
                user.username == config.ADMIN_USERNAME):
            st.session_state.first_login_warning = True

        logger.info("User '%s' logged in.", user.username)
        return True, ""

    def logout(self) -> None:
        """Logout user dan bersihkan session."""
        user = get_current_user()
        if user:
            self._db.log_activity(user.id, user.username, "logout")
            logger.info("User '%s' logged out.", user.username)

        # Bersihkan semua session state terkait
        keys_to_clear = [
            "auth_user", "auth_page", "auth_error", "auth_success",
            "messages", "chain", "first_login_warning",
        ]
        for k in keys_to_clear:
            st.session_state.pop(k, None)

        st.session_state.auth_page = "login"

    # ── Register ─────────────────────────────────────────────────

    def register(
        self,
        username: str,
        email: str,
        password: str,
        confirm_password: str,
        role: str = "user",
    ) -> tuple[bool, str]:
        """
        Registrasi user baru.

        Returns:
            (success, error_message)
        """
        # Validasi input
        username = username.strip()
        email    = email.strip().lower()

        if not _USERNAME_RE.match(username):
            return False, "Username harus 3–32 karakter, hanya huruf, angka, underscore."
        if not _EMAIL_RE.match(email):
            return False, "Format email tidak valid."
        if not _PASSWORD_RE.match(password):
            return False, "Password minimal 8 karakter."
        if password != confirm_password:
            return False, "Konfirmasi password tidak cocok."

        try:
            user = self._db.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
            )
        except ValueError as e:
            return False, str(e)

        self._db.log_activity(user.id, user.username, "register")
        logger.info("New user registered: '%s' (role=%s)", username, role)
        return True, f"Akun '{username}' berhasil dibuat!"

    # ── Password Management ───────────────────────────────────────

    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str,
        confirm_new: str,
    ) -> tuple[bool, str]:
        """Ganti password user (memerlukan password lama)."""
        user = self._db.get_user_by_id(user_id)
        if not user:
            return False, "User tidak ditemukan."

        # Verifikasi password lama
        verified = self._db.verify_password(user.username, old_password)
        if not verified:
            return False, "Password lama tidak benar."

        if not _PASSWORD_RE.match(new_password):
            return False, "Password baru minimal 8 karakter."
        if new_password != confirm_new:
            return False, "Konfirmasi password tidak cocok."
        if old_password == new_password:
            return False, "Password baru harus berbeda dari yang lama."

        self._db.update_password(user_id, new_password)
        self._db.log_activity(user_id, user.username, "change_password")
        st.session_state.first_login_warning = False
        return True, "Password berhasil diubah!"

    def admin_reset_password(
        self,
        target_user_id: int,
        new_password: str,
    ) -> tuple[bool, str]:
        """Admin reset password user lain (tanpa verifikasi password lama)."""
        if not _PASSWORD_RE.match(new_password):
            return False, "Password minimal 8 karakter."

        user = self._db.get_user_by_id(target_user_id)
        if not user:
            return False, "User tidak ditemukan."

        self._db.update_password(target_user_id, new_password)
        admin = get_current_user()
        if admin:
            self._db.log_activity(
                admin.id, admin.username, "change_password",
                f"Reset password for user '{user.username}'"
            )
        return True, f"Password '{user.username}' berhasil di-reset!"

    # ── Log Activity Helpers ──────────────────────────────────────

    def log_query(self, question: str) -> None:
        """Catat aktivitas query."""
        user = get_current_user()
        if user:
            self._db.log_activity(user.id, user.username, "query",
                                  question[:120])
            self._db.increment_queries(user.id)

    def log_upload(self, filename: str, chunks: int, pages: int, chars: int) -> None:
        """Catat upload dokumen + simpan doc stats."""
        user = get_current_user()
        if user:
            self._db.log_activity(user.id, user.username, "upload", filename)
            self._db.add_doc_stat(user.id, filename, chunks, pages, chars)

    def log_delete_doc(self, filename: str) -> None:
        """Catat penghapusan dokumen."""
        user = get_current_user()
        if user:
            self._db.log_activity(user.id, user.username, "delete_doc", filename)
            self._db.remove_doc_stat(user.id, filename)
