"""
ui/styles.py — Glass Morphism CSS untuk SiberkaRAG
===================================================
Dark gradient background + frosted glass cards + smooth animations.
"""


def get_glass_css() -> str:
    """
    Kembalikan string CSS glass morphism lengkap.
    Inject ke Streamlit menggunakan st.markdown(css, unsafe_allow_html=True).
    """
    return """
<style>
/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   GOOGLE FONTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   CSS VARIABLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
:root {
    --glass-bg: rgba(255, 255, 255, 0.07);
    --glass-border: rgba(255, 255, 255, 0.15);
    --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
    --glass-blur: blur(20px);
    --accent-primary: #667eea;
    --accent-secondary: #764ba2;
    --accent-green: #43e97b;
    --accent-blue: #38f9d7;
    --accent-gold: #f093fb;
    --text-primary: rgba(255, 255, 255, 0.95);
    --text-secondary: rgba(255, 255, 255, 0.65);
    --text-muted: rgba(255, 255, 255, 0.40);
    --radius-lg: 20px;
    --radius-md: 14px;
    --radius-sm: 10px;
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   BACKGROUND — ANIMATED GRADIENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 40%, #24243e 100%);
    background-attachment: fixed;
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
}

/* Animated floating orbs */
.stApp::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background:
        radial-gradient(circle at 20% 20%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 50% 50%, rgba(67, 233, 123, 0.05) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   MAIN CONTENT AREA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.main .block-container {
    padding: 2rem 2rem 4rem;
    max-width: 1200px;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SIDEBAR — GLASS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
[data-testid="stSidebar"] {
    background: rgba(15, 12, 41, 0.80) !important;
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border-right: 1px solid var(--glass-border) !important;
}

[data-testid="stSidebar"] > div {
    padding: 1.5rem 1rem;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TYPOGRAPHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-weight: 700;
    letter-spacing: -0.02em;
}

p, li, span, label {
    color: var(--text-secondary);
}

.stMarkdown {
    color: var(--text-secondary);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   GLASS CARD — Reusable Component
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.glass-card {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    box-shadow: var(--glass-shadow);
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: var(--transition);
    position: relative;
    overflow: hidden;
}

.glass-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
}

.glass-card:hover {
    border-color: rgba(102, 126, 234, 0.4);
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
    transform: translateY(-2px);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   HERO HEADER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.hero-header {
    text-align: center;
    padding: 2.5rem 1rem 2rem;
    margin-bottom: 2rem;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: -0.03em;
    line-height: 1.1;
}

.hero-subtitle {
    font-size: 1.1rem;
    color: var(--text-secondary) !important;
    margin-top: 0.75rem;
    font-weight: 400;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(102, 126, 234, 0.15);
    border: 1px solid rgba(102, 126, 234, 0.3);
    border-radius: 100px;
    padding: 0.35rem 1rem;
    font-size: 0.8rem;
    color: #a78bfa;
    font-weight: 500;
    margin-bottom: 1.2rem;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   CHAT MESSAGES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem 0;
}

/* User bubble */
.chat-user {
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    gap: 0.75rem;
    animation: slideInRight 0.3s ease;
}

.chat-user .bubble {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 20px 20px 4px 20px;
    padding: 0.9rem 1.2rem;
    max-width: 75%;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    color: white;
    font-size: 0.95rem;
    line-height: 1.6;
}

/* AI bubble */
.chat-ai {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    gap: 0.75rem;
    animation: slideInLeft 0.3s ease;
}

.chat-ai .bubble {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
    border-radius: 20px 20px 20px 4px;
    padding: 0.9rem 1.2rem;
    max-width: 80%;
    box-shadow: var(--glass-shadow);
    color: var(--text-primary);
    font-size: 0.95rem;
    line-height: 1.7;
}

/* Avatars */
.avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}

.avatar-user {
    background: linear-gradient(135deg, #667eea, #764ba2);
    box-shadow: 0 2px 10px rgba(102, 126, 234, 0.5);
}

.avatar-ai {
    background: linear-gradient(135deg, #43e97b, #38f9d7);
    box-shadow: 0 2px 10px rgba(67, 233, 123, 0.5);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SOURCE CITATION CARDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.sources-section {
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.sources-title {
    font-size: 0.75rem;
    color: var(--text-muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}

.source-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(67, 233, 123, 0.1);
    border: 1px solid rgba(67, 233, 123, 0.25);
    border-radius: 8px;
    padding: 0.3rem 0.7rem;
    font-size: 0.75rem;
    color: #43e97b;
    font-weight: 500;
    margin: 0.2rem;
    cursor: default;
    transition: var(--transition);
}

.source-chip:hover {
    background: rgba(67, 233, 123, 0.2);
    border-color: rgba(67, 233, 123, 0.5);
}

.source-card {
    background: rgba(67, 233, 123, 0.05);
    border: 1px solid rgba(67, 233, 123, 0.15);
    border-radius: var(--radius-sm);
    padding: 0.75rem 1rem;
    margin: 0.3rem 0;
    font-size: 0.82rem;
    color: var(--text-secondary);
    line-height: 1.5;
}

.source-card .source-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.4rem;
    font-weight: 600;
    color: #43e97b;
    font-size: 0.78rem;
}

.source-card .excerpt {
    color: var(--text-muted);
    font-size: 0.78rem;
    font-style: italic;
    line-height: 1.5;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   FILE UPLOAD ZONE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(102, 126, 234, 0.4) !important;
    border-radius: var(--radius-md) !important;
    background: rgba(102, 126, 234, 0.05) !important;
    transition: var(--transition) !important;
    padding: 1rem !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: rgba(102, 126, 234, 0.7) !important;
    background: rgba(102, 126, 234, 0.1) !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   BUTTONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.6rem 1.4rem !important;
    transition: var(--transition) !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.35) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.55) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* Danger button */
.btn-danger > button {
    background: linear-gradient(135deg, #f5576c, #f093fb) !important;
    box-shadow: 0 4px 15px rgba(245, 87, 108, 0.35) !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   INPUT FIELDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stChatInput textarea,
.stTextInput input,
.stTextArea textarea {
    background: rgba(255, 255, 255, 0.07) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    caret-color: #667eea;
}

.stChatInput textarea:focus,
.stTextInput input:focus {
    border-color: rgba(102, 126, 234, 0.7) !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15) !important;
    outline: none !important;
}

[data-testid="stChatInput"] {
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-md) !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   METRICS / STAT CARDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
[data-testid="metric-container"] {
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem !important;
    box-shadow: var(--glass-shadow) !important;
}

[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
}

[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   DIVIDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent) !important;
    margin: 1.5rem 0 !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ALERTS / INFO BOXES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stAlert {
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur) !important;
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--glass-border) !important;
}

.stSuccess {
    border-left: 3px solid #43e97b !important;
}

.stError {
    border-left: 3px solid #f5576c !important;
}

.stWarning {
    border-left: 3px solid #f093fb !important;
}

.stInfo {
    border-left: 3px solid #667eea !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   PROGRESS BAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stProgress > div > div {
    background: linear-gradient(90deg, #667eea, #f093fb) !important;
    border-radius: 100px !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SPINNER / LOADING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.typing-indicator {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.75rem 1rem;
}

.typing-dot {
    width: 8px;
    height: 8px;
    background: #667eea;
    border-radius: 50%;
    animation: typingPulse 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   DOCUMENT LIST ITEMS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.doc-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: var(--radius-sm);
    padding: 0.65rem 0.9rem;
    margin-bottom: 0.4rem;
    transition: var(--transition);
}

.doc-item:hover {
    background: rgba(102, 126, 234, 0.08);
    border-color: rgba(102, 126, 234, 0.25);
}

.doc-icon {
    font-size: 1.3rem;
    flex-shrink: 0;
}

.doc-name {
    font-size: 0.83rem;
    font-weight: 500;
    color: var(--text-primary);
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.doc-meta {
    font-size: 0.72rem;
    color: var(--text-muted);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   EXPANDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
[data-testid="stExpander"] {
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-md) !important;
}

[data-testid="stExpanderToggleIcon"] {
    color: var(--text-secondary) !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SELECT BOX / MULTISELECT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
    background: rgba(255, 255, 255, 0.07) !important;
    border-color: rgba(255, 255, 255, 0.15) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SCROLLBAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: rgba(102, 126, 234, 0.4);
    border-radius: 100px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(102, 126, 234, 0.7);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ANIMATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-20px); }
    to   { opacity: 1; transform: translateX(0); }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(20px); }
    to   { opacity: 1; transform: translateX(0); }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(15px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes typingPulse {
    0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
    40%           { transform: scale(1.1); opacity: 1; }
}

@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position: 200% center; }
}

/* Fade in for elements */
.fade-in {
    animation: fadeInUp 0.4s ease forwards;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   EMPTY STATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    color: var(--text-muted);
}

.empty-state .empty-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    display: block;
    filter: grayscale(30%);
}

.empty-state h3 {
    color: var(--text-secondary) !important;
    font-weight: 600;
    margin-bottom: 0.5rem;
    font-size: 1.1rem;
}

.empty-state p {
    font-size: 0.9rem;
    line-height: 1.6;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   HIDE STREAMLIT ELEMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
.stDeployButton { display: none; }
</style>
"""
