"""
pages/dashboard_page.py — Dashboard Analytics SiberkaRAG
==========================================================
Statistik personal + Plotly charts.
Admin mendapat overview seluruh sistem.
"""
from __future__ import annotations

from datetime import datetime, timedelta

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from auth.auth_manager import AuthManager, get_db, navigate_to, require_login
from auth.auth_manager import AuthManager
from ui.components import glass_card


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PLOTLY THEME
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.03)",
    font=dict(family="Inter, sans-serif", color="rgba(255,255,255,0.75)", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    showlegend=True,
    legend=dict(
        bgcolor="rgba(255,255,255,0.05)",
        bordercolor="rgba(255,255,255,0.1)",
        borderwidth=1,
        font=dict(size=11),
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.07)",
        linecolor="rgba(255,255,255,0.1)",
        tickfont=dict(size=10),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.07)",
        linecolor="rgba(255,255,255,0.1)",
        tickfont=dict(size=10),
    ),
)

_COLORS = ["#667eea", "#f093fb", "#43e97b", "#f5576c", "#38f9d7", "#fda085"]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHART HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _query_timeline_chart(stats: list[dict]) -> go.Figure:
    """Line chart: query per hari."""
    if not stats:
        # Dummy data 7 hari terakhir
        today = datetime.utcnow().date()
        stats = [
            {"day": str(today - timedelta(days=i)), "count": 0}
            for i in range(6, -1, -1)
        ]

    days   = [s["day"] for s in stats]
    counts = [s["count"] for s in stats]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=days, y=counts,
        mode="lines+markers",
        name="Queries",
        line=dict(color="#667eea", width=2.5, shape="spline"),
        marker=dict(size=7, color="#667eea",
                    line=dict(width=2, color="white")),
        fill="tozeroy",
        fillcolor="rgba(102,126,234,0.1)",
    ))
    fig.update_layout(
        title=dict(text="📈 Query per Hari (30 Hari Terakhir)",
                   font=dict(size=13)),
        **_PLOTLY_LAYOUT,
    )
    return fig


def _doc_type_pie(distribution: list[dict]) -> go.Figure:
    """Pie chart: distribusi tipe dokumen."""
    if not distribution:
        labels, values = ["Belum ada"], [1]
        colors = ["rgba(255,255,255,0.1)"]
    else:
        labels = [d["type"] for d in distribution]
        values = [d["count"] for d in distribution]
        colors = _COLORS[: len(labels)]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors,
                    line=dict(color="rgba(0,0,0,0.3)", width=2)),
        textfont=dict(size=12),
    ))
    fig.update_layout(
        title=dict(text="📂 Distribusi Tipe Dokumen",
                   font=dict(size=13)),
        **_PLOTLY_LAYOUT,
    )
    return fig


