"""
pages/login_page.py — Halaman Login & Register
================================================
Centered glass card dengan tab Login dan Register.
"""
from __future__ import annotations

import streamlit as st

import config
from auth.auth_manager import AuthManager, get_current_user, navigate_to
from ui.components import render_hero


def render_login_page(auth: AuthManager) -> None:
    """Render halaman login/register glass morphism."""

    # Jika sudah login, langsung redirect
    if get_current_user():
        navigate_to("dashboard")

    render_hero()

    # Container tengah
    _, col, _ = st.columns([1, 1.8, 1])

    with col:
        # Glass card wrapper
        st.markdown("""
        <div class="glass-card" style="padding: 2rem 2rem 1.5rem;">
            <div style="text-align:center; margin-bottom:1.5rem;">
                <div style="font-size:2.5rem; margin-bottom:0.3rem;">🔐</div>
                <div style="font-size:1.1rem; font-weight:700;
                     color:rgba(255,255,255,0.9);">Selamat Datang</div>
                <div style="font-size:0.82rem; color:rgba(255,255,255,0.45);
                     margin-top:0.2rem;">Masuk ke akun SiberkaRAG Anda</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Tab Login / Register
        if config.ALLOW_REGISTER:
            tab_login, tab_register = st.tabs(["🔑 Login", "✨ Daftar Akun"])
        else:
            tab_login = st.container()
            tab_register = None

        # ── TAB LOGIN ─────────────────────────────────────────────
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)

            with st.form("form_login", clear_on_submit=False):
                username = st.text_input(
                    "Username",
                    placeholder="Masukkan username Anda",
                    key="login_username",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Masukkan password Anda",
                    key="login_password",
                )

                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button(
                    "🚀 Masuk",
                    use_container_width=True,
                )

                if submit:
                    if not username or not password:
                        st.error("⚠️ Username dan password wajib diisi.")
                    else:
                        with st.spinner("Memverifikasi..."):
                            ok, err = auth.login(username, password)
                        if ok:
                            st.success("✅ Login berhasil! Mengalihkan...")
                            st.rerun()
                        else:
                            st.error(f"❌ {err}")

            # Info akun default
            st.markdown(f"""
            <div style="
                background: rgba(102,126,234,0.08);
                border: 1px solid rgba(102,126,234,0.2);
                border-radius: 10px;
                padding: 0.7rem 1rem;
                font-size: 0.78rem;
                color: rgba(255,255,255,0.5);
                margin-top: 0.5rem;
                text-align: center;
            ">
                💡 Default admin: <b style="color:#a78bfa;">
                {config.ADMIN_USERNAME}</b> /
                <b style="color:#a78bfa;">
                {config.DEFAULT_ADMIN_PASSWORD}</b>
            </div>
            """, unsafe_allow_html=True)

        # ── TAB REGISTER ─────────────────────────────────────────
        if config.ALLOW_REGISTER and tab_register is not None:
            with tab_register:
                st.markdown("<br>", unsafe_allow_html=True)

                with st.form("form_register", clear_on_submit=True):
                    reg_username = st.text_input(
                        "Username",
                        placeholder="3–32 karakter, huruf/angka/underscore",
                        key="reg_username",
                    )
                    reg_email = st.text_input(
                        "Email",
                        placeholder="contoh@email.com",
                        key="reg_email",
                    )
                    reg_password = st.text_input(
                        "Password",
                        type="password",
                        placeholder="Minimal 8 karakter",
                        key="reg_password",
                    )
                    reg_confirm = st.text_input(
                        "Konfirmasi Password",
                        type="password",
                        placeholder="Ulangi password",
                        key="reg_confirm",
                    )

                    st.markdown("<br>", unsafe_allow_html=True)
                    reg_submit = st.form_submit_button(
                        "✨ Buat Akun",
                        use_container_width=True,
                    )

                    if reg_submit:
                        ok, msg = auth.register(
                            reg_username, reg_email,
                            reg_password, reg_confirm,
                        )
                        if ok:
                            st.success(f"✅ {msg} Silakan login.")
                        else:
                            st.error(f"❌ {msg}")

        # Footer
        st.markdown("""
        <div style="text-align:center; margin-top:1.5rem;
             font-size:0.7rem; color:rgba(255,255,255,0.25);">
            SiberkaRAG · Vertex AI · Gemini · ChromaDB
        </div>
        """, unsafe_allow_html=True)
