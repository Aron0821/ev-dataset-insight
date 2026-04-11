import streamlit as st


def setup_page_config():
    st.set_page_config(
        page_title="EV Analytics Dashboard",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

    :root {
        --bg-primary:    #08080e;
        --bg-secondary:  #0f0f18;
        --bg-card:       #14141e;
        --accent-teal:   #00f5d4;
        --accent-green:  #b8ff57;
        --accent-purple: #7b6cff;
        --accent-amber:  #ffb830;
        --text-primary:  #eeeef8;
        --text-secondary:#8888aa;
        --text-muted:    #50506a;
        --border-subtle: rgba(255,255,255,0.07);
        --border-glow:   rgba(0,245,212,0.28);
        --shadow-card:   0 4px 24px rgba(0,0,0,0.5);
        --shadow-glow:   0 0 32px rgba(0,245,212,0.10);
        --radius-card:   16px;
        --radius-btn:    10px;
        --radius-input:  10px;
    }

    html, body, [class*="css"], .stApp {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: 'Syne', sans-serif !important;
    }

    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image: radial-gradient(rgba(0,245,212,0.05) 1px, transparent 1px);
        background-size: 32px 32px;
        pointer-events: none;
        z-index: 0;
    }

    /* ── Main container ── */
    .main .block-container {
        padding: 2.5rem 3rem 3rem 3rem !important;
        max-width: 1640px !important;
    }

    /* ── Headings ── */
    h1 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 800 !important;
        font-size: 2.4rem !important;
        letter-spacing: -0.03em !important;
        background: linear-gradient(120deg, #00f5d4 0%, #b8ff57 55%, #c0fff0 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        line-height: 1.1 !important;
        margin-bottom: 0.2rem !important;
    }
    h2 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
        letter-spacing: -0.02em !important;
        color: var(--text-primary) !important;
    }
    h3 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.07em !important;
        text-transform: uppercase !important;
        color: var(--text-secondary) !important;
    }
    p { line-height: 1.65 !important; color: var(--text-secondary) !important; }

    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-card) !important;
        padding: 1.4rem 1.6rem !important;
        transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s !important;
        position: relative !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-card) !important;
    }
    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent-teal), var(--accent-green) 60%, transparent);
    }
    [data-testid="metric-container"]:hover {
        border-color: var(--border-glow) !important;
        transform: translateY(-3px) !important;
        box-shadow: var(--shadow-glow), var(--shadow-card) !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 2rem !important;
        font-weight: 500 !important;
        color: var(--accent-teal) !important;
        letter-spacing: -0.02em !important;
    }
    [data-testid="stMetricLabel"] {
        font-family: 'Syne', sans-serif !important;
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.11em !important;
        text-transform: uppercase !important;
        color: var(--text-muted) !important;
    }
    [data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.76rem !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    [data-testid="stSidebar"] .block-container { padding: 2rem 1.25rem !important; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
    }

    /* ── Selectbox ── */
    [data-testid="stSelectbox"] > div > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-input) !important;
        color: var(--text-primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.84rem !important;
        transition: border-color 0.2s !important;
    }
    [data-testid="stSelectbox"] > div > div:hover { border-color: var(--accent-teal) !important; }

    /* ── Slider ── */
    [data-testid="stSlider"] [role="slider"] {
        background: var(--accent-teal) !important;
        box-shadow: 0 0 10px var(--accent-teal) !important;
    }

    /* ── Tabs ── */
    [data-testid="stTabs"] > div:first-child {
        background: var(--bg-secondary) !important;
        border-radius: 14px !important;
        padding: 0.3rem !important;
        border: 1px solid var(--border-subtle) !important;
        gap: 0.2rem !important;
        margin-bottom: 1.75rem !important;
        overflow-x: auto !important;
    }
    [data-testid="stTabs"] button {
        font-family: 'Syne', sans-serif !important;
        font-size: 0.76rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em !important;
        color: var(--text-muted) !important;
        border-radius: 10px !important;
        padding: 0.5rem 1.1rem !important;
        transition: all 0.2s ease !important;
        border: 1px solid transparent !important;
        background: transparent !important;
        white-space: nowrap !important;
    }
    [data-testid="stTabs"] button:hover {
        color: var(--text-primary) !important;
        background: var(--bg-card) !important;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0,245,212,0.13), rgba(184,255,87,0.08)) !important;
        color: var(--accent-teal) !important;
        border-color: rgba(0,245,212,0.22) !important;
    }

    /* ── PRIMARY button – teal/green gradient ── */
    [data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #00e5c4, #a8f040) !important;
        color: #080810 !important;
        border: none !important;
        border-radius: var(--radius-btn) !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.84rem !important;
        letter-spacing: 0.05em !important;
        padding: 0.55rem 1.6rem !important;
        transition: opacity 0.2s, transform 0.2s, box-shadow 0.2s !important;
        box-shadow: 0 4px 18px rgba(0,229,196,0.30) !important;
    }
    [data-testid="baseButton-primary"]:hover {
        opacity: 0.9 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(0,229,196,0.42) !important;
    }
    [data-testid="baseButton-primary"]:active { transform: translateY(0) !important; }

    /* ── SECONDARY button – purple tint ── */
    [data-testid="baseButton-secondary"] {
        background: rgba(123,108,255,0.10) !important;
        color: #a89dff !important;
        border: 1px solid rgba(123,108,255,0.35) !important;
        border-radius: var(--radius-btn) !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.84rem !important;
        padding: 0.5rem 1.3rem !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="baseButton-secondary"]:hover {
        background: rgba(123,108,255,0.20) !important;
        border-color: rgba(123,108,255,0.6) !important;
        color: #c4bcff !important;
    }

    /* ── Download button – amber tint ── */
    [data-testid="baseButton-downloadButton"] {
        background: rgba(255,184,48,0.10) !important;
        color: #ffcc66 !important;
        border: 1px solid rgba(255,184,48,0.35) !important;
        border-radius: var(--radius-btn) !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="baseButton-downloadButton"]:hover {
        background: rgba(255,184,48,0.20) !important;
        border-color: rgba(255,184,48,0.6) !important;
    }

    /* ── Dataframes ── */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-card) !important;
        overflow: hidden !important;
    }

    /* ── Alerts ── */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border-width: 1px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.81rem !important;
        padding: 0.75rem 1rem !important;
    }

    /* ───────────── CHAT UI ───────────── */
    [data-testid="stChatMessage"] {
        border-radius: 14px !important;
        margin-bottom: 0.65rem !important;
        padding: 0.9rem 1.15rem !important;
        border: 1px solid transparent !important;
        transition: border-color 0.2s !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: rgba(0,245,212,0.05) !important;
        border-left: 3px solid var(--accent-teal) !important;
        border-color: rgba(0,245,212,0.12) !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: rgba(123,108,255,0.05) !important;
        border-left: 3px solid var(--accent-purple) !important;
        border-color: rgba(123,108,255,0.12) !important;
    }
    [data-testid="chatAvatarIcon-user"] {
        background: linear-gradient(135deg, var(--accent-teal), var(--accent-green)) !important;
        border-radius: 10px !important;
    }
    [data-testid="chatAvatarIcon-assistant"] {
        background: linear-gradient(135deg, var(--accent-purple), #a78bfa) !important;
        border-radius: 10px !important;
    }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] div {
        font-family: 'Syne', sans-serif !important;
        font-size: 0.88rem !important;
        line-height: 1.7 !important;
        color: var(--text-primary) !important;
    }
    [data-testid="stChatInput"] > div {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border-subtle) !important;
        border-radius: 14px !important;
        transition: border-color 0.25s, box-shadow 0.25s !important;
    }
    [data-testid="stChatInput"]:focus-within > div {
        border-color: rgba(0,245,212,0.45) !important;
        box-shadow: 0 0 0 3px rgba(0,245,212,0.08), 0 4px 20px rgba(0,0,0,0.3) !important;
    }
    [data-testid="stChatInput"] textarea {
        font-family: 'Syne', sans-serif !important;
        font-size: 0.88rem !important;
        color: var(--text-primary) !important;
        background: transparent !important;
    }
    [data-testid="stChatInput"] textarea::placeholder { color: var(--text-muted) !important; }
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, var(--accent-teal), var(--accent-green)) !important;
        border: none !important;
        border-radius: 9px !important;
        color: #080810 !important;
        transition: opacity 0.2s !important;
    }
    [data-testid="stChatInput"] button:hover { opacity: 0.85 !important; }

    /* ── Text / Number inputs ── */
    [data-testid="stTextInput"] > div > div > input {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-input) !important;
        color: var(--text-primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.84rem !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    [data-testid="stTextInput"] > div > div > input:focus {
        border-color: var(--accent-teal) !important;
        box-shadow: 0 0 0 3px rgba(0,245,212,0.08) !important;
    }
    [data-testid="stNumberInput"] input {
        background: var(--bg-card) !important;
        border-color: var(--border-subtle) !important;
        color: var(--text-primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
        border-radius: var(--radius-input) !important;
    }
    [data-testid="stRadio"] label {
        color: var(--text-secondary) !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 0.85rem !important;
    }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
        margin-bottom: 0.5rem !important;
    }
    [data-testid="stExpander"] summary {
        font-family: 'Syne', sans-serif !important;
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        padding: 0.75rem 1rem !important;
    }
    [data-testid="stExpander"] summary:hover { color: var(--accent-teal) !important; }

    /* ── Code ── */
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        background: rgba(0,0,0,0.45) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 8px !important;
        font-size: 0.81rem !important;
        color: #9efce8 !important;
    }
    pre code { background: transparent !important; border: none !important; }

    /* ── Misc ── */
    .js-plotly-plot { border-radius: 14px !important; overflow: hidden !important; }
    hr { border-color: var(--border-subtle) !important; margin: 1.75rem 0 !important; }
    [data-testid="stCaptionContainer"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.71rem !important;
        color: var(--text-muted) !important;
    }
    [data-testid="stSpinner"] { color: var(--accent-teal) !important; }
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.18); }
    </style>
    """, unsafe_allow_html=True)