def _admin_users_bar(users) -> go.Figure:
    """Bar chart: query per user (admin view)."""
    names   = [u.username for u in users]
    queries = [u.total_queries for u in users]

    fig = go.Figure(go.Bar(
        x=names, y=queries,
        marker=dict(
            color=queries,
            colorscale=[[0, "#302b63"], [1, "#667eea"]],
            line=dict(color="rgba(255,255,255,0.1)", width=1),
        ),
        text=queries,
        textposition="outside",
        textfont=dict(color="rgba(255,255,255,0.7)", size=11),
    ))
    fig.update_layout(
        title=dict(text="👥 Total Query per User",
                   font=dict(size=13)),
        **_PLOTLY_LAYOUT,
    )
    return fig


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DASHBOARD PAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def render_dashboard_page(auth: AuthManager) -> None:
    """Render halaman dashboard utama."""
    user = require_login()
    db   = get_db()

    # ── Header ────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="
            background: linear-gradient(135deg, #667eea, #f093fb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 1.8rem;
            font-weight: 800;
            margin: 0;
        ">
            {user.avatar_emoji} Halo, {user.display_name}!
        </h2>
        <p style="color:rgba(255,255,255,0.45); font-size:0.87rem; margin:0.3rem 0 0;">
            Berikut ringkasan aktivitas Anda di SiberkaRAG
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── First Login Warning ───────────────────────────────────────
    if st.session_state.get("first_login_warning"):
        st.warning(
            "⚠️ **Anda masih menggunakan password default!** "
            "Segera ganti di menu **Pengaturan → Ganti Password**."
        )

    # ── Personal Stats Row ────────────────────────────────────────
    doc_stats   = db.get_doc_stats(user.id)
    query_stats = db.get_query_stats_by_day(user.id, days=30)
    total_chunks = sum(d["chunks"] for d in doc_stats)
    total_pages  = sum(d["pages"] for d in doc_stats)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📄 Dokumen", len(doc_stats),
                  help="Total dokumen yang Anda upload")
    with c2:
        st.metric("💬 Total Query", user.total_queries,
                  help="Total pertanyaan yang pernah diajukan")
    with c3:
        st.metric("🔢 Total Chunks", f"{total_chunks:,}",
                  help="Total potongan teks yang ter-index")
    with c4:
        quota_used = len(doc_stats)
        delta_str  = f"{user.doc_quota - quota_used} sisa"
        st.metric("📊 Kuota Dokumen", f"{quota_used}/{user.doc_quota}",
                  delta=delta_str, delta_color="normal")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row ────────────────────────────────────────────────
    col_left, col_right = st.columns([2, 1])

    with col_left:
        fig_timeline = _query_timeline_chart(query_stats)
        st.plotly_chart(fig_timeline, use_container_width=True,
                        config={"displayModeBar": False})

    with col_right:
        dist = db.get_doc_type_distribution(user.id)
        fig_pie = _doc_type_pie(dist)
        st.plotly_chart(fig_pie, use_container_width=True,
                        config={"displayModeBar": False})

    # ── Document Table ────────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <p style="font-size:0.85rem; font-weight:700;
       color:rgba(255,255,255,0.7); text-transform:uppercase;
       letter-spacing:0.1em; margin-bottom:0.75rem;">
    📚 Dokumen Anda
    </p>
    """, unsafe_allow_html=True)

    if not doc_stats:
        st.markdown("""
        <div class="empty-state" style="padding:1.5rem;">
            <span class="empty-icon" style="font-size:2rem;">📂</span>
            <h3>Belum ada dokumen</h3>
            <p>Pergi ke halaman <b>Chat</b> dan upload dokumen Anda.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Format table data
        import pandas as pd
        df_data = []
        for d in doc_stats:
            uploaded = d.get("uploaded_at", "")[:10]
            df_data.append({
                "📄 Nama File": d["filename"],
                "Tipe": d["file_type"],
                "Halaman": d["pages"],
                "Chunks": f"{d['chunks']:,}",
                "Chars": f"{d['chars']:,}",
                "Diupload": uploaded,
            })
        df = pd.DataFrame(df_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    # ── Recent Activity ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <p style="font-size:0.85rem; font-weight:700;
       color:rgba(255,255,255,0.7); text-transform:uppercase;
       letter-spacing:0.1em; margin-bottom:0.75rem;">
    🕐 Aktivitas Terbaru
    </p>
    """, unsafe_allow_html=True)

    activities = db.get_user_activity(user.id, limit=10)
    if not activities:
        st.info("Belum ada aktivitas tercatat.")
    else:
        for act in activities:
            ts = act.timestamp.strftime("%d %b %Y %H:%M")
            detail_str = f" — {act.detail}" if act.detail else ""
            st.markdown(
                f'<div class="doc-item">'
                f'<span style="font-size:1.1rem;">{act.action_emoji}</span>'
                f'<div style="flex:1;">'
                f'<div class="doc-name">{act.action.capitalize()}{detail_str}</div>'
                f'<div class="doc-meta">{ts}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

    # ── Admin Section ─────────────────────────────────────────────
    if user.is_admin:
        _render_admin_overview(db)

    # ── Change Password Section ───────────────────────────────────
    st.markdown("---")
    with st.expander("🔑 Ganti Password", expanded=False):
        _render_change_password_form(user, auth)


def _render_change_password_form(user, auth: AuthManager) -> None:
    """Form ganti password."""
    with st.form("form_change_pw"):
        old_pw  = st.text_input("Password Lama", type="password")
        new_pw  = st.text_input("Password Baru", type="password",
                                placeholder="Minimal 8 karakter")
        conf_pw = st.text_input("Konfirmasi Password Baru", type="password")
        sub     = st.form_submit_button("💾 Simpan Password", use_container_width=True)

        if sub:
            ok, msg = auth.change_password(user.id, old_pw, new_pw, conf_pw)
            if ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")


def _render_admin_overview(db) -> None:
    """Bagian overview sistem khusus admin."""
    st.markdown("---")
    st.markdown("""
    <p style="font-size:0.85rem; font-weight:700;
       color:rgba(255,255,255,0.7); text-transform:uppercase;
       letter-spacing:0.1em; margin-bottom:0.75rem;">
    👑 Overview Sistem (Admin)
    </p>
    """, unsafe_allow_html=True)

    sys_stats = db.get_system_stats()

    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        ("👥 Total User",    sys_stats["total_users"],   c1),
        ("✅ User Aktif",    sys_stats["active_users"],  c2),
        ("📄 Total Dokumen", sys_stats["total_docs"],    c3),
        ("💬 Total Query",   sys_stats["total_queries"], c4),
        ("🔢 Total Vectors", f'{sys_stats["total_chunks"]:,}', c5),
    ]
    for label, val, col in metrics:
        with col:
            st.metric(label, val)

    # Bar chart query per user
    all_users = db.get_all_users()
    if all_users:
        fig_bar = _admin_users_bar(all_users)
        st.plotly_chart(fig_bar, use_container_width=True,
                        config={"displayModeBar": False})
