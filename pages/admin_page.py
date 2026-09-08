"""
pages/admin_page.py — Panel Manajemen User (Admin Only)
========================================================
Tabel user dengan aksi: aktifkan, nonaktifkan, reset password,
set kuota, ganti role, dan hapus user beserta datanya.
"""
from __future__ import annotations

import streamlit as st

import config
from auth.auth_manager import AuthManager, get_db, get_current_user, require_admin
from auth.models import User


def render_admin_page(auth: AuthManager) -> None:
    """Render halaman admin — manajemen user."""
    current_admin = require_admin()
    db = get_db()

    # ── Header ────────────────────────────────────────────────────
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h2 style="
            background: linear-gradient(135deg, #f093fb, #f5576c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 1.8rem;
            font-weight: 800;
            margin: 0;
        ">👑 Panel Admin</h2>
        <p style="color:rgba(255,255,255,0.45); font-size:0.87rem; margin:0.3rem 0 0;">
            Kelola seluruh user, kuota, dan akses sistem SiberkaRAG
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────
    tab_users, tab_create, tab_activity = st.tabs([
        "👥 Daftar User",
        "➕ Buat User Baru",
        "🕐 Log Aktivitas",
    ])

    # ── TAB 1: USER LIST ─────────────────────────────────────────
    with tab_users:
        _render_user_list(db, auth, current_admin)

    # ── TAB 2: CREATE USER ────────────────────────────────────────
    with tab_create:
        _render_create_user_form(auth)

    # ── TAB 3: ACTIVITY LOG ───────────────────────────────────────
    with tab_activity:
        _render_activity_log(db)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1 — USER LIST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _render_user_list(db, auth: AuthManager, current_admin: User) -> None:
    users = db.get_all_users()

    st.markdown(
        f"<p style='color:rgba(255,255,255,0.5); font-size:0.83rem;'>"
        f"Total: <b>{len(users)}</b> user terdaftar</p>",
        unsafe_allow_html=True,
    )

    for user in users:
        _render_user_card(user, db, auth, current_admin)


def _render_user_card(
    user: User,
    db,
    auth: AuthManager,
    current_admin: User,
) -> None:
    """Render satu card user dengan aksi-aksi."""
    is_self = user.id == current_admin.id

    status_badge = (
        '<span style="background:rgba(67,233,123,0.15);border:1px solid rgba(67,233,123,0.4);'
        'color:#43e97b;border-radius:100px;padding:0.15rem 0.6rem;font-size:0.72rem;'
        'font-weight:600;">● Aktif</span>'
        if user.is_active else
        '<span style="background:rgba(245,87,108,0.15);border:1px solid rgba(245,87,108,0.4);'
        'color:#f5576c;border-radius:100px;padding:0.15rem 0.6rem;font-size:0.72rem;'
        'font-weight:600;">● Nonaktif</span>'
    )
    role_badge = (
        '<span style="background:rgba(240,147,251,0.15);border:1px solid rgba(240,147,251,0.4);'
        'color:#f093fb;border-radius:100px;padding:0.15rem 0.6rem;font-size:0.72rem;'
        'font-weight:600;">👑 Admin</span>'
        if user.is_admin else
        '<span style="background:rgba(102,126,234,0.15);border:1px solid rgba(102,126,234,0.4);'
        'color:#a78bfa;border-radius:100px;padding:0.15rem 0.6rem;font-size:0.72rem;'
        'font-weight:600;">👤 User</span>'
    )

    last_login = (
        user.last_login.strftime("%d %b %Y %H:%M")
        if user.last_login else "Belum pernah"
    )
    created = user.created_at.strftime("%d %b %Y")

    st.markdown(f"""
    <div class="glass-card" style="padding:1.2rem 1.5rem; margin-bottom:0.8rem;">
        <div style="display:flex; align-items:center; gap:1rem; flex-wrap:wrap;">
            <div style="font-size:2rem;">{user.avatar_emoji}</div>
            <div style="flex:1; min-width:160px;">
                <div style="font-size:1rem; font-weight:700;
                     color:rgba(255,255,255,0.95);">
                    {user.username}
                    {"&nbsp;<small style='font-size:0.7rem;color:rgba(255,255,255,0.3);'>(You)</small>" if is_self else ""}
                </div>
                <div style="font-size:0.78rem; color:rgba(255,255,255,0.45); margin-top:0.15rem;">
                    {user.email}
                </div>
            </div>
            <div style="display:flex; gap:0.4rem; flex-wrap:wrap; align-items:center;">
                {status_badge} {role_badge}
            </div>
        </div>
        <div style="display:flex; gap:2rem; margin-top:0.8rem; padding-top:0.8rem;
             border-top:1px solid rgba(255,255,255,0.06); flex-wrap:wrap;">
            <div>
                <div style="font-size:0.7rem; color:rgba(255,255,255,0.35);
                     text-transform:uppercase; letter-spacing:0.08em;">Terdaftar</div>
                <div style="font-size:0.82rem; color:rgba(255,255,255,0.7);">{created}</div>
            </div>
            <div>
                <div style="font-size:0.7rem; color:rgba(255,255,255,0.35);
                     text-transform:uppercase; letter-spacing:0.08em;">Login Terakhir</div>
                <div style="font-size:0.82rem; color:rgba(255,255,255,0.7);">{last_login}</div>
            </div>
            <div>
                <div style="font-size:0.7rem; color:rgba(255,255,255,0.35);
                     text-transform:uppercase; letter-spacing:0.08em;">Total Query</div>
                <div style="font-size:0.82rem; color:rgba(255,255,255,0.7);">{user.total_queries:,}</div>
            </div>
            <div>
                <div style="font-size:0.7rem; color:rgba(255,255,255,0.35);
                     text-transform:uppercase; letter-spacing:0.08em;">Kuota Dokumen</div>
                <div style="font-size:0.82rem; color:rgba(255,255,255,0.7);">{user.doc_quota}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Action Buttons ────────────────────────────────────────────
    with st.expander(f"⚙️ Kelola {user.username}", expanded=False):
        col1, col2, col3 = st.columns(3)

        # Toggle aktif/nonaktif
        if not is_self:
            with col1:
                if user.is_active:
                    if st.button(
                        "🚫 Nonaktifkan",
                        key=f"deact_{user.id}",
                        use_container_width=True,
                    ):
                        db.set_active(user.id, False)
                        db.log_activity(
                            current_admin.id, current_admin.username,
                            "admin_action",
                            f"Deactivated user '{user.username}'"
                        )
                        st.success(f"User '{user.username}' dinonaktifkan.")
                        st.rerun()
                else:
                    if st.button(
                        "✅ Aktifkan",
                        key=f"act_{user.id}",
                        use_container_width=True,
                    ):
                        db.set_active(user.id, True)
                        db.log_activity(
                            current_admin.id, current_admin.username,
                            "admin_action",
                            f"Activated user '{user.username}'"
                        )
                        st.success(f"User '{user.username}' diaktifkan.")
                        st.rerun()

            # Toggle role
            with col2:
                new_role = "user" if user.is_admin else "admin"
                role_label = "👤 Jadikan User" if user.is_admin else "👑 Jadikan Admin"
                if st.button(role_label, key=f"role_{user.id}", use_container_width=True):
                    db.set_role(user.id, new_role)
                    db.log_activity(
                        current_admin.id, current_admin.username,
                        "admin_action",
                        f"Changed role of '{user.username}' to {new_role}"
                    )
                    st.success(f"Role '{user.username}' diubah ke {new_role}.")
                    st.rerun()

        # Kuota dokumen
        with col3:
            new_quota = st.number_input(
                "Kuota Dokumen",
                min_value=1, max_value=500,
                value=user.doc_quota,
                key=f"quota_{user.id}",
            )
            if st.button("💾 Simpan Kuota", key=f"savequota_{user.id}",
                         use_container_width=True):
                db.set_quota(user.id, int(new_quota))
                st.success("Kuota disimpan!")
                st.rerun()

        st.markdown("---")

        # Reset password
        col_pw1, col_pw2 = st.columns(2)
        with col_pw1:
            new_pw = st.text_input(
                "Password Baru",
                type="password",
                placeholder="Min. 8 karakter",
                key=f"pw_{user.id}",
            )
        with col_pw2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"🔑 Reset Password",
                         key=f"resetpw_{user.id}",
                         use_container_width=True):
                if new_pw:
                    ok, msg = auth.admin_reset_password(user.id, new_pw)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.error("Masukkan password baru terlebih dahulu.")

        # Hapus user
        if not is_self:
            st.markdown("---")
            st.markdown(
                "<p style='font-size:0.78rem; color:rgba(245,87,108,0.7);'>"
                "⚠️ Zona Berbahaya — aksi di bawah tidak dapat dibatalkan</p>",
                unsafe_allow_html=True,
            )
            confirm_key = f"confirm_del_{user.id}"
            if confirm_key not in st.session_state:
                st.session_state[confirm_key] = False

            if not st.session_state[confirm_key]:
                if st.button(
                    f"🗑️ Hapus User '{user.username}'",
                    key=f"del_{user.id}",
                    use_container_width=True,
                    type="primary",
                ):
                    st.session_state[confirm_key] = True
                    st.rerun()
            else:
                st.warning(f"Yakin hapus **{user.username}** beserta semua datanya?")
                c_yes, c_no = st.columns(2)
                with c_yes:
                    if st.button("Ya, Hapus!", key=f"yes_{user.id}",
                                 use_container_width=True, type="primary"):
                        # Hapus ChromaDB collection user
                        try:
                            from rag.vector_store import get_vsm_for_user
                            vsm = get_vsm_for_user(user)
                            vsm.clear_all()
                        except Exception:
                            pass
                        db.delete_user(user.id)
                        db.log_activity(
                            current_admin.id, current_admin.username,
                            "admin_action",
                            f"Deleted user '{user.username}'"
                        )
                        st.session_state.pop(confirm_key, None)
                        st.success(f"User '{user.username}' dihapus.")
                        st.rerun()
                with c_no:
                    if st.button("Batal", key=f"no_{user.id}",
                                 use_container_width=True):
                        st.session_state[confirm_key] = False
                        st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2 — CREATE USER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _render_create_user_form(auth: AuthManager) -> None:
    """Form buat user baru oleh admin."""
    st.markdown(
        "<p style='color:rgba(255,255,255,0.6); font-size:0.87rem;'>"
        "Buat akun user baru. Admin dapat mengatur role dan kuota dokumen.</p>",
        unsafe_allow_html=True,
    )

    with st.form("form_admin_create_user", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input(
                "Username*", placeholder="3–32 karakter"
            )
            new_password = st.text_input(
                "Password*", type="password", placeholder="Min. 8 karakter"
            )
        with col2:
            new_email = st.text_input(
                "Email*", placeholder="contoh@email.com"
            )
            confirm_pw = st.text_input(
                "Konfirmasi Password*", type="password"
            )

        col3, col4 = st.columns(2)
        with col3:
            new_role = st.selectbox(
                "Role",
                options=["user", "admin"],
                index=0,
                format_func=lambda x: "👑 Admin" if x == "admin" else "👤 User",
            )
        with col4:
            new_quota = st.number_input(
                "Kuota Dokumen",
                min_value=1, max_value=500,
                value=config.DEFAULT_DOC_QUOTA,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "➕ Buat User",
            use_container_width=True,
        )

        if submitted:
            ok, msg = auth.register(
                username=new_username,
                email=new_email,
                password=new_password,
                confirm_password=confirm_pw,
                role=new_role,
            )
            if ok:
                # Set quota yang dipilih
                user_created = get_db().get_user_by_username(new_username)
                if user_created:
                    get_db().set_quota(user_created.id, int(new_quota))
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3 — ACTIVITY LOG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _render_activity_log(db) -> None:
    """Tampilkan log aktivitas semua user."""
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        filter_user = st.text_input(
            "Filter username", placeholder="Kosongkan untuk semua user"
        )
    with col_f2:
        limit = st.selectbox("Tampilkan", [25, 50, 100, 200], index=1)

    activities = db.get_all_activity(limit=limit)

    if filter_user:
        activities = [a for a in activities
                      if filter_user.lower() in a.username.lower()]

    if not activities:
        st.info("Tidak ada aktivitas yang ditemukan.")
        return

    st.markdown(
        f"<p style='font-size:0.8rem; color:rgba(255,255,255,0.4);'>"
        f"Menampilkan {len(activities)} entri</p>",
        unsafe_allow_html=True,
    )

    for act in activities:
        ts = act.timestamp.strftime("%d %b %Y %H:%M:%S")
        detail_str = f" — {act.detail}" if act.detail else ""
        st.markdown(
            f'<div class="doc-item">'
            f'<span style="font-size:1.1rem;">{act.action_emoji}</span>'
            f'<div style="flex:1;">'
            f'<div class="doc-name">'
            f'<b style="color:#a78bfa;">{act.username}</b> · '
            f'{act.action}{detail_str}'
            f'</div>'
            f'<div class="doc-meta">{ts}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
