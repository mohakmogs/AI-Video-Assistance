import streamlit as st
import os
import re
import base64
import tempfile
import time
import html
import textwrap
import inspect
from pathlib import Path
from dotenv import load_dotenv

from main import run_pipeline
from core.rag_engine import ask_question


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Video Assistance",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_dotenv()


# =========================================================
# BACKGROUND WALLPAPER
# Replace utils/wallpaper.jpg anytime to change the background
# =========================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return None

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


wallpaper_path = os.path.join("utils", "wallpaper.jpg")
wallpaper_base64 = get_base64_image(wallpaper_path)

if wallpaper_base64:
    background_css = f"""
        background-image:
            linear-gradient(
                rgba(5, 3, 12, 0.84),
                rgba(8, 4, 18, 0.90)
            ),
            url("data:image/jpg;base64,{wallpaper_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    """
else:
    background_css = """
        background:
            radial-gradient(circle at 50% 0%, rgba(131, 30, 255, 0.20), transparent 32%),
            radial-gradient(circle at 5% 20%, rgba(109, 20, 220, 0.14), transparent 25%),
            linear-gradient(135deg, #07060b 0%, #0d0915 50%, #090611 100%);
    """


# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown(
    f"""
    <style>

    /* ---------------- REMOVE DEFAULT STREAMLIT ELEMENTS ---------------- */

    #MainMenu {{
        visibility: hidden;
    }}

    footer {{
        visibility: hidden;
    }}

    header {{
        visibility: hidden;
    }}

    /* Remove unwanted top spacing / empty elements */
    [data-testid="stHeader"] {{
        display: none;
    }}

    .stApp {{
        {background_css}
        color: #f5f3ff;
    }}

    .main {{
        background: transparent;
    }}

    .block-container {{
        padding-top: 3rem !important;
        padding-bottom: 4rem;
        max-width: 1200px;
    }}

    div[data-testid="stVerticalBlock"] {{
        gap: 0.7rem;
    }}

    /* ---------------- NAVIGATION AREA ---------------- */

    .nav-brand {{
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 10px;
        white-space: nowrap;
        padding-top: 0.45rem;
    }}

    .brand-icon {{
        width: 34px;
        height: 34px;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #a855f7, #6d28d9);
        box-shadow: 0 0 20px rgba(168, 85, 247, 0.55);
    }}

    /* ---------------- PILL BUTTONS ---------------- */

    div.stButton > button {{
        width: 100%;
        min-height: 48px;

        border-radius: 999px !important;

        border: 1px solid rgba(255, 255, 255, 0.10);
        background: rgba(255, 255, 255, 0.045);
        color: #ded9e8;

        font-size: 0.88rem;
        font-weight: 500;

        padding: 0.65rem 1.1rem;

        transition:
            transform 0.2s ease,
            background 0.2s ease,
            border-color 0.2s ease,
            box-shadow 0.2s ease;
    }}

    div.stButton > button:hover {{
        transform: translateY(-2px);
        border-color: rgba(168, 85, 247, 0.70);
        color: white;
        background: rgba(139, 92, 246, 0.14);
        box-shadow: 0 5px 22px rgba(139, 92, 246, 0.16);
    }}

    div.stButton > button:active {{
        transform: translateY(0px);
    }}

    /* ---------------- HERO ---------------- */

    .hero {{
        text-align: center;
        padding: 2.5rem 1rem 2rem;
    }}

    .badge {{
        display: inline-block;
        padding: 8px 17px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 500;
        color: #d8b4fe;
        background: rgba(139, 92, 246, 0.10);
        border: 1px solid rgba(168, 85, 247, 0.30);
        margin-bottom: 1.2rem;
    }}

    .hero h1 {{
        font-size: clamp(2.3rem, 5vw, 4.3rem);
        line-height: 1.08;
        font-weight: 700;
        letter-spacing: -2px;
        margin-bottom: 1rem;
        color: #ffffff;
    }}

    .gradient-text {{
        background: linear-gradient(90deg, #ffffff, #c084fc, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .hero p {{
        max-width: 680px;
        margin: auto;
        color: #aaa5b5;
        font-size: 1.05rem;
        line-height: 1.7;
    }}

    /* ---------------- GLASS CARD ---------------- */

    .glass-card {{
        background: rgba(16, 12, 25, 0.66);

        backdrop-filter: blur(22px);
        -webkit-backdrop-filter: blur(22px);

        border: 1px solid rgba(255,255,255,0.11);
        border-radius: 26px;

        box-shadow:
            0 20px 60px rgba(0,0,0,0.30),
            inset 0 1px 0 rgba(255,255,255,0.06);

        padding: 2rem;
    }}

    .section-title {{
        font-size: 1.7rem;
        font-weight: 650;
        color: white;
        margin-bottom: 0.35rem;
    }}

    .section-subtitle {{
        color: #9d98aa;
        margin-bottom: 1.5rem;
    }}

    /* ---------------- INPUT CARDS (UPLOAD + YOUTUBE SIDE BY SIDE) ---------------- */

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(16, 12, 25, 0.66);
        backdrop-filter: blur(22px);
        -webkit-backdrop-filter: blur(22px);
        border: 1px solid rgba(255,255,255,0.11) !important;
        border-radius: 24px !important;
        box-shadow:
            0 20px 60px rgba(0,0,0,0.25),
            inset 0 1px 0 rgba(255,255,255,0.06);
        padding: 0.6rem 0.8rem;
        transition: border-color 0.25s ease, box-shadow 0.25s ease;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"]:focus-within {{
        border-color: rgba(168, 85, 247, 0.65) !important;
        box-shadow: 0 0 0 2px rgba(168,85,247,0.12),
                    0 20px 60px rgba(0,0,0,0.25);
    }}

    .input-card-title {{
        font-size: 1.1rem;
        font-weight: 650;
        color: white;
        margin-bottom: 0.2rem;
    }}

    .input-card-sub {{
        font-size: 0.82rem;
        color: #9d98aa;
        margin-bottom: 0.6rem;
    }}

    /* ---------------- LIVE PROGRESS CARD ---------------- */

    .pg-card {{
        margin-top: 1.2rem;
        padding: 1.6rem 1.8rem;
        border-radius: 24px;
        background: rgba(16, 12, 25, 0.72);
        backdrop-filter: blur(22px);
        -webkit-backdrop-filter: blur(22px);
        border: 1px solid rgba(168, 85, 247, 0.30);
        box-shadow: 0 20px 60px rgba(0,0,0,0.30), 0 0 40px rgba(139,92,246,0.10);
    }}

    .pg-head {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }}

    .pg-title {{
        font-size: 1.1rem;
        font-weight: 650;
        color: #ffffff;
    }}

    .pg-time {{
        font-size: 0.85rem;
        font-weight: 600;
        color: #d8b4fe;
        padding: 5px 12px;
        border-radius: 999px;
        background: rgba(139,92,246,0.12);
        border: 1px solid rgba(168,85,247,0.30);
        font-variant-numeric: tabular-nums;
    }}

    .pg-bar {{
        height: 8px;
        border-radius: 999px;
        background: rgba(255,255,255,0.07);
        overflow: hidden;
        margin-bottom: 1.3rem;
    }}

    .pg-bar-fill {{
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #7c3aed, #c084fc, #7c3aed);
        background-size: 200% 100%;
        animation: pg-shimmer 1.6s linear infinite;
        transition: width 0.5s ease;
    }}

    .pg-bar-indeterminate {{
        width: 40%;
        animation: pg-slide 1.4s ease-in-out infinite;
    }}

    .pg-steps {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.7rem 1.2rem;
    }}

    .pg-step {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0.75rem 0.95rem;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.07);
        background: rgba(255,255,255,0.025);
        transition: all 0.3s ease;
    }}

    .pg-step.pending {{
        opacity: 0.45;
    }}

    .pg-step.active {{
        opacity: 1;
        border-color: rgba(192,132,252,0.70);
        background: rgba(139,92,246,0.14);
        box-shadow: 0 0 24px rgba(139,92,246,0.22);
    }}

    .pg-step.done {{
        border-color: rgba(74,222,128,0.25);
        background: rgba(74,222,128,0.05);
    }}

    .pg-dot {{
        flex-shrink: 0;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 700;
        border: 2px solid rgba(255,255,255,0.18);
        color: transparent;
    }}

    .pg-step.done .pg-dot {{
        background: #22c55e;
        border-color: #22c55e;
        color: #052e16;
    }}

    .pg-step.active .pg-dot {{
        border: 2px solid rgba(192,132,252,0.25);
        border-top-color: #c084fc;
        animation: pg-spin 0.8s linear infinite;
    }}

    .pg-label {{
        font-size: 0.92rem;
        font-weight: 600;
        color: #ffffff;
        line-height: 1.3;
    }}

    .pg-detail {{
        font-size: 0.78rem;
        color: #a9a3b8;
        line-height: 1.45;
        margin-top: 2px;
    }}

    .pg-took {{
        margin-left: auto;
        font-size: 0.75rem;
        color: #86efac;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
    }}

    .pg-hint {{
        margin-top: 1.1rem;
        font-size: 0.8rem;
        color: #8f88a3;
        text-align: center;
    }}

    @keyframes pg-spin {{
        to {{ transform: rotate(360deg); }}
    }}

    @keyframes pg-shimmer {{
        0% {{ background-position: 0% 0; }}
        100% {{ background-position: 200% 0; }}
    }}

    @keyframes pg-slide {{
        0% {{ margin-left: -40%; }}
        100% {{ margin-left: 100%; }}
    }}

    @media(max-width: 850px) {{
        .pg-steps {{
            grid-template-columns: 1fr;
        }}
    }}

    /* ---------------- YOUTUBE NOTE (FULL WIDTH) ---------------- */

    .yt-note {{
        margin-top: 1.2rem;
        padding: 1.6rem 1.8rem;
        border-radius: 24px;
        background:
            linear-gradient(135deg, rgba(251,191,36,0.08), rgba(168,85,247,0.05));
        border: 1px solid rgba(251, 191, 36, 0.28);
        border-left: 4px solid #fbbf24;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: 0 20px 60px rgba(0,0,0,0.22);
    }}

    .yt-note-head {{
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 1.1rem;
    }}

    .yt-note-icon {{
        flex-shrink: 0;
        width: 42px;
        height: 42px;
        border-radius: 14px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        background: rgba(251,191,36,0.14);
        border: 1px solid rgba(251,191,36,0.35);
    }}

    .yt-note-title {{
        font-size: 1.1rem;
        font-weight: 650;
        color: #fde68a;
        margin-bottom: 0.2rem;
    }}

    .yt-note-intro {{
        color: #bdb7c9;
        font-size: 0.9rem;
        line-height: 1.6;
        margin: 0;
    }}

    .yt-note-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }}

    .yt-note-card {{
        display: flex;
        gap: 14px;
        align-items: flex-start;
        padding: 1.1rem 1.2rem;
        border-radius: 18px;
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.09);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}

    .yt-note-card:hover {{
        transform: translateY(-3px);
        border-color: rgba(251,191,36,0.40);
    }}

    .yt-note-num {{
        flex-shrink: 0;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.82rem;
        font-weight: 700;
        color: #1a1325;
        background: linear-gradient(135deg, #fde68a, #fbbf24);
    }}

    .yt-note-card h4 {{
        margin: 0 0 0.3rem 0;
        font-size: 0.98rem;
        font-weight: 600;
        color: #ffffff;
    }}

    .yt-note-card p {{
        margin: 0;
        color: #aaa5b5;
        font-size: 0.86rem;
        line-height: 1.65;
    }}

    .yt-note-card b {{
        color: #ffffff;
        font-weight: 600;
    }}

    .yt-note a {{
        color: #c084fc;
        text-decoration: none;
        font-weight: 600;
    }}

    .yt-note a:hover {{
        text-decoration: underline;
    }}

    @media(max-width: 850px) {{
        .yt-note-grid {{
            grid-template-columns: 1fr;
        }}
    }}

    /* ---------------- FEATURE CARDS ---------------- */

    .feature-card {{
        height: 100%;
        min-height: 190px;
        padding: 1.8rem;
        border-radius: 24px;

        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.09);

        backdrop-filter: blur(14px);

        transition:
            transform 0.25s ease,
            border 0.25s ease,
            box-shadow 0.25s ease;
    }}

    .feature-card:hover {{
        transform: translateY(-5px);
        border-color: rgba(168, 85, 247, 0.45);
        box-shadow: 0 15px 40px rgba(0,0,0,0.20);
    }}

    .feature-icon {{
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }}

    .feature-card h3 {{
        font-size: 1.05rem;
        margin-bottom: 0.65rem;
        color: white;
    }}

    .feature-card p {{
        color: #9d98aa;
        font-size: 0.9rem;
        line-height: 1.65;
    }}

    /* ---------------- RESULT CONTENT ---------------- */

    .result-content {{
        white-space: pre-wrap;
        color: #d6d1df;
        line-height: 1.85;
        font-size: 1rem;
    }}

    /* ---------------- CHAT ---------------- */

    .chat-header {{
        text-align: center;
        margin-bottom: 1.5rem;
    }}

    .chat-header h2 {{
        color: white;
        font-size: 2.5rem;
        margin-bottom: 0.4rem;
    }}

    .chat-header p {{
        color: #9d98aa;
    }}

    /* ---------------- INPUTS ---------------- */

    .stTextInput input {{
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: white !important;
        border-radius: 999px !important;
    }}

    .stTextInput input:focus {{
        border-color: #a855f7 !important;
        box-shadow: 0 0 0 2px rgba(168,85,247,0.15) !important;
    }}

    .stTextInput input:disabled {{
        opacity: 0.4;
        cursor: not-allowed;
    }}

    /* ---------------- FILE UPLOADER ---------------- */

    div[data-testid="stFileUploader"] {{
        background: rgba(255,255,255,0.025);
        border-radius: 20px;
        padding: 0.7rem;
    }}

    div[data-testid="stFileUploaderDropzone"] {{
        background: rgba(255,255,255,0.025);
        border: 1px dashed rgba(168, 85, 247, 0.5);
        border-radius: 20px;
    }}

    /* ---------------- BACKGROUND GLOW ---------------- */

    .glow {{
        position: fixed;
        width: 500px;
        height: 350px;
        background: rgba(125, 30, 255, 0.12);
        filter: blur(120px);
        border-radius: 50%;
        top: 25%;
        left: 50%;
        transform: translateX(-50%);
        z-index: -1;
        pointer-events: none;
    }}

    @media(max-width: 850px) {{
        .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}

        .hero h1 {{
            letter-spacing: -1px;
        }}
    }}

    </style>

    <div class="glow"></div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# CLEAN AI OUTPUT
# =========================================================
def clean_ai_text(text):
    """
    Removes unwanted Markdown formatting and generic AI headings.
    This keeps the generated content clean inside the UI.
    """

    if not text:
        return ""

    text = str(text)

    # Remove Markdown bold / italic markers
    text = text.replace("**", "")
    text = text.replace("__", "")

    # Remove common unnecessary headings from the beginning
    text = re.sub(
        r"^\s*(combined\s+summary|summary|final\s+summary)\s*:?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove Markdown heading symbols
    text = re.sub(r"^\s*#+\s*", "", text, flags=re.MULTILINE)

    # Clean excessive empty lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def prepare_markdown(text):
    """
    Light cleanup that KEEPS real Markdown (bold, lists, headings)
    so it can be rendered properly with st.markdown.
    """
    if not text:
        return ""

    text = str(text).replace("\r\n", "\n")

    # Drop a leading generic "Summary:" style heading
    text = re.sub(
        r"^\s*(?:#+\s*)?\**(?:combined\s+summary|final\s+summary|summary)\**\s*(?::|\n)\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove blank lines right before list items -> tight, clean lists
    text = re.sub(
        r"\n[ \t]*\n(?=[ \t]*(?:[-*\u2022+]|\d+[.)])[ \t]+\S)",
        "\n",
        text,
    )

    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


_NUM_RE = re.compile(r"^ {0,3}(\d{1,3})[.)]\s*(.*)$")
_BUL_RE = re.compile(r"^ {0,1}[-*\u2022]\s+(.*)$")


def split_items(text):
    """
    Splits an LLM list into separate items so each can be shown as a card.
    Returns (preamble, [item_markdown, ...]). If it is not a clear list,
    the whole text comes back as a single item.
    """
    lines = text.split("\n")

    n_num = sum(1 for line in lines if _NUM_RE.match(line))
    n_bul = sum(1 for line in lines if _BUL_RE.match(line))

    if n_num >= 2:
        matcher = lambda line: (_NUM_RE.match(line).group(2) if _NUM_RE.match(line) else None)
    elif n_bul >= 2:
        matcher = lambda line: (_BUL_RE.match(line).group(1) if _BUL_RE.match(line) else None)
    else:
        return "", [text]

    preamble, items, current = [], [], None

    for line in lines:
        head = matcher(line)
        if head is not None:
            if current is not None:
                items.append(current)
            current = [head] if head.strip() else []
        elif current is None:
            preamble.append(line)
        else:
            current.append(line)

    if current is not None:
        items.append(current)

    cleaned = []
    for item in items:
        first = item[0] if item and not item[0].startswith((" ", "\t")) else None
        if first is not None:
            body = first + "\n" + textwrap.dedent("\n".join(item[1:]))
        else:
            body = textwrap.dedent("\n".join(item))
        body = re.sub(r"\n{3,}", "\n\n", body).strip()
        if body:
            cleaned.append(body)

    return "\n".join(preamble).strip(), cleaned or [text]


def word_count(text):
    return len(str(text or "").split())


def read_minutes(text):
    return max(1, round(word_count(text) / 200))


def file_stub(title):
    stub = re.sub(r"[^A-Za-z0-9]+", "-", str(title)).strip("-")[:50]
    return stub or "analysis"


# =========================================================
# SESSION STATE
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "Upload File"

if "result" not in st.session_state:
    st.session_state.result = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# NAVIGATION
# =========================================================
nav_items = [
    ("Upload", "Upload File", ":material/upload:"),
    ("Summary", "Summary", ":material/description:"),
    ("Action Items", "Action Items", ":material/task_alt:"),
    ("Decisions", "Key Decisions", ":material/gavel:"),
    ("Questions", "Open Questions", ":material/help:"),
]

# Highlight the button of the page that is currently open
active_selector = ".st-key-chat_button"
for i, (_, page_name, _) in enumerate(nav_items):
    if st.session_state.page == page_name:
        active_selector = f".st-key-nav_{i}"

st.markdown(
    f"""
    <style>

    /* Never cut button text with "..." */
    div.stButton > button p {{
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
        font-size: 0.86rem;
        font-weight: 550;
        letter-spacing: 0.1px;
    }}

    /* Compact nav pills */
    [class*="st-key-nav_"] button,
    .st-key-chat_button button {{
        min-height: 44px;
        padding: 0.45rem 0.9rem !important;
        gap: 0.4rem;
    }}

    /* Material icons inside nav buttons */
    [class*="st-key-nav_"] button span[data-testid="stIconMaterial"],
    .st-key-chat_button button span[data-testid="stIconMaterial"] {{
        font-size: 1.15rem;
        color: #c4b5fd;
    }}

    /* Chat with AI = call-to-action pill */
    .st-key-chat_button button {{
        background: linear-gradient(135deg, #a855f7, #6d28d9) !important;
        border: 1px solid rgba(216, 180, 254, 0.45) !important;
        color: #ffffff !important;
        box-shadow: 0 6px 24px rgba(139, 92, 246, 0.35);
    }}

    .st-key-chat_button button span[data-testid="stIconMaterial"] {{
        color: #ffffff;
    }}

    .st-key-chat_button button:hover {{
        box-shadow: 0 8px 30px rgba(168, 85, 247, 0.55);
        filter: brightness(1.08);
    }}

    /* Active page */
    {active_selector} button {{
        background: rgba(168, 85, 247, 0.20) !important;
        border-color: rgba(192, 132, 252, 0.85) !important;
        color: #ffffff !important;
        box-shadow: 0 0 0 1px rgba(168,85,247,0.25),
                    0 6px 24px rgba(139, 92, 246, 0.30);
    }}

    {active_selector} button span[data-testid="stIconMaterial"] {{
        color: #ffffff;
    }}

    /* Make sure nothing inside a button clips its label */
    [class*="st-key-nav_"] button,
    .st-key-chat_button button,
    [class*="st-key-nav_"] button > div,
    .st-key-chat_button button > div,
    [class*="st-key-nav_"] button [data-testid="stMarkdownContainer"],
    .st-key-chat_button button [data-testid="stMarkdownContainer"] {{
        overflow: visible !important;
        text-overflow: clip !important;
        max-width: none !important;
    }}

    [class*="st-key-nav_"] button,
    .st-key-chat_button button {{
        padding: 0.45rem 0.7rem !important;
    }}

    /* ---------------- BRAND ---------------- */

    .nav-brand {{
        display: flex;
        align-items: center;
        gap: 12px;
        height: 44px;
        padding-top: 0;
        padding-right: 1.2rem;
        white-space: nowrap;
    }}

    .brand-icon {{
        position: relative;
        flex-shrink: 0;
        width: 42px;
        height: 42px;
        border-radius: 14px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #c084fc 0%, #8b5cf6 50%, #5b21b6 100%);
        border: 1px solid rgba(255,255,255,0.25);
        box-shadow:
            0 0 24px rgba(168, 85, 247, 0.55),
            inset 0 1px 0 rgba(255,255,255,0.35);
    }}

    .brand-text {{
        display: flex;
        flex-direction: column;
        line-height: 1.1;
    }}

    .brand-name {{
        font-size: 1.08rem;
        font-weight: 700;
        letter-spacing: -0.4px;
        color: #ffffff;
    }}

    .brand-name .brand-ai {{
        background: linear-gradient(90deg, #e9d5ff, #c084fc, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-right: 4px;
    }}

    .brand-tag {{
        margin-top: 3px;
        font-size: 0.62rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        color: #8f88a3;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


def nav_button(label, key, icon=None):
    """Button with a clean Material icon (falls back to text on old Streamlit)."""
    try:
        return st.button(label, key=key, icon=icon)
    except TypeError:
        return st.button(label, key=key)


nav_cols = st.columns([3.1, 1.35, 1.55, 1.8, 1.5, 1.55, 1.75], gap="small")

with nav_cols[0]:
    brand_html = (
        '<div class="nav-brand">'
        '<span class="brand-icon">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M7 5.2v13.6a1 1 0 0 0 1.5.86l11-6.8a1 1 0 0 0 0-1.72l-11-6.8A1 1 0 0 0 7 5.2z" fill="#ffffff"/>'
        '<path d="M19.5 1.5l.9 2.4 2.4.9-2.4.9-.9 2.4-.9-2.4-2.4-.9 2.4-.9z" fill="#ffffff" opacity="0.9"/>'
        '</svg>'
        '</span>'
        '<span class="brand-text">'
        '<span class="brand-name"><span class="brand-ai">AI</span>Video Assistance</span>'
        '<span class="brand-tag">Understand more. Watch less.</span>'
        '</span>'
        '</div>'
    )
    st.markdown(brand_html, unsafe_allow_html=True)

for i, (label, page_name, icon) in enumerate(nav_items):
    with nav_cols[i + 1]:
        if nav_button(label, f"nav_{i}", icon):
            st.session_state.page = page_name
            st.rerun()

with nav_cols[6]:
    if nav_button("Chat with AI", "chat_button", ":material/chat:"):
        st.session_state.page = "Chat with AI"
        st.rerun()


# =========================================================
# CSS FOR RESULT PAGES + CHAT
# =========================================================
st.markdown(
    """
    <style>

    /* ---------- pill style for download buttons ---------- */
    div.stDownloadButton > button {
        width: 100%;
        min-height: 44px;
        border-radius: 999px !important;
        border: 1px solid rgba(168, 85, 247, 0.45);
        background: rgba(139, 92, 246, 0.12);
        color: #f3e8ff;
        font-weight: 550;
        padding: 0.45rem 1rem;
        transition: all 0.2s ease;
    }
    div.stDownloadButton > button:hover {
        transform: translateY(-2px);
        border-color: rgba(192, 132, 252, 0.9);
        background: rgba(139, 92, 246, 0.22);
        color: #ffffff;
        box-shadow: 0 6px 22px rgba(139, 92, 246, 0.25);
    }
    div.stDownloadButton > button p {
        white-space: nowrap !important;
        font-size: 0.86rem;
    }

    /* ---------- result header ---------- */
    .rh-label {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.9px;
        color: #a78bfa;
        margin-bottom: 0.35rem;
    }
    .rh-title {
        font-size: 1.3rem;
        font-weight: 650;
        color: #ffffff;
        line-height: 1.35;
        margin-bottom: 0.75rem;
    }
    .chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }
    .chip {
        font-size: 0.78rem;
        font-weight: 600;
        color: #d8b4fe;
        padding: 4px 12px;
        border-radius: 999px;
        background: rgba(139, 92, 246, 0.12);
        border: 1px solid rgba(168, 85, 247, 0.28);
    }

    /* ---------- numbered item badge ---------- */
    .item-num {
        width: 42px;
        height: 42px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.95rem;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
        color: var(--accent);
        background: color-mix(in srgb, var(--accent) 14%, transparent);
        border: 1px solid color-mix(in srgb, var(--accent) 40%, transparent);
    }

    /* ---------- real markdown typography inside cards ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] p,
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] li {
        color: #d6d1df;
        font-size: 1rem;
        line-height: 1.75;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] strong {
        color: #ffffff;
        font-weight: 650;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] ul,
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] ol {
        padding-left: 1.4rem;
        margin: 0.35rem 0;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] li {
        margin: 0.3rem 0;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] li::marker {
        color: #a855f7;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] li p {
        margin: 0;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] h1,
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] h2,
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] h3,
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] h4 {
        font-size: 1.15rem;
        font-weight: 650;
        color: #ffffff;
        letter-spacing: -0.2px;
        padding: 0;
        margin: 1.1rem 0 0.4rem 0;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] h1:first-child,
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] h2:first-child,
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] h3:first-child {
        margin-top: 0;
    }

    /* ---------- empty state ---------- */
    .empty-state {
        text-align: center;
        padding: 3rem 1.5rem;
        border-radius: 26px;
        background: rgba(16, 12, 25, 0.60);
        border: 1px dashed rgba(168, 85, 247, 0.35);
    }
    .empty-state h3 { color: #ffffff; font-size: 1.25rem; margin-bottom: 0.4rem; }
    .empty-state p { color: #9d98aa; font-size: 0.95rem; margin: 0; }

    /* ---------- transcript expander ---------- */
    div[data-testid="stExpander"] {
        background: rgba(16, 12, 25, 0.60);
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 20px !important;
        margin-top: 0.8rem;
    }
    div[data-testid="stExpander"] summary {
        font-weight: 600;
        color: #e9d5ff;
    }

    /* ---------- chat ---------- */
    .chat-welcome {
        text-align: center;
        padding: 2rem 1rem 1rem;
    }
    .chat-welcome h3 { color: #ffffff; font-size: 1.3rem; margin-bottom: 0.3rem; }
    .chat-welcome p { color: #9d98aa; font-size: 0.92rem; margin-bottom: 0.4rem; }

    [data-testid="stChatMessage"] {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 22px;
        padding: 1rem 1.3rem;
        margin-bottom: 0.9rem;
        backdrop-filter: blur(14px);
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background: rgba(139, 92, 246, 0.12);
        border-color: rgba(168, 85, 247, 0.35);
    }
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        background: linear-gradient(135deg, #a855f7, #6d28d9) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {
        color: #e4e0ee;
        line-height: 1.75;
    }
    [data-testid="stChatMessage"] strong { color: #ffffff; }
    [data-testid="stChatMessage"] li::marker { color: #a855f7; }

    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottomBlockContainer"] {
        background: transparent !important;
    }
    [data-testid="stBottom"] {
        background: linear-gradient(to top, rgba(7, 6, 11, 0.96) 55%, transparent) !important;
    }
    [data-testid="stChatInput"] {
        background: rgba(16, 12, 25, 0.88) !important;
        border: 1px solid rgba(168, 85, 247, 0.38) !important;
        border-radius: 999px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.35);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stChatInput"] > div {
        background: transparent !important;
        border: none !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #a855f7 !important;
        box-shadow: 0 0 0 3px rgba(168,85,247,0.18), 0 10px 40px rgba(0,0,0,0.35);
    }
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================
def require_result():

    if st.session_state.result is None:

        st.markdown(
            """
            <div class="glass-card" style="text-align:center; margin-top:3rem;">
                <h2 style="color:white;">No video processed yet 🎬</h2>
                <p style="color:#9d98aa;">
                    Upload a video or paste a YouTube link first to unlock
                    summaries, insights and AI chat.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("📤 Upload a Video"):
            st.session_state.page = "Upload File"
            st.rerun()

        return False

    return True


def render_hero(badge, title, subtitle=None):
    # flush-left, no blank lines -> avoids Markdown code-block bug
    sub = f"<p>{html.escape(subtitle)}</p>" if subtitle else ""
    st.markdown(
        '<div class="hero" style="padding-bottom:1rem;">'
        f'<div class="badge">✦ {html.escape(badge)}</div>'
        f'<h1 style="font-size:2.7rem;">{html.escape(title)}</h1>'
        f'{sub}'
        '</div>',
        unsafe_allow_html=True,
    )


def download_btn(label, data, file_name, key, mime="text/markdown"):
    try:
        st.download_button(
            label, data=data, file_name=file_name, mime=mime,
            key=key, icon=":material/download:",
        )
    except TypeError:
        st.download_button(
            label, data=data, file_name=file_name, mime=mime, key=key,
        )


def two_cols(ratios):
    try:
        return st.columns(ratios, vertical_alignment="center")
    except TypeError:
        return st.columns(ratios)


def chips_html(chips):
    return (
        '<div class="chips">'
        + "".join(f'<span class="chip">{html.escape(c)}</span>' for c in chips)
        + '</div>'
    )


def result_header(video_title, chips, download_data, stub, key):
    """Card with video title, small stat chips and a download button."""
    with st.container(border=True):
        left, right = two_cols([5, 1.5])
        with left:
            st.markdown(
                '<div class="rh-label">ANALYSIS FOR</div>'
                f'<div class="rh-title">{html.escape(video_title)}</div>'
                f'{chips_html(chips)}',
                unsafe_allow_html=True,
            )
        with right:
            download_btn("Download", download_data, f"{stub}.md", key)


def show_items_page(title, content_key, accent, noun, key_stub):
    """Action items / decisions / questions -> one card per item."""
    result = st.session_state.result
    video_title = clean_ai_text(result.get("title", "Your Video"))
    content = prepare_markdown(result.get(content_key, ""))

    render_hero("AI GENERATED INSIGHT", title)

    is_empty = (not content) or (
        len(content) < 80 and re.match(r"^(no|none|n/a)\b", content.lower())
    )

    if is_empty:
        st.markdown(
            '<div class="empty-state">'
            f'<h3>No {noun} found</h3>'
            f'<p>The AI did not detect any {noun} in this video.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    preamble, items = split_items(content)
    stub = f"{file_stub(video_title)}-{key_stub}"

    chips = [f"{len(items)} {noun}"] if len(items) > 1 else [noun.capitalize()]
    result_header(
        video_title,
        chips,
        f"# {title} - {video_title}\n\n{content}",
        stub,
        f"dl_{key_stub}",
    )

    if preamble:
        st.markdown(preamble)

    if len(items) == 1:
        with st.container(border=True):
            st.markdown(items[0])
        return

    for i, body in enumerate(items, start=1):
        with st.container(border=True):
            c_num, c_body = st.columns([0.9, 12], gap="small")
            with c_num:
                st.markdown(
                    f'<div class="item-num" style="--accent:{accent}">{i:02d}</div>',
                    unsafe_allow_html=True,
                )
            with c_body:
                st.markdown(body)


# =========================================================
# LIVE PROGRESS (shows exactly what the pipeline is doing)
# =========================================================
PIPELINE_STAGES = [
    ("download",  "Preparing audio",          "Extracting and cleaning audio from your source"),
    ("transcribe", "Transcribing speech",     "Converting speech to text"),
    ("summary",   "Writing summary",          "LLM is condensing the key ideas"),
    ("actions",   "Extracting action items",  "LLM is listing who needs to do what"),
    ("decisions", "Finding key decisions",    "LLM is picking out decisions that were made"),
    ("questions", "Spotting open questions",  "LLM is noting what is still unresolved"),
    ("index",     "Building knowledge base",  "Embedding the transcript so you can chat with it"),
]

STAGE_KEYS = [key for key, _, _ in PIPELINE_STAGES]

# run_pipeline must accept `progress_callback` for live steps (see main.py note)
SUPPORTS_PROGRESS = "progress_callback" in inspect.signature(run_pipeline).parameters


def format_seconds(seconds):
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes:02d}:{secs:02d}"


def build_progress_html(current_idx, durations, details, started_at, indeterminate=False):
    """
    current_idx: index of the running stage (-1 = not started,
                 len(stages) = everything finished)
    NOTE: HTML is built flush-left with no blank lines on purpose,
    otherwise Streamlit's Markdown turns it into a code block.
    """
    total = len(PIPELINE_STAGES)
    elapsed = format_seconds(time.time() - started_at)

    if indeterminate:
        title = "AI is analyzing your video"
        bar = '<div class="pg-bar"><div class="pg-bar-fill pg-bar-indeterminate"></div></div>'
        steps_html = ""
    else:
        finished = current_idx >= total
        title = "Analysis complete" if finished else "AI is analyzing your video"
        progress = total if finished else max(current_idx, 0) + 0.5
        percent = int(progress / total * 100)
        bar = f'<div class="pg-bar"><div class="pg-bar-fill" style="width:{percent}%"></div></div>'

        steps_html = '<div class="pg-steps">'
        for i, (key, label, default_detail) in enumerate(PIPELINE_STAGES):
            if i < current_idx:
                state, dot = "done", "✓"
            elif i == current_idx:
                state, dot = "active", ""
            else:
                state, dot = "pending", ""

            detail = details.get(key, default_detail) if state == "active" else ""
            took = ""
            if state == "done" and durations.get(i) is not None:
                took = f'<span class="pg-took">{durations[i]:.0f}s</span>'

            steps_html += (
                f'<div class="pg-step {state}">'
                f'<span class="pg-dot">{dot}</span>'
                '<div>'
                f'<div class="pg-label">{label}</div>'
                + (f'<div class="pg-detail">{detail}</div>' if detail else "")
                + '</div>'
                f'{took}'
                '</div>'
            )
        steps_html += '</div>'

    return (
        '<div class="pg-card">'
        '<div class="pg-head">'
        f'<div class="pg-title">{title}</div>'
        f'<div class="pg-time">⏱ {elapsed}</div>'
        '</div>'
        f'{bar}'
        f'{steps_html}'
        '<div class="pg-hint">Long videos can take a few minutes — please keep this tab open.</div>'
        '</div>'
    )


# =========================================================
# UPLOAD PAGE
# =========================================================
if st.session_state.page == "Upload File":

    st.markdown(
    """
    <div class="hero">
    <div class="badge">✦ AI THAT UNDERSTANDS YOUR VIDEO</div>
    <h1>Your Video.<br><span class="gradient-text">Fully Understood.</span></h1>
    <p>
        Turn videos, podcasts and meeting recordings into summaries,
        action items, key decisions and intelligent answers — all in one place.
    </p>
    </div>
    """,
    unsafe_allow_html=True
)

    st.markdown(
        """
        <div class="section-title">Add your content</div>
        <div class="section-subtitle">
            Upload a file from your device or paste a YouTube link — use one at a time.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # SIDE-BY-SIDE INPUTS (only ONE can be active at a time)
    #   - File uploaded      -> YouTube box gets disabled
    #   - YouTube link typed -> Upload box gets disabled
    # Clear the active one to re-enable the other.
    # -----------------------------------------------------
    file_active = st.session_state.get("file_input") is not None
    yt_active = bool(st.session_state.get("yt_input", "").strip())

    col_file, col_yt = st.columns(2, gap="large")

    with col_file:
        with st.container(border=True):
            st.markdown(
                """
                <div class="input-card-title">📁 Upload File</div>
                <div class="input-card-sub">Video or audio from your device</div>
                """,
                unsafe_allow_html=True,
            )

            uploaded_file = st.file_uploader(
                "Upload video or audio",
                type=[
                    "mp4", "mkv", "avi", "mov",
                    "webm", "mp3", "wav", "m4a"
                ],
                key="file_input",
                disabled=yt_active,
                label_visibility="collapsed",
            )

            if yt_active:
                st.caption("🔒 YouTube link active hai — link clear karo to upload use kar sakte ho.")

    with col_yt:
        with st.container(border=True):
            st.markdown(
                """
                <div class="input-card-title">🔗 YouTube Link</div>
                <div class="input-card-sub">Paste any YouTube video URL</div>
                """,
                unsafe_allow_html=True,
            )

            youtube_url = st.text_input(
                "YouTube URL",
                placeholder="Paste your YouTube video link here...",
                key="yt_input",
                disabled=file_active,
                label_visibility="collapsed",
            )

            if file_active:
                st.caption("🔒 File upload active hai — file remove karo to YouTube link use kar sakte ho.")

    language = st.selectbox(
        "Audio language",
        options=["english", "hinglish"],
        format_func=lambda x:
            "English" if x == "english" else "Hinglish",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    process_button = st.button(
        "✨ Analyze with AI",
        type="primary",
        use_container_width=True,
    )

    # PROCESS VIDEO
    if process_button:

        youtube_url = (youtube_url or "").strip()

        if not youtube_url and uploaded_file is None:
            st.warning(
                "Please upload a file or paste a YouTube link first."
            )

        else:

            temp_path = None
            progress_state = {"idx": -1, "t": 0}

            try:

                if uploaded_file is not None:

                    suffix = Path(uploaded_file.name).suffix

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=suffix,
                    ) as temp_file:

                        temp_file.write(uploaded_file.getbuffer())
                        temp_path = temp_file.name

                    source_path = temp_path

                else:
                    source_path = youtube_url

                progress_box = st.empty()
                started_at = time.time()
                durations, details = {}, {}
                progress_state["idx"] = -1
                progress_state["t"] = started_at

                # Language specific wording for the transcription step
                details["transcribe"] = (
                    "Sarvam AI is transcribing and translating to English"
                    if language == "hinglish"
                    else "Whisper is converting speech to text"
                )

                def on_progress(stage, detail=None):
                    """Called by run_pipeline every time a new step starts."""
                    if stage not in STAGE_KEYS:
                        return

                    idx = STAGE_KEYS.index(stage)
                    now = time.time()

                    if detail:
                        details[stage] = detail

                    if idx > progress_state["idx"]:
                        if progress_state["idx"] >= 0:
                            durations[progress_state["idx"]] = now - progress_state["t"]
                        progress_state["idx"] = idx
                        progress_state["t"] = now

                    progress_box.markdown(
                        build_progress_html(
                            progress_state["idx"], durations, details, started_at
                        ),
                        unsafe_allow_html=True,
                    )

                if SUPPORTS_PROGRESS:
                    on_progress("download")
                    result = run_pipeline(
                        source_path,
                        language=language,
                        progress_callback=on_progress,
                    )
                else:
                    # main.py not updated yet -> honest "working..." animation
                    progress_box.markdown(
                        build_progress_html(-1, {}, {}, started_at, indeterminate=True),
                        unsafe_allow_html=True,
                    )
                    result = run_pipeline(source_path, language=language)

                st.session_state.result = result
                st.session_state.messages = []

                if SUPPORTS_PROGRESS:
                    durations[progress_state["idx"]] = time.time() - progress_state["t"]
                    progress_box.markdown(
                        build_progress_html(
                            len(PIPELINE_STAGES), durations, details, started_at
                        ),
                        unsafe_allow_html=True,
                    )
                    time.sleep(1.0)

                st.session_state.page = "Summary"
                st.rerun()

            except Exception as e:

                failed_idx = progress_state["idx"]
                failed_step = (
                    PIPELINE_STAGES[failed_idx][1]
                    if 0 <= failed_idx < len(PIPELINE_STAGES)
                    else "starting the analysis"
                )
                st.error(
                    f"Something went wrong during: **{failed_step}**\n\n{e}"
                )

            finally:

                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass

    # -------- IMPORTANT NOTE (full width, always visible to every user) --------
    GITHUB_REPO_URL = "https://github.com/mohakmogs/AI-Video-Assistance"

    # NOTE: HTML is flush-left with NO blank lines on purpose.
    # Streamlit's Markdown treats 4+ space indented lines after a blank line as a code block.
    note_html = (
        '<div class="yt-note">'
        '<div class="yt-note-head">'
        '<div class="yt-note-icon">⚠️</div>'
        '<div>'
        '<div class="yt-note-title">Important note about YouTube links</div>'
        '<p class="yt-note-intro">'
        'YouTube generally blocks cloud server IPs for security reasons, '
        'so a YouTube link may sometimes fail on this hosted app. '
        'If that happens, you have two easy options:'
        '</p>'
        '</div>'
        '</div>'
        '<div class="yt-note-grid">'
        '<div class="yt-note-card">'
        '<span class="yt-note-num">1</span>'
        '<div>'
        '<h4>Download &amp; upload</h4>'
        '<p>Download the video from YouTube manually and upload it '
        'using <b>Upload File</b> — it works every time.</p>'
        '</div>'
        '</div>'
        '<div class="yt-note-card">'
        '<span class="yt-note-num">2</span>'
        '<div>'
        '<h4>Run it locally</h4>'
        f'<p>Clone my <a href="{GITHUB_REPO_URL}" target="_blank">GitHub repo</a> '
        'and install the dependencies. On your own PC the YouTube link '
        'feature works perfectly, since the blocking only affects '
        'cloud IP addresses.</p>'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(note_html, unsafe_allow_html=True)

    # =====================================================
    # WHY AI VIDEO ASSISTANCE
    # =====================================================
    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="text-align:center; margin-bottom:1.8rem;">
        <div class="badge">WHY AI VIDEO ASSISTANCE?</div>

        <h2 style="
            color:white;
            font-size:2.2rem;
            margin-bottom:0.7rem;
        ">
            Why use multiple tools when one AI can do it all?
        </h2>

        <p style="
            max-width:720px;
            margin:auto;
            color:#9d98aa;
            line-height:1.7;
        ">
            YouTube, Google and Gemini can help you understand content,
            but AI Video Assistance brings the complete workflow together
            in one powerful place.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    f1, f2, f3 = st.columns(3)

    with f1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🧩</div>
                <h3>All-in-One Experience</h3>
                <p>
                    No need to jump between YouTube transcripts, search engines,
                    AI chatbots and separate analysis tools. Add your video and
                    get everything in one workflow.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with f2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <h3>More Than Just a Summary</h3>
                <p>
                    Discover summaries, action items, key decisions and open
                    questions — then ask AI anything about the actual content
                    of your video.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with f3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h3>One Powerful Assistant</h3>
                <p>
                    From podcasts and YouTube videos to meetings and recordings,
                    AI Video Assistance helps you understand more, faster —
                    without switching between tools.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# SUMMARY PAGE
# =========================================================
elif st.session_state.page == "Summary":

    if require_result():

        result = st.session_state.result

        video_title = clean_ai_text(result.get("title", "Your Video"))
        summary_md = prepare_markdown(result.get("summary", "")) or "No summary available."
        transcript = result.get("transcript", "") or ""
        stub = file_stub(video_title)

        render_hero(
            "VIDEO SUMMARY",
            video_title,
            "The essential ideas, condensed into a clear overview.",
        )

        toolbar_left, toolbar_right = two_cols([5, 1.5])
        with toolbar_left:
            st.markdown(
                chips_html([
                    f"~{read_minutes(summary_md)} min read",
                    f"{word_count(transcript):,} words transcribed",
                ]),
                unsafe_allow_html=True,
            )
        with toolbar_right:
            download_btn(
                "Download",
                f"# {video_title}\n\n{summary_md}",
                f"{stub}-summary.md",
                "dl_summary",
            )

        with st.container(border=True):
            st.markdown(summary_md)

        with st.expander("View full transcript"):
            st.write(clean_ai_text(transcript))
            download_btn(
                "Download transcript",
                transcript,
                f"{stub}-transcript.txt",
                "dl_transcript",
                mime="text/plain",
            )


# =========================================================
# ACTION ITEMS
# =========================================================
elif st.session_state.page == "Action Items":

    if require_result():
        show_items_page("Action Items", "action_items", "#34d399", "action items", "action-items")


# =========================================================
# KEY DECISIONS
# =========================================================
elif st.session_state.page == "Key Decisions":

    if require_result():
        show_items_page("Key Decisions", "key_decisions", "#c084fc", "decisions", "decisions")


# =========================================================
# OPEN QUESTIONS
# =========================================================
elif st.session_state.page == "Open Questions":

    if require_result():
        show_items_page("Open Questions", "open_questions", "#fbbf24", "questions", "questions")


# =========================================================
# CHAT WITH AI
# =========================================================
elif st.session_state.page == "Chat with AI":

    CHAT_SUGGESTIONS = [
        "Summarize the main points in 5 bullets",
        "What are the key takeaways?",
        "What action items were mentioned?",
        "Which topics were discussed in the most detail?",
    ]

    if require_result():

        video_title = clean_ai_text(
            st.session_state.result.get("title", "your video")
        )

        render_hero(
            "RAG POWERED CHAT",
            "Chat with your video",
            "Answers are grounded in the transcript of: " + video_title,
        )

        # A suggested question that was clicked on the previous run
        pending = st.session_state.pop("pending_question", None)

        suggestion_box = st.empty()

        if not st.session_state.messages and not pending:
            with suggestion_box.container():
                st.markdown(
                    '<div class="chat-welcome">'
                    '<h3>Ask anything about this video</h3>'
                    '<p>Pick a suggestion or type your own question below.</p>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                sugg_cols = st.columns(2)
                for i, suggestion in enumerate(CHAT_SUGGESTIONS):
                    with sugg_cols[i % 2]:
                        if st.button(suggestion, key=f"sugg_{i}"):
                            st.session_state.pending_question = suggestion
                            st.rerun()

        # Previous messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(prepare_markdown(message["content"]))

        typed = st.chat_input("Ask a question about the video...")
        question = typed or pending

        if question:

            suggestion_box.empty()

            st.session_state.messages.append(
                {"role": "user", "content": question}
            )

            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):

                with st.spinner("Searching the transcript..."):

                    try:

                        rag_chain = st.session_state.result.get("rag_chain")

                        answer = ask_question(rag_chain, question)
                        answer = prepare_markdown(answer)

                        st.markdown(answer)

                        st.session_state.messages.append(
                            {"role": "assistant", "content": answer}
                        )

                    except Exception as e:

                        st.error(
                            "Sorry, I couldn't process that question.\n\n"
                            f"Error: {e}"
                        )

        if st.session_state.messages:

            st.markdown("<br>", unsafe_allow_html=True)

            clear_col, _ = st.columns([1.4, 6])
            with clear_col:
                if st.button("Clear chat", key="clear_chat"):
                    st.session_state.messages = []
                    st.rerun()

            # keep the last message clear of the fixed input bar
            st.markdown("<div style='height:5rem'></div>", unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    """
    <div style="
        text-align:center;
        color:rgba(255,255,255,0.35);
        font-size:0.75rem;
        margin-top:4rem;
        padding-bottom:1rem;
    ">
        AI Video Assistance · Understand more. Watch less.
    </div>
    """,
    unsafe_allow_html=True,
)