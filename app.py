import os
import json
from pathlib import Path

import streamlit as st
import fitz
from dotenv import load_dotenv
from google import genai

# Load environment variables (Preserve exact API key loading)
load_dotenv(Path(__file__).with_name(".env"))

st.set_page_config(
    page_title="ResearchMate AI – AI Research Paper Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# PREMIUM ACADEMIC SAAS DESIGN SYSTEM CSS
# Colour Palette:
# - Deep Navy: #172554
# - Royal Violet: #6558D3
# - Teal: #19A7A0
# - Warm Gold: #F4B860
# - Lavender: #E9E8FF
# - Background: #F5F7FC
# - White: #FFFFFF
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* Global canvas & typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #F5F7FC !important;
        color: #172554 !important;
    }

    /* Main container padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3.5rem;
        max-width: 1200px;
    }

    /* ========================================================= */
    /* 1. DARK NAVY SIDEBAR STYLING (#172554)                   */
    /* ========================================================= */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #172554 0%, #0F172A 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.7rem;
    }

    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stCaption {
        color: #E2E8F0 !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.12) !important;
        margin: 0.8rem 0 !important;
    }

    /* Sidebar Logo Box */
    .sidebar-brand-box {
        padding: 10px 6px 14px 6px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 12px;
    }

    .sidebar-brand-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }

    .sidebar-logo-icon {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: linear-gradient(135deg, #6558D3 0%, #19A7A0 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        box-shadow: 0 4px 12px rgba(101, 88, 211, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .sidebar-brand-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #FFFFFF !important;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }

    .sidebar-brand-badge {
        display: inline-block;
        background-color: rgba(101, 88, 211, 0.3);
        border: 1px solid rgba(244, 184, 96, 0.5);
        color: #F4B860 !important;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        padding: 2px 8px;
        border-radius: 9999px;
        text-transform: uppercase;
    }

    /* Sidebar Navigation Menu Radio Items */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {
        gap: 6px;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        margin-bottom: 4px !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(101, 88, 211, 0.4) !important;
        transform: translateX(3px) !important;
    }

    /* Highlighted Active Menu Item */
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(135deg, rgba(101, 88, 211, 0.95) 0%, rgba(79, 70, 229, 0.95) 100%) !important;
        border: 1px solid #F4B860 !important;
        box-shadow: 0 4px 16px rgba(101, 88, 211, 0.45) !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) span {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Sidebar Document Overview Card */
    .sidebar-doc-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 12px;
        backdrop-filter: blur(10px);
    }

    .sidebar-doc-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #FFFFFF !important;
        margin-bottom: 8px;
        word-break: break-all;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .sidebar-stat-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        color: #94A3B8 !important;
        padding: 5px 0;
        border-bottom: 1px dashed rgba(255, 255, 255, 0.1);
    }

    .sidebar-stat-row:last-child {
        border-bottom: none;
    }

    .sidebar-stat-val {
        font-weight: 700;
        color: #F4B860 !important;
    }

    /* ========================================================= */
    /* 2. HERO SECTION WITH VIOLET-TO-BLUE GRADIENT             */
    /* ========================================================= */
    .hero-container {
        background: linear-gradient(135deg, #172554 0%, #2A2170 35%, #6558D3 75%, #3B82F6 100%);
        border-radius: 20px;
        padding: 32px 38px;
        margin-bottom: 24px;
        color: #FFFFFF;
        box-shadow: 0 12px 30px -5px rgba(23, 37, 84, 0.25);
        position: relative;
        overflow: hidden;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.16);
        backdrop-filter: blur(8px);
        color: #F4B860;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 5px 14px;
        border-radius: 9999px;
        margin-bottom: 12px;
        border: 1px solid rgba(244, 184, 96, 0.4);
    }

    .hero-title {
        font-size: 2.25rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.025em;
        margin-bottom: 8px;
        line-height: 1.2;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #E2E8F0;
        font-weight: 400;
        line-height: 1.55;
        max-width: 780px;
        margin-bottom: 0px;
    }

    /* ========================================================= */
    /* 3. FOUR COLOURFUL FEATURE CARDS                           */
    /* ========================================================= */
    .feature-grid-row {
        margin-bottom: 24px;
    }

    .feature-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 22px 20px;
        height: 100%;
        border: 1px solid #E2E8F0;
        transition: all 0.25s ease;
        box-shadow: 0 4px 10px rgba(23, 37, 84, 0.03);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
    }

    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 14px 26px -4px rgba(23, 37, 84, 0.08);
    }

    /* Card Themes */
    .card-theme-violet {
        border-top: 5px solid #6558D3;
    }
    .card-theme-teal {
        border-top: 5px solid #19A7A0;
    }
    .card-theme-blue {
        border-top: 5px solid #2563EB;
    }
    .card-theme-gold {
        border-top: 5px solid #F4B860;
    }

    .badge-violet {
        background-color: #E9E8FF;
        color: #6558D3;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
        display: inline-block;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .badge-teal {
        background-color: #CCFBF1;
        color: #0D9488;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
        display: inline-block;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .badge-blue {
        background-color: #DBEAFE;
        color: #2563EB;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
        display: inline-block;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .badge-gold {
        background-color: #FEF3C7;
        color: #B45309;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
        display: inline-block;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .feature-card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #172554;
        margin-bottom: 6px;
    }

    .feature-card-desc {
        font-size: 0.85rem;
        color: #64748B;
        line-height: 1.5;
        margin-bottom: 14px;
    }

    .feature-card-status {
        font-size: 0.78rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
    }

    /* ========================================================= */
    /* 4. LARGE DRAG-AND-DROP PDF UPLOAD CONTAINER              */
    /* ========================================================= */
    .upload-card-container {
        background: #FFFFFF;
        border: 2px dashed #6558D3;
        border-radius: 18px;
        padding: 28px 24px;
        text-align: center;
        margin-bottom: 24px;
        transition: all 0.25s ease;
        box-shadow: 0 4px 15px rgba(101, 88, 211, 0.05);
    }

    .upload-card-container:hover {
        border-color: #19A7A0;
        box-shadow: 0 8px 25px rgba(25, 167, 160, 0.12);
        transform: translateY(-2px);
    }

    .upload-icon-badge {
        width: 58px;
        height: 58px;
        border-radius: 16px;
        background: linear-gradient(135deg, #E9E8FF 0%, #EEF2FF 100%);
        color: #6558D3;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.9rem;
        margin: 0 auto 12px auto;
        border: 1px solid #C7D2FE;
    }

    .upload-main-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #172554;
        margin-bottom: 4px;
    }

    .upload-sub-title {
        font-size: 0.92rem;
        color: #64748B;
        margin-bottom: 6px;
    }

    /* Streamlit Uploader Overrides */
    [data-testid="stFileUploader"] {
        padding: 0 !important;
    }

    [data-testid="stFileUploader"] section {
        border: none !important;
        background: transparent !important;
    }

    /* ========================================================= */
    /* 5. ELEGANT WHITE OUTPUT CARDS WITH SECTION HEADINGS      */
    /* ========================================================= */
    .output-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 30px 34px;
        margin-bottom: 24px;
        box-shadow: 0 4px 18px rgba(23, 37, 84, 0.04);
    }

    .output-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 16px;
        margin-bottom: 22px;
        border-bottom: 1px solid #F1F5F9;
    }

    .output-heading-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #172554;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .output-content-body {
        font-size: 1.02rem;
        line-height: 1.75;
        color: #1E293B;
    }

    .output-content-body h1, .output-content-body h2, .output-content-body h3 {
        color: #172554 !important;
        font-weight: 700 !important;
        margin-top: 18px !important;
        margin-bottom: 8px !important;
    }

    /* ========================================================= */
    /* 6. QUIZ INTERFACE & CELEBRATORY SCORE CARD               */
    /* ========================================================= */
    .quiz-q-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #2563EB;
        border-radius: 14px;
        padding: 22px 24px;
        margin-bottom: 18px;
        box-shadow: 0 2px 6px rgba(23, 37, 84, 0.03);
    }

    .quiz-q-pill {
        font-size: 0.75rem;
        font-weight: 700;
        color: #2563EB;
        background: #DBEAFE;
        padding: 3px 10px;
        border-radius: 9999px;
        display: inline-block;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .quiz-q-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #172554;
        margin-bottom: 12px;
    }

    .quiz-score-hero {
        background: linear-gradient(135deg, #172554 0%, #2A2170 50%, #6558D3 100%);
        border-radius: 18px;
        padding: 32px;
        text-align: center;
        color: #FFFFFF;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px rgba(101, 88, 211, 0.25);
    }

    .quiz-score-badge {
        background: rgba(255, 255, 255, 0.16);
        color: #F4B860;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 4px 14px;
        border-radius: 9999px;
        display: inline-block;
        margin-bottom: 10px;
        border: 1px solid rgba(244, 184, 96, 0.35);
    }

    .quiz-score-val {
        font-size: 2.8rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        margin-bottom: 6px;
    }

    /* ========================================================= */
    /* 7. FLASHCARDS WITH WARM GOLD THEME & REVEAL INTERACTION  */
    /* ========================================================= */
    .flashcard-deck {
        background: linear-gradient(145deg, #FFFFFF 0%, #FFFDF7 100%);
        border: 2px solid #F4B860;
        border-radius: 20px;
        padding: 38px 32px;
        text-align: center;
        min-height: 240px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 12px 30px rgba(244, 184, 96, 0.15);
        position: relative;
        margin: 18px 0 22px 0;
        transition: all 0.3s ease;
    }

    .flashcard-deck:hover {
        box-shadow: 0 16px 36px rgba(244, 184, 96, 0.22);
    }

    .flashcard-tag {
        position: absolute;
        top: 16px;
        left: 22px;
        background: #FEF3C7;
        color: #B45309;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    .flashcard-question-text {
        font-size: 1.35rem;
        font-weight: 700;
        color: #172554;
        line-height: 1.5;
        margin: 20px 0 14px 0;
    }

    .flashcard-answer-revealed {
        background: #F0FDF4;
        border-left: 5px solid #19A7A0;
        border-radius: 10px;
        padding: 18px 24px;
        margin-top: 18px;
        text-align: left;
        width: 100%;
        animation: cardReveal 0.3s ease-in-out;
    }

    @keyframes cardReveal {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .flashcard-answer-heading {
        font-size: 0.78rem;
        font-weight: 700;
        color: #0D9488;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }

    .flashcard-answer-body {
        font-size: 1.05rem;
        color: #064E3B;
        line-height: 1.55;
        font-weight: 500;
    }

    /* ========================================================= */
    /* 8. BUTTONS & UI CONTROLS                                 */
    /* ========================================================= */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6558D3 0%, #4F46E5 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.6rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.01em !important;
        box-shadow: 0 4px 14px rgba(101, 88, 211, 0.35) !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(101, 88, 211, 0.45) !important;
    }

    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #172554 !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        border-color: #6558D3 !important;
        color: #6558D3 !important;
        background-color: #E9E8FF !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# API Key Validation (Preserves exact validation)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API key not found. Check your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)


def ask_gemini(prompt, paper_text):
    """Query Gemini with research paper source text (Unchanged backend function)."""
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=[
            prompt,
            "Use only the following research paper text as your source:\n"
            + paper_text[:40000]
        ]
    )
    return response.text or ""


# Navigation Options List
NAV_OPTIONS = [
    "📑 Executive Summary",
    "💡 Simple English",
    "📝 Interactive Quiz",
    "🗂️ Smart Flashcards"
]

if "active_nav" not in st.session_state:
    st.session_state.active_nav = "📑 Executive Summary"


# ==============================================================================
# 1. DARK NAVY SIDEBAR (#172554) WITH BRAND LOGO & HIGHLIGHTED ACTIVE MENU
# ==============================================================================
with st.sidebar:
    # ResearchMate AI Logo Box
    st.markdown(
        """
        <div class="sidebar-brand-box">
            <div class="sidebar-brand-logo">
                <div class="sidebar-logo-icon">📚</div>
                <div>
                    <div class="sidebar-brand-title">ResearchMate</div>
                    <span class="sidebar-brand-badge">AI SaaS Suite</span>
                </div>
            </div>
            <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 4px;">
                Accelerated Academic Paper Reading
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Navigation Menu with highlighted active item
    st.markdown("<div style='font-size: 0.75rem; font-weight: 700; color: #94A3B8; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px;'>WORKSPACE NAVIGATION</div>", unsafe_allow_html=True)
    
    current_index = NAV_OPTIONS.index(st.session_state.active_nav) if st.session_state.active_nav in NAV_OPTIONS else 0
    sidebar_selection = st.radio(
        "Navigation Menu",
        NAV_OPTIONS,
        index=current_index,
        key="nav_radio_menu",
        label_visibility="collapsed"
    )

    if sidebar_selection != st.session_state.active_nav:
        st.session_state.active_nav = sidebar_selection
        st.rerun()

    st.markdown("---")

    # Document Overview & Study Settings (Displayed once a document is active)
    if "doc_metadata" in st.session_state:
        meta = st.session_state.doc_metadata
        st.markdown(
            f"""
            <div class="sidebar-doc-card">
                <div class="sidebar-doc-title">📄 {meta['name']}</div>
                <div class="sidebar-stat-row">
                    <span>Pages Processed:</span>
                    <span class="sidebar-stat-val">{meta['pages']}</span>
                </div>
                <div class="sidebar-stat-row">
                    <span>Extracted Words:</span>
                    <span class="sidebar-stat-val">{meta['words']:,}</span>
                </div>
                <div class="sidebar-stat-row">
                    <span>Est. Reading Time:</span>
                    <span class="sidebar-stat-val">~{meta['reading_time']} min</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='font-size: 0.75rem; font-weight: 700; color: #94A3B8; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px;'>STUDY SETTINGS</div>", unsafe_allow_html=True)
        quiz_count = st.selectbox(
            "Quiz Question Count",
            [5, 10],
            index=0,
            key="cfg_quiz_count"
        )
        card_count = st.selectbox(
            "Flashcard Count",
            [5, 10, 15],
            index=1,
            key="cfg_card_count"
        )

        st.markdown("---")
        if st.button("🔄 Reset Study Session", use_container_width=True):
            for key in [
                "summary_result",
                "explanation_result",
                "quiz_data",
                "quiz_answers",
                "quiz_submitted",
                "flashcards",
                "card_index",
                "card_revealed"
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    else:
        st.markdown(
            """
            <div class="sidebar-doc-card">
                <div style="font-size: 0.85rem; font-weight: 700; color: #FFFFFF; margin-bottom: 4px;">Awaiting PDF Paper</div>
                <div style="font-size: 0.78rem; color: #94A3B8; line-height: 1.4;">
                    Upload an academic paper in PDF format to activate all reading, analysis, and active recall features.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        quiz_count = 5
        card_count = 10


# ==============================================================================
# 2. HERO SECTION WITH VIOLET-TO-BLUE GRADIENT
# ==============================================================================
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-badge">⚡ Next-Gen Academic Assistant</div>
        <div class="hero-title">Master Complex Research Papers in Minutes</div>
        <div class="hero-subtitle">
            ResearchMate AI transforms academic literature into structured executive summaries, plain-English conceptual breakdowns, adaptive multiple-choice quizzes, and smart flashcards.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==============================================================================
# 4. LARGE DRAG-AND-DROP PDF UPLOAD CONTAINER
# ==============================================================================
st.markdown(
    """
    <div class="upload-card-container">
        <div class="upload-icon-badge">📄</div>
        <div class="upload-main-title">Upload Research Paper</div>
        <div class="upload-sub-title">Drag and drop your academic PDF here, or browse files to begin text extraction</div>
    </div>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Upload Research Paper (PDF)",
    type=["pdf"],
    label_visibility="collapsed",
    help="Upload an academic research paper in PDF format."
)

paper_text = ""
pages = []

if uploaded_file:
    try:
        with fitz.open(stream=uploaded_file.getvalue(), filetype="pdf") as document:
            pages = [page.get_text() for page in document]
            paper_text = "\n".join(pages)

        if not paper_text.strip():
            st.error("No readable text found in this PDF. Please upload a text-based document.")
            st.stop()

        word_count = len(paper_text.split())
        est_reading_time = max(1, round(word_count / 220))

        # Persist document metadata for sidebar
        st.session_state.doc_metadata = {
            "name": uploaded_file.name[:24] + ("..." if len(uploaded_file.name) > 24 else ""),
            "pages": len(pages),
            "words": word_count,
            "reading_time": est_reading_time
        }

    except Exception as error:
        st.error(f"Could not process PDF: {error}")
        st.stop()
else:
    if "doc_metadata" in st.session_state:
        del st.session_state["doc_metadata"]


# ==============================================================================
# 3. FOUR COLOURFUL FEATURE CARDS
# ==============================================================================
st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
col_card1, col_card2, col_card3, col_card4 = st.columns(4)

# Status determinations
status_summary = "✅ Generated" if "summary_result" in st.session_state else "⚡ Ready"
status_explain = "✅ Generated" if "explanation_result" in st.session_state else "⚡ Ready"
status_quiz = f"🎯 {len(st.session_state.quiz_data)} Questions" if "quiz_data" in st.session_state else "⚡ Ready"
status_cards = f"🗂️ {len(st.session_state.flashcards)} Cards" if "flashcards" in st.session_state else "⚡ Ready"

with col_card1:
    st.markdown(
        f"""
        <div class="feature-card card-theme-violet">
            <div>
                <span class="badge-violet">Executive Summary</span>
                <div class="feature-card-title">📑 7-Point Synthesis</div>
                <div class="feature-card-desc">Structured academic breakdown of problem, methods, findings, and limitations.</div>
            </div>
            <div>
                <span class="feature-card-status" style="background: #E9E8FF; color: #6558D3;">{status_summary}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Summary", key="btn_open_sum", use_container_width=True):
        st.session_state.active_nav = "📑 Executive Summary"
        st.rerun()

with col_card2:
    st.markdown(
        f"""
        <div class="feature-card card-theme-teal">
            <div>
                <span class="badge-teal">Simple English</span>
                <div class="feature-card-title">💡 Plain Explainer</div>
                <div class="feature-card-desc">Demystifies dense academic terminology, mathematical formulas, and concepts.</div>
            </div>
            <div>
                <span class="feature-card-status" style="background: #CCFBF1; color: #0D9488;">{status_explain}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Explainer", key="btn_open_exp", use_container_width=True):
        st.session_state.active_nav = "💡 Simple English"
        st.rerun()

with col_card3:
    st.markdown(
        f"""
        <div class="feature-card card-theme-blue">
            <div>
                <span class="badge-blue">Interactive Quiz</span>
                <div class="feature-card-title">📝 Knowledge Check</div>
                <div class="feature-card-desc">Adaptive multiple-choice test with immediate scoring and rationales.</div>
            </div>
            <div>
                <span class="feature-card-status" style="background: #DBEAFE; color: #2563EB;">{status_quiz}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Quiz", key="btn_open_quiz", use_container_width=True):
        st.session_state.active_nav = "📝 Interactive Quiz"
        st.rerun()

with col_card4:
    st.markdown(
        f"""
        <div class="feature-card card-theme-gold">
            <div>
                <span class="badge-gold">Smart Flashcards</span>
                <div class="feature-card-title">🗂️ Active Recall</div>
                <div class="feature-card-desc">High-retention study cards with revealable answers and deck navigation.</div>
            </div>
            <div>
                <span class="feature-card-status" style="background: #FEF3C7; color: #B45309;">{status_cards}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Flashcards", key="btn_open_cards", use_container_width=True):
        st.session_state.active_nav = "🗂️ Smart Flashcards"
        st.rerun()

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)


# ==============================================================================
# ACTIVE FEATURE WORKSPACE SECTION
# ==============================================================================
if uploaded_file and paper_text.strip():
    with st.expander(f"📄 Preview Extracted Text ({len(pages)} pages processed)"):
        st.caption("First 3,000 characters of raw extracted text:")
        st.text(paper_text[:3000])

    active_section = st.session_state.active_nav

    # --------------------------------------------------------------------------
    # FEATURE 1: EXECUTIVE SUMMARY (VIOLET THEME: #6558D3)
    # --------------------------------------------------------------------------
    if active_section == "📑 Executive Summary":
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                <span class="badge-violet">Feature 1</span>
                <h3 style="margin: 0; color: #172554; font-weight: 800;">Executive Research Summary</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        if "summary_result" not in st.session_state:
            st.markdown(
                """
                <div class="output-card" style="border-top: 5px solid #6558D3;">
                    <div class="output-heading-title" style="color: #6558D3;">
                        <span>📑 Structured Academic Synthesis</span>
                    </div>
                    <p style="color: #64748B; font-size: 0.95rem; line-height: 1.6; margin-top: 8px;">
                        Gemini will analyze the source paper and extract a structured 7-part brief tailored for undergraduate students and researchers: <b>Research problem, Objective, Methodology, Dataset/materials, Key results, Limitations, and Important conclusion</b>.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("✨ Generate Executive Summary", type="primary", key="btn_run_summary"):
                prompt = """
                Summarize the research paper for an undergraduate student.
                Use these headings:
                1. Research problem
                2. Objective
                3. Methodology
                4. Dataset or materials
                5. Key results
                6. Limitations
                7. Important conclusion

                Do not invent information absent from the paper.
                """
                with st.spinner("Analyzing and synthesizing paper with Gemini..."):
                    try:
                        result = ask_gemini(prompt, paper_text)
                        st.session_state.summary_result = result
                        st.rerun()
                    except Exception as error:
                        st.error(f"Could not generate summary: {error}")

        else:
            st.markdown(
                """
                <div class="output-card" style="border-top: 5px solid #6558D3;">
                    <div class="output-header-bar">
                        <div class="output-heading-title" style="color: #6558D3;">
                            <span>📑 Executive Summary Findings</span>
                        </div>
                    </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div class='output-content-body'>{st.session_state.summary_result}</div>",
                unsafe_allow_html=False
            )
            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("🔄 Regenerate Executive Summary", type="secondary", key="btn_regen_sum"):
                del st.session_state.summary_result
                st.rerun()

    # --------------------------------------------------------------------------
    # FEATURE 2: SIMPLE ENGLISH EXPLANATION (TEAL THEME: #19A7A0)
    # --------------------------------------------------------------------------
    elif active_section == "💡 Simple English":
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                <span class="badge-teal">Feature 2</span>
                <h3 style="margin: 0; color: #172554; font-weight: 800;">Plain-English Concept Explainer</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        if "explanation_result" not in st.session_state:
            st.markdown(
                """
                <div class="output-card" style="border-top: 5px solid #19A7A0;">
                    <div class="output-heading-title" style="color: #0D9488;">
                        <span>💡 Demystify Complex Jargon</span>
                    </div>
                    <p style="color: #64748B; font-size: 0.95rem; line-height: 1.6; margin-top: 8px;">
                        Translates dense equations, technical definitions, and domain mechanisms into intuitive conceptual explanations with relatable everyday analogies.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("✨ Explain in Simple English", type="primary", key="btn_run_explain"):
                prompt = """
                Explain this research paper to an undergraduate student.
                Use simple English, explain technical terms,
                and give examples where useful.
                Do not invent facts.
                """
                with st.spinner("Preparing plain-English explanation with Gemini..."):
                    try:
                        result = ask_gemini(prompt, paper_text)
                        st.session_state.explanation_result = result
                        st.rerun()
                    except Exception as error:
                        st.error(f"Could not explain the paper: {error}")

        else:
            st.markdown(
                """
                <div class="output-card" style="border-top: 5px solid #19A7A0;">
                    <div class="output-header-bar">
                        <div class="output-heading-title" style="color: #0D9488;">
                            <span>💡 Plain-English Breakdown</span>
                        </div>
                    </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div class='output-content-body'>{st.session_state.explanation_result}</div>",
                unsafe_allow_html=False
            )
            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("🔄 Regenerate Explanation", type="secondary", key="btn_regen_exp"):
                del st.session_state.explanation_result
                st.rerun()

    # --------------------------------------------------------------------------
    # FEATURE 3: INTERACTIVE QUIZ (BLUE THEME: #2563EB)
    # --------------------------------------------------------------------------
    elif active_section == "📝 Interactive Quiz":
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                <span class="badge-blue">Feature 3</span>
                <h3 style="margin: 0; color: #172554; font-weight: 800;">Interactive Knowledge Check</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        if "quiz_data" not in st.session_state:
            st.markdown(
                f"""
                <div class="output-card" style="border-top: 5px solid #2563EB;">
                    <div class="output-heading-title" style="color: #2563EB;">
                        <span>📝 Active Multiple-Choice Assessment</span>
                    </div>
                    <p style="color: #64748B; font-size: 0.95rem; line-height: 1.6; margin-top: 8px;">
                        Evaluate your comprehension with <b>{quiz_count} AI-generated multiple-choice questions</b> strictly sourced from the paper's findings, dataset, and methodology.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("✨ Generate Interactive Quiz", type="primary", key="btn_run_quiz"):
                prompt = f"""
                Create exactly {quiz_count} multiple-choice questions
                based only on this research paper.

                Return ONLY valid JSON in this format:
                {{
                  "questions": [
                    {{
                      "question": "Question text",
                      "options": {{
                        "A": "First option",
                        "B": "Second option",
                        "C": "Third option",
                        "D": "Fourth option"
                      }},
                      "answer": "A",
                      "explanation": "Brief explanation based on the paper"
                    }}
                  ]
                }}

                Requirements:
                - Exactly {quiz_count} questions.
                - Four options per question.
                - The answer must be A, B, C, or D.
                - Avoid ambiguous questions.
                - Do not include information absent from the paper.
                """
                with st.spinner("Generating quiz questions with Gemini..."):
                    try:
                        result = ask_gemini(prompt, paper_text)
                        result = result.strip()

                        if result.startswith("```"):
                            result = result.split("\n", 1)[1]
                            result = result.rsplit("```", 1)[0].strip()

                        if result.startswith("json"):
                            result = result[4:].strip()

                        quiz_data = json.loads(result)
                        questions = quiz_data.get("questions", [])

                        if not questions:
                            raise ValueError("No questions were returned. Try again.")

                        st.session_state.quiz_data = questions
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_submitted = False
                        st.rerun()

                    except Exception as error:
                        st.error(f"Could not create the quiz: {error}")

        else:
            questions = st.session_state.quiz_data

            if not st.session_state.get("quiz_submitted", False):
                st.caption(f"Select an option for each of the {len(questions)} questions below, then click Submit.")

                with st.form("quiz_form"):
                    selected_answers = {}

                    for index, question in enumerate(questions):
                        st.markdown(
                            f"""
                            <div class="quiz-q-card">
                                <span class="quiz-q-pill">Question {index + 1} of {len(questions)}</span>
                                <div class="quiz-q-title">{question['question']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        options = question.get("options", {})
                        selected = st.radio(
                            f"Answer selection for Q{index + 1}",
                            options=list(options.keys()),
                            format_func=lambda key, opts=options: f"{key}. {opts[key]}",
                            index=None,
                            key=f"quiz_question_{index}",
                            label_visibility="collapsed"
                        )
                        selected_answers[index] = selected
                        st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

                    submitted = st.form_submit_button("Submit Quiz Answers", type="primary")

                    if submitted:
                        st.session_state.quiz_answers = selected_answers
                        st.session_state.quiz_submitted = True
                        st.rerun()

            else:
                answers = st.session_state.quiz_answers
                score = 0

                for index, question in enumerate(questions):
                    correct = question.get("answer", "").upper()
                    chosen = answers.get(index)
                    if chosen == correct:
                        score += 1

                pct = round((score / len(questions)) * 100)

                # Celebratory Score Card
                st.markdown(
                    f"""
                    <div class="quiz-score-hero">
                        <span class="quiz-score-badge">Assessment Completed</span>
                        <div class="quiz-score-val">{score} / {len(questions)} Correct ({pct}%)</div>
                        <div style="font-size: 1.05rem; color: #E2E8F0;">
                            {'🎉 Exceptional understanding! You have mastered the key concepts of this research paper.' if pct >= 80 else '💪 Good effort! Review the detailed rationales below to solidify your understanding.'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Question Breakdown Cards
                for index, question in enumerate(questions):
                    correct = question.get("answer", "").upper()
                    chosen = answers.get(index)
                    is_correct = (chosen == correct)

                    border_color = "#10B981" if is_correct else "#EF4444"
                    badge_bg = "#ECFDF5" if is_correct else "#FEF2F2"
                    badge_color = "#059669" if is_correct else "#DC2626"
                    status_text = "✅ Correct" if is_correct else "❌ Incorrect"

                    st.markdown(
                        f"""
                        <div class="output-card" style="border-left: 6px solid {border_color}; margin-bottom: 16px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <div style="font-weight: 700; color: #172554; font-size: 1.1rem;">
                                    Q{index + 1}. {question['question']}
                                </div>
                                <span style="font-weight: 700; font-size: 0.85rem; padding: 4px 12px; border-radius: 9999px; background: {badge_bg}; color: {badge_color};">
                                    {status_text}
                                </span>
                            </div>
                            <div style="font-size: 0.95rem; margin-bottom: 6px;">
                                <b>Your Answer:</b> <span style="color: {'#059669' if is_correct else '#DC2626'}; font-weight: 600;">{chosen if chosen else 'Not answered'}</span>
                            </div>
                            <div style="font-size: 0.95rem; margin-bottom: 12px; color: #0D9488;">
                                <b>Correct Answer:</b> Option {correct} ({question.get('options', {}).get(correct, '')})
                            </div>
                            <div style="background-color: #F8FAFC; border-radius: 10px; padding: 14px 16px; font-size: 0.92rem; color: #334155; border: 1px solid #E2E8F0;">
                                💡 <b>Detailed Rationale:</b> {question.get('explanation', '')}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                col_retry, col_new = st.columns(2)
                with col_retry:
                    if st.button("🔄 Retake This Quiz", use_container_width=True):
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_answers = {}
                        st.rerun()
                with col_new:
                    if st.button("✨ Generate New Questions", use_container_width=True, type="primary"):
                        del st.session_state.quiz_data
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_answers = {}
                        st.rerun()

    # --------------------------------------------------------------------------
    # FEATURE 4: SMART FLASHCARDS (WARM GOLD THEME: #F4B860)
    # --------------------------------------------------------------------------
    elif active_section == "🗂️ Smart Flashcards":
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                <span class="badge-gold">Feature 4</span>
                <h3 style="margin: 0; color: #172554; font-weight: 800;">Active Recall Smart Flashcards</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        if "flashcards" not in st.session_state:
            st.markdown(
                f"""
                <div class="output-card" style="border-top: 5px solid #F4B860;">
                    <div class="output-heading-title" style="color: #D97706;">
                        <span>🗂️ High-Yield Active Recall Deck</span>
                    </div>
                    <p style="color: #64748B; font-size: 0.95rem; line-height: 1.6; margin-top: 8px;">
                        Reinforce long-term retention with <b>{card_count} flashcards</b> focusing on technical definitions, core algorithms, and empirical conclusions.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("✨ Generate Flashcards", type="primary", key="btn_run_flashcards"):
                prompt = f"""
                Create exactly {card_count} flashcards based only
                on this research paper.

                Return ONLY valid JSON in this format:
                {{
                  "cards": [
                    {{
                      "question": "A concise question",
                      "answer": "A concise and accurate answer"
                    }}
                  ]
                }}

                Focus on concepts, methods, findings, and technical terms.
                Do not invent facts.
                """
                with st.spinner("Crafting flashcard deck with Gemini..."):
                    try:
                        result = ask_gemini(prompt, paper_text)
                        result = result.strip()

                        if result.startswith("```"):
                            result = result.split("\n", 1)[1]
                            result = result.rsplit("```", 1)[0].strip()

                        if result.startswith("json"):
                            result = result[4:].strip()

                        flashcard_data = json.loads(result)
                        cards = flashcard_data.get("cards", [])

                        if not cards:
                            raise ValueError("No flashcards were returned. Try again.")

                        st.session_state.flashcards = cards
                        st.session_state.card_index = 0
                        st.session_state.card_revealed = False
                        st.rerun()

                    except Exception as error:
                        st.error(f"Could not create flashcards: {error}")

        else:
            cards = st.session_state.flashcards

            if cards:
                index = st.session_state.get("card_index", 0)
                index = min(max(0, index), len(cards) - 1)
                card = cards[index]
                is_revealed = st.session_state.get("card_revealed", False)

                # Progress Bar & Deck Navigation Header
                col_prog, col_btn_new = st.columns([4, 1])
                with col_prog:
                    st.progress((index + 1) / len(cards))
                    st.caption(f"Progress: Card {index + 1} of {len(cards)}")
                with col_btn_new:
                    if st.button("✨ New Set", key="btn_new_cards_top", type="secondary"):
                        del st.session_state.flashcards
                        st.session_state.card_index = 0
                        st.session_state.card_revealed = False
                        st.rerun()

                # Coloured Flashcard Container
                answer_markup = ""
                if is_revealed:
                    answer_markup = f"""
                    <div class="flashcard-answer-revealed">
                        <div class="flashcard-answer-heading">Core Concept & Explanation</div>
                        <div class="flashcard-answer-body">{card.get('answer', 'No answer available.')}</div>
                    </div>
                    """

                st.markdown(
                    f"""
                    <div class="flashcard-deck">
                        <span class="flashcard-tag">Card #{index + 1} • Active Recall</span>
                        <div class="flashcard-question-text">{card.get('question', 'No question available.')}</div>
                        {answer_markup}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Action Controls: Reveal, Prev, Next
                col_btn_prev, col_btn_rev, col_btn_next = st.columns([1, 2, 1])

                with col_btn_prev:
                    if st.button("← Previous", disabled=(index == 0), key="previous_card", use_container_width=True):
                        st.session_state.card_index = index - 1
                        st.session_state.card_revealed = False
                        st.rerun()

                with col_btn_rev:
                    reveal_label = "🙈 Hide Answer" if is_revealed else "👁️ Reveal Answer"
                    if st.button(reveal_label, key="reveal_card", use_container_width=True, type="primary"):
                        st.session_state.card_revealed = not is_revealed
                        st.rerun()

                with col_btn_next:
                    if st.button("Next →", disabled=(index == len(cards) - 1), key="next_card", use_container_width=True):
                        st.session_state.card_index = index + 1
                        st.session_state.card_revealed = False
                        st.rerun()

else:
    # Empty State Guidance
    st.markdown(
        """
        <div style="text-align: center; padding: 28px 16px; background: #FFFFFF; border-radius: 16px; border: 1px solid #E2E8F0; margin-top: 10px;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #172554; margin-bottom: 6px;">
                Ready to Analyze Your Research Paper
            </div>
            <div style="font-size: 0.9rem; color: #64748B; max-width: 600px; margin: 0 auto; line-height: 1.5;">
                Select or drag a PDF file into the upload zone above. Once extracted, you can jump directly into structured summaries, plain-English explanations, multiple-choice quizzes, or flashcards.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
