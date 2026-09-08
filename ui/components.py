"""
ui/components.py — Custom HTML/CSS components untuk SiberkaRAG
==============================================================
Helper functions untuk render elemen UI khusus via st.markdown.
"""
from __future__ import annotations

import html
from typing import Any

import streamlit as st


# ── Hero Header ──────────────────────────────────────────────────

def render_hero() -> None:
    """Tampilkan hero header dengan judul dan badge."""
    st.markdown("""
    <div class="hero-header fade-in">
        <div class="hero-badge">
            ✦ &nbsp; Powered by Google Vertex AI &nbsp; ✦
        </div>
        <h1 class="hero-title">SiberkaRAG</h1>
        <p class="hero-subtitle">
            Tanya apa saja tentang dokumen Anda — seperti NotebookLM,<br>
            didukung Gemini &amp; pencarian semantik.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ── Glass Card ───────────────────────────────────────────────────

def glass_card(content_html: str, extra_class: str = "") -> None:
    """Render konten dalam glass card."""
    st.markdown(
        f'<div class="glass-card {extra_class}">{content_html}</div>',
        unsafe_allow_html=True,
    )


# ── Chat Bubbles ─────────────────────────────────────────────────

def render_user_message(text: str) -> None:
    """Render chat bubble dari pengguna (kanan, ungu gradient)."""
    safe_text = html.escape(text).replace("\n", "<br>")
    st.markdown(f"""
    <div class="chat-user fade-in">
        <div class="bubble">{safe_text}</div>
        <div class="avatar avatar-user">👤</div>
    </div>
    """, unsafe_allow_html=True)


def render_ai_message(
    text: str,
    sources: list[dict[str, Any]] | None = None,
) -> None:
    """
    Render chat bubble dari AI (kiri, glass).

    Args:
        text:    Teks jawaban dari Gemini.
        sources: List source dicts berisi filename, page, excerpt.
    """
    # Render markdown dalam bubble
    safe_text = text.replace("\n", "<br>")

    sources_html = ""
    if sources:
        chips = "".join(
            f'<span class="source-chip">📄 {html.escape(s["filename"])} '
            f'&nbsp;·&nbsp; hal. {s["page"]}</span>'
            for s in sources
        )
        sources_html = f"""
        <div class="sources-section">
            <div class="sources-title">📎 Sumber Referensi</div>
            {chips}
        </div>
        """

    st.markdown(f"""
    <div class="chat-ai fade-in">
        <div class="avatar avatar-ai">🤖</div>
        <div class="bubble">
            {safe_text}
            {sources_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_typing_indicator() -> None:
    """Animasi 'AI sedang mengetik...'"""
    st.markdown("""
    <div class="chat-ai">
        <div class="avatar avatar-ai">🤖</div>
        <div class="bubble">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <span style="color: rgba(255,255,255,0.4); font-size:0.8rem; margin-left:4px;">
                    Gemini sedang berpikir...
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Source Detail Expander ────────────────────────────────────────

def render_source_details(sources: list[dict[str, Any]]) -> None:
    """Tampilkan detail sumber dalam expander yang bisa dibuka."""
    if not sources:
        return

    with st.expander("📚 Lihat Detail Sumber", expanded=False):
        for i, src in enumerate(sources, 1):
            st.markdown(f"""
            <div class="source-card fade-in">
                <div class="source-header">
                    📄 {html.escape(src['filename'])}
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    📖 Halaman {src['page']}
                    &nbsp;&nbsp;|&nbsp;&nbsp;
                    #️⃣ Chunk {src.get('chunk_index', '—')}
                </div>
                <div class="excerpt">"{html.escape(src['excerpt'])}..."</div>
            </div>
            """, unsafe_allow_html=True)


# ── Document Item (Sidebar) ───────────────────────────────────────

def render_doc_item(filename: str, pages: int, chunks: int) -> None:
    """Render satu item dokumen di sidebar."""
    ext = filename.rsplit(".", 1)[-1].upper() if "." in filename else "FILE"
    icons = {"PDF": "📕", "TXT": "📄", "DOCX": "📘"}
    icon = icons.get(ext, "📄")

    short_name = filename if len(filename) <= 28 else filename[:25] + "..."

    st.markdown(f"""
    <div class="doc-item">
        <span class="doc-icon">{icon}</span>
        <div style="flex: 1; min-width: 0;">
            <div class="doc-name" title="{html.escape(filename)}">{html.escape(short_name)}</div>
            <div class="doc-meta">{pages} hal · {chunks} chunks</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Empty State ───────────────────────────────────────────────────

def render_empty_chat() -> None:
    """Tampilkan placeholder saat belum ada percakapan."""
    st.markdown("""
    <div class="empty-state fade-in">
        <span class="empty-icon">💬</span>
        <h3>Mulai Percakapan</h3>
        <p>Upload dokumen di sidebar, lalu tanyakan apa saja.<br>
        Siberka akan menjawab berdasarkan isi dokumen Anda.</p>
    </div>
    """, unsafe_allow_html=True)


def render_no_docs() -> None:
    """Tampilkan placeholder saat belum ada dokumen."""
    st.markdown("""
    <div class="empty-state" style="padding: 2rem 1rem;">
        <span class="empty-icon">📂</span>
        <h3>Belum Ada Dokumen</h3>
        <p>Upload PDF, TXT, atau DOCX<br>untuk memulai.</p>
    </div>
    """, unsafe_allow_html=True)


# ── Stats Row ─────────────────────────────────────────────────────

def render_stats_row(
    total_docs: int,
    total_vectors: int,
    total_messages: int,
) -> None:
    """Tampilkan stats ringkas dalam 3 kolom."""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 Dokumen", total_docs)
    with col2:
        st.metric("🔢 Vectors", f"{total_vectors:,}")
    with col3:
        st.metric("💬 Pesan", total_messages)


# ── Sidebar Logo ─────────────────────────────────────────────────

def render_sidebar_logo() -> None:
    """Header di sidebar."""
    st.markdown("""
    <div style="text-align:center; padding: 0.5rem 0 1.5rem;">
        <div style="
            font-size: 2.5rem;
            filter: drop-shadow(0 0 20px rgba(102,126,234,0.8));
        ">🧠</div>
        <div style="
            font-size: 1.3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea, #f093fb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.02em;
        ">SiberkaRAG</div>
        <div style="
            font-size: 0.72rem;
            color: rgba(255,255,255,0.4);
            margin-top: 0.2rem;
        ">Vertex AI · Gemini · ChromaDB</div>
    </div>
    """, unsafe_allow_html=True)


# ── Nav Sidebar (stub — logic ada di app.py) ──────────────────────

def render_nav_sidebar() -> None:
    """
    Placeholder — navigasi dirender langsung di app.py
    agar bisa akses AuthManager dan session state dengan mudah.
    """
    pass
