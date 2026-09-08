"""
app.py — SiberkaRAG Main Application (with Auth)
=================================================
NotebookLM-style RAG app + autentikasi + dashboard + admin panel.

Cara menjalankan:
    streamlit run app.py

Prasyarat:
    1. pip install -r requirements.txt
    2. cp .env.example .env  → isi GOOGLE_CLOUD_PROJECT
    3. gcloud auth application-default login
"""
from __future__ import annotations

import logging
import sys
from typing import Any

import streamlit as st
from dotenv import load_dotenv

# ── Setup logging ─────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# ── Load .env ─────────────────────────────────────────────────────
load_dotenv()

# ── Page Config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="SiberkaRAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Local imports ─────────────────────────────────────────────────
import config
from auth.auth_manager import (
    AuthManager,
    init_auth_session,
    get_current_user,
    is_logged_in,
    is_admin,
    navigate_to,
    get_db,
)
from rag.document_processor import process_uploaded_file, ProcessedDocument
from rag.vector_store import get_vsm_for_user, VectorStoreManager
from rag.chain import RAGChain
from ui.styles import get_glass_css
from ui.components import (
    render_hero,
    render_user_message,
    render_ai_message,
    render_source_details,
    render_doc_item,
    render_empty_chat,
    render_no_docs,
    render_stats_row,
    render_sidebar_logo,
    render_typing_indicator,
    render_nav_sidebar,
)
from pages.login_page import render_login_page
from pages.dashboard_page import render_dashboard_page
from pages.admin_page import render_admin_page


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SESSION STATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _init_session() -> None:
    """Inisialisasi semua session state."""
    init_auth_session()
    rag_defaults: dict[str, Any] = {
        "messages": [],
        "chain": None,
        "processing_file": False,
    }
    for k, v in rag_defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BACKEND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@st.cache_resource(show_spinner=False)
def _get_auth() -> AuthManager:
    """Singleton AuthManager."""
    return AuthManager()


def _get_chain_for_user(vsm: VectorStoreManager) -> RAGChain:
    """Kembalikan RAGChain dari session state, rebuild jika perlu."""
    if st.session_state.chain is None:
        st.session_state.chain = RAGChain(vsm)
    return st.session_state.chain


