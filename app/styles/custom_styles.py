import streamlit as st


def inject_global_css():
    """Inyecta todos los estilos CSS personalizados para la aplicación."""
    custom_css = """
    <style>

    /* ─────────────────────────────────────────────
       TITLE & SUBHEADERS (native Streamlit + refinements)
    ───────────────────────────────────────────── */
    [data-testid="stAppViewContainer"] h1 {
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        color: var(--text-color) !important;
        margin-bottom: 0.5rem !important;
        padding-bottom: 0.75rem !important;
        border-bottom: 1px solid rgba(128, 128, 128, 0.15) !important;
    }
    [data-testid="stAppViewContainer"] h2 {
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        letter-spacing: 0.01em !important;
        color: var(--text-color) !important;
        opacity: 0.95;
        margin-top: 0.5rem !important;
        margin-bottom: 0.4rem !important;
    }

    /* ─────────────────────────────────────────────
       BACKGROUND & GLOBAL
    ───────────────────────────────────────────── */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(to bottom, var(--background-color) 0%, var(--secondary-background-color) 100%);
        background-attachment: fixed;
        color: var(--text-color);
    }

    code, pre, .banner-path {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* ─────────────────────────────────────────────
       SIDEBAR
    ───────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: var(--background-color);
        border-right: 1px solid rgba(128, 128, 128, 0.2);
    }

    /* ─────────────────────────────────────────────
       EXPANDER & DATA EDITOR
    ───────────────────────────────────────────── */
    [data-testid="stExpander"], [data-testid="stDataEditor"] {
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 14px !important;
    }
    /* Space between expander header and content (e.g. warning banner) */
    [data-testid="stExpander"] > div:last-child {
        padding-top: 16px !important;
    }

    /* Info alert: same font size as banner-warning text */
    [data-testid="stAlert"] {
        font-size: 14px !important;
    }

    /* ─────────────────────────────────────────────
       PANEL HEADER
    ───────────────────────────────────────────── */
    .panel-head {
        /* Color primario con transparencia para adaptarse al fondo */
        background: rgba(56, 139, 253, 0.1); 
        border: 1px solid var(--primary-color);
        border-left: 3px solid var(--primary-color);
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 15px;
        animation: fadeSlideIn 0.25s cubic-bezier(0.16, 1, 0.3, 1) both;
    }

    .panel-head-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1px;
    }

    .panel-head-icon { font-size: 18px; }
    .panel-head-caption { 
        font-size: 14px; 
        color: var(--text-color); 
        opacity: 0.8; 
    }

    /* ─────────────────────────────────────────────
       BADGE
    ───────────────────────────────────────────── */
    .panel-badge {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        padding: 4px 10px;
        background: rgba(56, 139, 253, 0.15);
        border: 1px solid var(--primary-color);
        border-radius: 20px;
        font-size: 10px;
        font-weight: 600;
        color: var(--primary-color);
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    /* ─────────────────────────────────────────────
       ANIMATION
    ───────────────────────────────────────────── */
    @keyframes fadeSlideIn {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ─────────────────────────────────────────────
       SAVE BANNER SUCCESS
    ───────────────────────────────────────────── */
    .save-banner-ok {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 18px;
        background: rgba(63, 185, 80, 0.1);
        border: 1px solid rgba(63, 185, 80, 0.3);
        border-left: 3px solid #3fb950;
        border-radius: 10px;
        color: #3fb950;
        margin-top: 16px;
    }

    .save-banner-ok .banner-path {
        font-size: 11px;
        color: var(--text-color);
        opacity: 0.6;
        margin-top: 2px;
    }


    /* ─────────────────────────────────────────────
       SAVE BANNER WARNING
    ───────────────────────────────────────────── */
    .banner-warning {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 18px 20px 18px;
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-left: 3px solid #ffc107;
        border-radius: 10px;
        color: #ffc107;
        margin-top: 16px;
    }

    .banner-warning .banner-warning-text {
        font-size: 11px;
        color: var(--text-color);
        opacity: 0.6;
        margin-top: 2px;
    }

    /* ─────────────────────────────────────────────
       FANCY PRIMARY BUTTON
    ───────────────────────────────────────────── */
    div[data-testid="stButton"] button[kind="primary"] {
        display: block !important;
        margin: 0 auto !important;
        width: 100%;
        background: rgba(56, 139, 253, 0.1);
        border: 1px solid var(--primary-color) !important;
        color: var(--primary-color) !important;
        font-size: 10px;
        padding: 3px 10px;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.25s ease;
    }

    div[data-testid="stButton"] button[kind="primary"]:hover {
        transform: translateY(-4px);
        background: rgba(56, 139, 253, 0.1);
        color: white !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    /* Download button: same fancy style as primary buttons */
    div[data-testid="stDownloadButton"] button {
        display: block !important;
        margin: 0 auto !important;
        width: 100%;
        background: rgba(56, 139, 253, 0.1) !important;
        border: 1px solid var(--primary-color) !important;
        color: var(--primary-color) !important;
        font-size: 10px;
        padding: 3px 10px;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.25s ease;
    }
    div[data-testid="stDownloadButton"] button:hover {
        transform: translateY(-4px);
        background: rgba(56, 139, 253, 0.1) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    /* ─────────────────────────────────────────────
       METRIC CARDS (vertical layout + two-column wrapper)
    ───────────────────────────────────────────── */
    .metric-cards-two-cols {
        display: flex;
        flex-direction: row;
        gap: 12px;
    }
    .metric-cards-two-cols > .metric-cards-vertical {
        flex: 1;
    }
    .metric-cards-vertical {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .metric-card {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.18);
        border-radius: 12px;
        padding: 14px 18px;
        min-height: auto;
    }
    .metric-title {
        color: var(--text-color);
        opacity: 0.75;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 6px;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }
    .metric-value {
        color: var(--text-color);
        font-size: 1.5rem;
        font-weight: 700;
        line-height: 1.25;
    }
    .metric-unit {
        font-size: 0.9rem;
        color: var(--text-color);
        opacity: 0.7;
        font-weight: 500;
    }
    .status-tag {
        font-size: 12px;
        font-weight: 600;
        margin-top: 8px;
        color: #00E676;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)