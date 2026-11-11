import streamlit as st
import requests
import base64
import mimetypes
import time
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
    background: rgba(255, 255, 255, 0.9);
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

# ---------------- SIDEBAR (TECHY & FIXI PROFILE) ----------------

with st.sidebar:
    st.markdown("## 🚀 DS-FixIT")
    st.caption("Universal AI Problem Detector • v3.4")

    st.divider()

    st.toggle("🌙 Dark mode", key="dark_mode")

    st.divider()

    # FIXI Dynamic Avatar & Expression
    st.markdown("### 🤖 FIXI Companion")
    
    st.markdown(f"""
    <div style="background: rgba(0, 159, 255, 0.08); padding: 14px; border-radius: 12px; text-align: center; border: 1px solid #009fff;">
        <span style="font-size: 38px;">🔮</span><br>
        <b style="color: #009fff; font