def _check_config() -> tuple[bool, str]:
    if config.GOOGLE_CLOUD_PROJECT == "your-project-id":
        return False, (
            "⚠️ **GOOGLE_CLOUD_PROJECT** belum dikonfigurasi!\n\n"
            "Salin `.env.example` ke `.env` dan isi `GOOGLE_CLOUD_PROJECT`."
        )
    return True, ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DOCUMENT UPLOAD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _handle_file_upload(
    uploaded_file,
    vsm: VectorStoreManager,
    auth: AuthManager,
) -> bool:
    """Proses file yang diunggah."""
    user = get_current_user()
    if not user:
        return False

    try:
        file_bytes = uploaded_file.read()
        filename   = uploaded_file.name

        # Cek kuota
        db = get_db()
        doc_stats = db.get_doc_stats(user.id)
        if len(doc_stats) >= user.doc_quota:
            st.error(
                f"❌ Kuota dokumen Anda sudah penuh ({user.doc_quota} dokumen). "
                "Hapus dokumen lama atau hubungi admin untuk meningkatkan kuota."
            )
            return False

        # Cek duplikat
        existing_names = {d["filename"] for d in doc_stats}
        if filename in existing_names:
            st.warning(f"📄 **{filename}** sudah ada di knowledge base Anda.")
            return False

        with st.spinner(f"🔄 Memproses **{filename}**..."):
            progress_bar = st.progress(0, text="📖 Membaca dokumen...")
            processed: ProcessedDocument = process_uploaded_file(file_bytes, filename)
            progress_bar.progress(40, text="🔢 Membuat embeddings...")

            from rag.vector_store import DocumentInfo as DI
            doc_info = DI(
                filename=processed.filename,
                file_hash=processed.file_hash,
                chunk_count=len(processed.chunks),
                total_chars=processed.total_chars,
                total_pages=processed.total_pages,
            )
            vsm.add_documents(processed.chunks, doc_info)
            progress_bar.progress(80, text="💾 Menyimpan...")

            # Log aktivitas + update stats DB
            auth.log_upload(
                filename=processed.filename,
                chunks=len(processed.chunks),
                pages=processed.total_pages,
                chars=processed.total_chars,
            )

            # Rebuild chain dengan retriever baru
            st.session_state.chain = None
            progress_bar.progress(100, text="✅ Selesai!")

        st.success(
            f"✅ **{filename}** berhasil diproses!\n"
            f"📊 {processed.total_pages} halaman · {len(processed.chunks)} chunks"
        )
        return True

    except ValueError as e:
        st.error(f"❌ {e}")
        return False
    except Exception as e:
        logger.exception("Error processing '%s': %s", uploaded_file.name, e)
        st.error(f"❌ Terjadi kesalahan: {e}")
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHAT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _handle_user_query(
    question: str,
    vsm: VectorStoreManager,
    auth: AuthManager,
) -> None:
    """Proses query pengguna dan tampilkan respons."""
    user = get_current_user()

    st.session_state.messages.append({
        "role": "user",
        "content": question,
        "sources": [],
    })
    render_user_message(question)

    if vsm.collection_count() == 0:
        answer = (
            "⚠️ Belum ada dokumen yang diunggah. "
            "Silakan upload PDF, TXT, atau DOCX di sidebar terlebih dahulu."
        )
        st.session_state.messages.append({
            "role": "assistant", "content": answer, "sources": [],
        })
        render_ai_message(answer)
        return

    typing_placeholder = st.empty()
    with typing_placeholder:
        render_typing_indicator()

    try:
        chain = _get_chain_for_user(vsm)
        answer, sources = chain.ask_with_sources(question)
        typing_placeholder.empty()

        # Log query ke DB
        auth.log_query(question)

        st.session_state.messages.append({
            "role": "assistant", "content": answer, "sources": sources,
        })
        render_ai_message(answer, sources)
        if sources:
            render_source_details(sources)

    except Exception as e:
        typing_placeholder.empty()
        logger.exception("RAGChain error: %s", e)
        err_msg = (
            f"❌ Terjadi kesalahan: {e}\n\n"
            "Pastikan Vertex AI API aktif dan credentials valid."
        )
        st.session_state.messages.append({
            "role": "assistant", "content": err_msg, "sources": [],
        })
        render_ai_message(err_msg)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR — AUTH + NAV
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _render_auth_sidebar(auth: AuthManager) -> None:
    """Sidebar untuk halaman yang butuh auth: nav + user info."""
    user = get_current_user()
    if not user:
        return

    with st.sidebar:
        render_sidebar_logo()
        st.markdown("---")

        # ── User Info ─────────────────────────────────────────────
        st.markdown(f"""
        <div style="
            background: rgba(102,126,234,0.1);
            border: 1px solid rgba(102,126,234,0.2);
            border-radius: 14px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.75rem;
        ">
            <div style="display:flex; align-items:center; gap:0.75rem;">
                <div style="
                    width:38px; height:38px; border-radius:50%;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    display:flex; align-items:center; justify-content:center;
                    font-size:1.2rem; flex-shrink:0;
                ">{user.avatar_emoji}</div>
                <div>
                    <div style="font-size:0.9rem; font-weight:700;
                         color:rgba(255,255,255,0.95);">{user.display_name}</div>
                    <div style="font-size:0.72rem; color:rgba(255,255,255,0.4);">
                        {'👑 Administrator' if user.is_admin else '👤 User'} · {user.email}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Navigation ────────────────────────────────────────────
        current_page = st.session_state.get("auth_page", "chat")

        nav_items = [
            ("📊 Dashboard", "dashboard"),
            ("💬 Chat (RAG)", "chat"),
        ]
        if user.is_admin:
            nav_items.append(("👑 Admin Panel", "admin"))

        for label, page_key in nav_items:
            is_active = current_page == page_key
            btn_style = (
                "background: linear-gradient(135deg,#667eea,#764ba2);"
                if is_active else ""
            )
            if st.button(
                label,
                key=f"nav_{page_key}",
                use_container_width=True,
            ):
                navigate_to(page_key)

        st.markdown("---")

        # ── Logout ────────────────────────────────────────────────
        if st.button("🚪 Logout", use_container_width=True, key="btn_logout"):
            auth.logout()
            st.rerun()

        # ── Project Info ──────────────────────────────────────────
        st.markdown(
            f"<div style='position:absolute; bottom:1rem; left:0; right:0; text-align:center;"
            f" font-size:0.65rem; color:rgba(255,255,255,0.2);'>"
            f"{config.GOOGLE_CLOUD_PROJECT} · {config.GOOGLE_CLOUD_REGION}"
            f"</div>",
            unsafe_allow_html=True,
        )


def _render_chat_sidebar(vsm: VectorStoreManager, auth: AuthManager) -> None:
    """Bagian tambahan di sidebar khusus untuk halaman Chat."""
    user = get_current_user()
    if not user:
        return

    with st.sidebar:
        st.markdown("---")

        # Upload section
        st.markdown(
            "<p style='font-size:0.82rem; font-weight:600; "
            "color:rgba(255,255,255,0.65); text-transform:uppercase; "
            "letter-spacing:0.1em; margin-bottom:0.5rem;'>📤 Upload Dokumen</p>",
            unsafe_allow_html=True,
        )

        db = get_db()
        doc_stats = db.get_doc_stats(user.id)
        quota_pct = len(doc_stats) / user.doc_quota if user.doc_quota > 0 else 0
        st.progress(quota_pct, text=f"Kuota: {len(doc_stats)}/{user.doc_quota}")

        uploaded_file = st.file_uploader(
            "Upload",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=False,
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            if st.button("⚡ Proses Dokumen", use_container_width=True):
                success = _handle_file_upload(uploaded_file, vsm, auth)
                if success:
                    st.rerun()

        st.markdown("---")

        # Documents list
        st.markdown(
            "<p style='font-size:0.82rem; font-weight:600; "
            "color:rgba(255,255,255,0.65); text-transform:uppercase; "
            "letter-spacing:0.1em; margin-bottom:0.5rem;'>📚 Dokumen Saya</p>",
            unsafe_allow_html=True,
        )

        vsm_docs = vsm.list_documents()
        if not vsm_docs:
            render_no_docs()
        else:
            for doc in vsm_docs:
                render_doc_item(doc.filename, doc.total_pages, doc.chunk_count)
                if st.button("🗑️ Hapus", key=f"del_{doc.filename}",
                             use_container_width=False):
                    vsm.delete_document(doc.filename)
                    auth.log_delete_doc(doc.filename)
                    st.session_state.chain = None
                    st.rerun()

        st.markdown("---")

        # Settings expander
        with st.expander("⚙️ Pengaturan", expanded=False):
            st.markdown(
                f"<div style='font-size:0.78rem; color:rgba(255,255,255,0.5);'>"
                f"🤖 Model: <b style='color:#a78bfa;'>{config.GEMINI_MODEL}</b><br>"
                f"🔢 Embeddings: <b style='color:#a78bfa;'>{config.EMBEDDING_MODEL}</b><br>"
                f"📦 Chunk Size: <b style='color:#a78bfa;'>{config.CHUNK_SIZE}</b><br>"
                f"🔍 Top-K: <b style='color:#a78bfa;'>{config.TOP_K_RETRIEVAL}</b>"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🔄 Reset Percakapan", use_container_width=True):
                st.session_state.messages = []
                if st.session_state.chain:
                    st.session_state.chain.clear_memory()
                st.rerun()

            if st.button("🗑️ Hapus Semua Dokumen", use_container_width=True):
                # Hapus semua dokumen user
                for doc in vsm_docs:
                    vsm.delete_document(doc.filename)
                    auth.log_delete_doc(doc.filename)
                vsm.clear_all()
                st.session_state.chain = None
                st.session_state.messages = []
                st.warning("Semua dokumen dihapus.")
                st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHAT PAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _render_chat_page(auth: AuthManager) -> None:
    """Render halaman chat RAG utama."""
    user = get_current_user()
    if not user:
        navigate_to("login")

    # Dapatkan VSM per-user
    vsm = get_vsm_for_user(user)  # type: ignore[arg-type]

    # Render chat sidebar terlebih dahulu
    _render_chat_sidebar(vsm, auth)

    # ── Header ────────────────────────────────────────────────────
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 1.8rem;
            font-weight: 800;
            margin: 0;
        ">💬 Chat dengan Dokumen Anda</h2>
    </div>
    """, unsafe_allow_html=True)

    # Cek konfigurasi Vertex AI
    config_ok, config_error = _check_config()
    if not config_ok:
        st.error(config_error)
        return

    # Stats row
    db = get_db()
    doc_stats = db.get_doc_stats(user.id)  # type: ignore[union-attr]
    render_stats_row(
        total_docs=len(doc_stats),
        total_vectors=vsm.collection_count(),
        total_messages=len(st.session_state.messages),
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            render_empty_chat()

            # Suggested questions jika ada dokumen
            if doc_stats:
                st.markdown("---")
                st.markdown(
                    "<p style='font-size:0.82rem; color:rgba(255,255,255,0.5);"
                    " font-weight:600; text-transform:uppercase; letter-spacing:0.1em;'>"
                    "💡 Pertanyaan yang Bisa Anda Coba</p>",
                    unsafe_allow_html=True,
                )
                suggestions = [
                    "Apa poin-poin utama dari dokumen ini?",
                    "Buat ringkasan singkat dari semua dokumen.",
                    "Apa kesimpulan yang bisa diambil?",
                    "Jelaskan konsep paling penting yang disebutkan.",
                ]
                cols = st.columns(2)
                for i, s in enumerate(suggestions):
                    with cols[i % 2]:
                        if st.button(s, key=f"sugg_{i}", use_container_width=True):
                            _handle_user_query(s, vsm, auth)
                            st.rerun()
        else:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    render_user_message(msg["content"])
                else:
                    render_ai_message(msg["content"], msg.get("sources"))
                    if msg.get("sources"):
                        render_source_details(msg["sources"])

    # Chat input
    st.markdown("<br>", unsafe_allow_html=True)
    if question := st.chat_input(
        placeholder="💬 Tanya apa saja tentang dokumen Anda...",
    ):
        _handle_user_query(question, vsm, auth)
        st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN ROUTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main() -> None:
    # 1. Inject CSS
    st.markdown(get_glass_css(), unsafe_allow_html=True)

    # 2. Init session
    _init_session()

    # 3. Singleton AuthManager
    auth = _get_auth()

    # 4. Routing berdasarkan halaman aktif
    current_page = st.session_state.get("auth_page", "login")

    # ── Halaman Login (tidak perlu auth) ──────────────────────────
    if not is_logged_in() or current_page == "login":
        render_login_page(auth)
        return

    # ── Semua halaman lain butuh login ────────────────────────────
    # Render sidebar navigasi
    _render_auth_sidebar(auth)

    # Route ke halaman yang sesuai
    if current_page == "dashboard":
        render_dashboard_page(auth)

    elif current_page == "chat":
        _render_chat_page(auth)

    elif current_page == "admin":
        render_admin_page(auth)

    else:
        # Fallback ke dashboard
        navigate_to("dashboard")


if __name__ == "__main__":
    main()
