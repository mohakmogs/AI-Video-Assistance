
import streamlit as st
import os
import re
import base64
import tempfile
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
nav_left, nav_center, nav_right = st.columns([1.7, 5.2, 1.4])

with nav_left:
    st.markdown(
        """
        <div class="nav-brand">
            <span class="brand-icon">👀</span>
            AI Video Assistance
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_center:
    nav_cols = st.columns(5)

    nav_items = [
        ("📤 Upload", "Upload File"),
        ("📄 Summary", "Summary"),
        ("✓ Action Items", "Action Items"),
        ("◆ Decisions", "Key Decisions"),
        ("❓ Questions", "Open Questions"),
    ]

    for col, (label, page_name) in zip(nav_cols, nav_items):
        with col:
            if st.button(label, key=f"nav_{page_name}"):
                st.session_state.page = page_name
                st.rerun()

with nav_right:
    if st.button("💬 Chat with AI", key="chat_button"):
        st.session_state.page = "Chat with AI"
        st.rerun()


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


def show_result_page(title, icon, content):

    content = clean_ai_text(content)

    st.markdown(
        f"""
        <div class="hero" style="padding-bottom:1rem;">
            <div class="badge">{icon} AI GENERATED INSIGHT</div>
            <h1 style="font-size:2.7rem;">{title}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    video_title = clean_ai_text(
        st.session_state.result.get("title", "Your Video")
    )

    # Use st.markdown for safe text rendering
    st.markdown(
        f"""
        <div class="glass-card">
        <div style="
            color:#a78bfa;
            font-size:0.78rem;
            font-weight:600;
            letter-spacing:0.5px;
            margin-bottom:0.7rem;
        ">
            ANALYSIS FOR
        </div>

        <div style="
            font-size:1.3rem;
            color:white;
            font-weight:600;
            margin-bottom:1.5rem;
        ">
            {video_title}
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Content displayed separately to avoid ugly Markdown symbols
    with st.container():
        st.markdown(
            f"""
            <div class="glass-card" style="margin-top:1rem;">
                <div class="result-content">{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
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

    # st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-title">Add your content</div>
        <div class="section-subtitle">
            Paste a YouTube link or upload a video from your device.
        </div>
        """,
        unsafe_allow_html=True,
    )

    input_tab, upload_tab = st.tabs(
        ["🔗 YouTube Link", "📁 Upload Video"]
    )

    youtube_url = ""
    uploaded_file = None

    with input_tab:
        youtube_url = st.text_input(
            "YouTube URL",
            placeholder="Paste your YouTube video link here...",
        )

    with upload_tab:
        uploaded_file = st.file_uploader(
            "Upload video or audio",
            type=[
                "mp4", "mkv", "avi", "mov",
                "webm", "mp3", "wav", "m4a"
            ],
        )

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

    st.markdown("</div>", unsafe_allow_html=True)

    # PROCESS VIDEO
    if process_button:

        if not youtube_url and uploaded_file is None:
            st.warning(
                "Please paste a YouTube link or upload a file first."
            )

        else:

            temp_path = None

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
                    source_path = youtube_url.strip()

                with st.status(
                    "🎬 AI is analyzing your video...",
                    expanded=True,
                ) as status:

                    st.write("📥 Processing audio...")
                    st.write("🎙️ Transcribing content...")
                    st.write("🧠 Generating AI insights...")
                    st.write("🔎 Building video knowledge base...")

                    result = run_pipeline(
                        source_path,
                        language=language,
                    )

                    st.session_state.result = result
                    st.session_state.messages = []

                    status.update(
                        label="✨ Analysis complete!",
                        state="complete",
                        expanded=False,
                    )

                st.session_state.page = "Summary"
                st.rerun()

            except Exception as e:

                st.error(
                    f"Something went wrong while analyzing the video:\n\n{e}"
                )

            finally:

                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass

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

        video_title = clean_ai_text(
            result.get("title", "Your Video")
        )

        summary = clean_ai_text(
            result.get("summary", "No summary available.")
        )

        st.markdown(
            f"""
            <div class="hero" style="padding-bottom:1rem;">
                <div class="badge">📄 VIDEO SUMMARY</div>

            <h1 style="font-size:2.7rem;">
                {video_title}
            </h1>

            <p>
                The essential ideas, condensed into a clear overview.
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="glass-card">
                <div class="result-content">{summary}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("📄 View full transcript"):
            transcript = result.get("transcript", "")
            st.write(clean_ai_text(transcript))


# =========================================================
# ACTION ITEMS
# =========================================================
elif st.session_state.page == "Action Items":

    if require_result():

        show_result_page(
            "Action Items",
            "✓",
            st.session_state.result.get(
                "action_items",
                "No action items found.",
            ),
        )


# =========================================================
# KEY DECISIONS
# =========================================================
elif st.session_state.page == "Key Decisions":

    if require_result():

        show_result_page(
            "Key Decisions",
            "◆",
            st.session_state.result.get(
                "key_decisions",
                "No key decisions found.",
            ),
        )


# =========================================================
# OPEN QUESTIONS
# =========================================================
elif st.session_state.page == "Open Questions":

    if require_result():

        show_result_page(
            "Open Questions",
            "❓",
            st.session_state.result.get(
                "open_questions",
                "No open questions found.",
            ),
        )


# =========================================================
# CHAT WITH AI
# =========================================================
elif st.session_state.page == "Chat with AI":

    if require_result():

        st.markdown(
            """
            <div class="chat-header">
                <div class="badge">💬 RAG POWERED CHAT</div>
                <h2>Chat with your video</h2>
                <p>
                    Ask anything about the content. Answers are based on
                    your video's transcript.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Previous messages
        for message in st.session_state.messages:

            with st.chat_message(message["role"]):
                st.markdown(
                    clean_ai_text(message["content"])
                )

        question = st.chat_input(
            "Ask a question about the video..."
        )

        if question:

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": question,
                }
            )

            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):

                with st.spinner("Thinking..."):

                    try:

                        rag_chain = (
                            st.session_state.result.get("rag_chain")
                        )

                        answer = ask_question(
                            rag_chain,
                            question,
                        )

                        answer = clean_ai_text(answer)

                        st.markdown(answer)

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer,
                            }
                        )

                    except Exception as e:

                        st.error(
                            "Sorry, I couldn't process that question.\n\n"
                            f"Error: {e}"
                        )

        if st.session_state.messages:

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🗑️ Clear conversation"):
                st.session_state.messages = []
                st.rerun()


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

