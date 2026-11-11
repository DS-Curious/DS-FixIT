import streamlit as st
import requests
import base64
import mimetypes
import time
import re
from openai import OpenAI

st.set_page_config(
    page_title="DS-FixIT | Universal AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CONFIG & STYLING (#009fff → #ec2f4b GRADIENT THEME) ----------------

st.markdown("""
<style>
/* Base Light Theme Gradient: #009fff to #ec2f4b */
.stApp {
    background: linear-gradient(
        135deg,
        #f0f8ff 0%,
        #eef2f3 50%,
        #fff0f3 100%
    );
    color: #111827;
}

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg, #e0f2fe, #fce7f3, #fff1f2
    );
    border-right: 2px solid rgba(0, 159, 255, 0.2);
}

.main-title {
    font-size: 48px;
    font-weight: 900;
    background: linear-gradient(
        90deg, #009fff, #ec2f4b
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 1px;
}

.subtitle {
    color: #4b5563;
    font-size: 18px;
    font-weight: 600;
}

div.stButton > button {
    border-radius: 12px;
    background: linear-gradient(90deg, #009fff, #ec2f4b);
    color: #ffffff;
    font-weight: bold;
    border: none;
    box-shadow: 0 4px 12px rgba(0, 159, 255, 0.25);
    transition: all 0.3s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(236, 47, 75, 0.35);
}

.result-card {
    padding: 24px;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(0, 159, 255, 0.3);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
}

.tech-badge {
    background: #009fff;
    color: white;
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------

if "history" not in st.session_state:
    st.session_state.history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "fixi_mood" not in st.session_state:
    st.session_state.fixi_mood = "🚀 Online & Ready"

# ---------------- SIDEBAR (PROFESSIONAL FIXI PROFILE) ----------------

with st.sidebar:
    st.markdown("## 🚀 DS-FixIT")
    st.caption("Universal AI Problem Detector • v4.3")

    st.divider()

    st.toggle("🌙 Dark mode", key="dark_mode")

    st.divider()

    # FIXI Professional AI Companion Profile
    st.markdown("### 🤖 FIXI Companion")
    
    st.markdown(f"""
    <div style="background: rgba(0, 159, 255, 0.08); padding: 14px; border-radius: 14px; text-align: center; border: 1.5px solid #009fff; box-shadow: 0 4px 12px rgba(0,159,255,0.15);">
        <div style="font-size: 32px; margin-bottom: 4px;">🤖⚡</div>
        <b style="color: #009fff; font-size: 19px; letter-spacing: 0.5px;">FIXI</b><br>
        <span style="font-size: 11px; color: #555;"><i>Neural AI Assistant</i></span><br><br>
        <span style="font-size: 11px; color: #333;"><b>Status:</b> {st.session_state.fixi_mood}</span><br><br>
        <span class="tech-badge">Honest</span> 
        <span class="tech-badge">Polite</span> 
        <span class="tech-badge">Vision AI</span>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # Specialized Solvers (All 9 included)
    st.markdown("### 🛠️ Specialized Solvers")
    solver_mode = st.selectbox(
        "Select Domain Mode",
        [
            "General Problem Solver",
            "Code Doctor & Syntax Repair",
            "Math & Equation Solver",
            "Study Assistant",
            "Home & Hardware Fixer",
            "Plant & Flora Doctor",
            "Data & Log Inspector",
            "Sound Detective",
            "Writing & Text Doctor"
        ]
    )

    st.divider()

    # Conversation Search & Memory Vault
    st.markdown("### 🧠 FIXI Memory Vault")
    search_query = st.text_input("🔍 Search past sessions", placeholder="Keyword...")

    if not st.session_state.history:
        st.caption("No history logged yet.")
    else:
        filtered_history = [
            item for item in st.session_state.history 
            if search_query.lower() in item["title"].lower() or search_query.lower() in item["result"].lower()
        ] if search_query else st.session_state.history

        for i, item in enumerate(reversed(filtered_history[-10:])):
            if st.button(
                f"📌 {item['title'][:25]}...",
                key=f"history_{i}",
                use_container_width=True
            ):
                st.session_state.latest_result = item["result"]

    st.divider()

    with st.expander("ℹ️ About DS-FixIT & Creator"):
        st.write("**DS-FixIT** is a universal multi-modal AI problem detector powered by advanced vision and reasoning.")
        st.write("**Creator:** J.P. Dheepak Saianand")
        st.write("**Companion:** FIXI")
        st.caption("DS-FixIT © 2026 • Built with Streamlit & OpenRouter")

# ---------------- DARK MODE OVERRIDE ----------------

if st.session_state.dark_mode:
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(
            135deg, #090d16, #111827, #1f1118
        ) !important;
        color: #f3f4f6 !important;
    }
    [data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 2px solid rgba(0, 159, 255, 0.3);
    }
    .result-card {
        background: rgba(15, 23, 42, 0.95) !important;
        border: 1px solid #009fff !important;
        color: #f3f4f6 !important;
    }
    .subtitle {
        color: #f43f5e !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.markdown(
    '<div class="main-title">DS-FixIT 🚀</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Detect. Analyse. Fix. • Active Mode: ' + solver_mode + '</div>',
    unsafe_allow_html=True
)

st.write(
    "Detect code errors, mathematical proofs, study queries, acoustic anomalies, hardware faults, plant diseases, or text issues instantly. "
    "FIXI is ready to assist you with rigorous multi-perspective analysis."
)

st.divider()

# ---------------- INPUT SECTION ----------------

st.markdown("## 🚀 What's the problem today?")

col_desc, col_extra = st.columns(2)

with col_desc:
    description = st.text_area(
        "Describe your problem",
        placeholder="Explain what's happening or paste code/equations/errors...",
        height=140
    )

with col_extra:
    additional_info = st.text_area(
        "Additional Information (Optional Context)",
        placeholder="Provide environmental factors, OS, previous attempts, error logs...",
        height=140
    )

uploaded_files = st.file_uploader(
    "📎 Upload Evidence (Images, Audio, PDF, Text, or Code Files)",
    type=[
        "png", "jpg", "jpeg", "webp",
        "pdf", "txt", "csv", "py", "json",
        "mp3", "wav", "m4a"
    ],
    accept_multiple_files=True
