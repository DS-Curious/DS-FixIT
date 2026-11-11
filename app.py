import streamlit as st
import requests
import base64
import mimetypes
import time
from openai import OpenAI

st.set_page_config(
    page_title="DS-FixIT | Universal AI",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CONFIG & STYLING (CYAN-MINT-YELLOW GRADIENT & TECHY THEME) ----------------

st.markdown("""
<style>
/* Base Light Theme Gradient: Cyan, Mint, Yellow */
.stApp {
    background: linear-gradient(
        135deg,
        #e0fbfc 0%,
        #d8f3dc 50%,
        #fefae0 100%
    );
    color: #1d3557;
}

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg, #cbf3f0, #e8f5e9, #fefae0
    );
    border-right: 2px solid rgba(0, 174, 202, 0.2);
}

.main-title {
    font-size: 48px;
    font-weight: 900;
    background: linear-gradient(
        90deg, #0096c7, #2ec4b6, #e9c46a
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 1px;
}

.subtitle {
    color: #2b6777;
    font-size: 18px;
    font-weight: 600;
}

div.stButton > button {
    border-radius: 12px;
    background: linear-gradient(90deg, #00b4d8, #52b788);
    color: #ffffff;
    font-weight: bold;
    border: none;
    box-shadow: 0 4px 10px rgba(0,180,216,0.2);
    transition: all 0.3s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0,180,216,0.4);
}

.result-card {
    padding: 24px;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid #90e0ef;
    box-shadow: 0 8px 32px rgba(0, 119, 182, 0.08);
}

.tech-badge {
    background: #00b4d8;
    color: white;
    padding: 3px 8px;
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

# ---------------- SIDEBAR (TECHY & FIXI PROFILE) ----------------

with st.sidebar:
    st.markdown("## ⭐ DS-FixIT")
    st.caption("Universal AI Problem Detector • v2.6")

    st.divider()

    st.toggle("🌙 Dark mode", key="dark_mode")

    st.divider()

    # FIXI Companion Profile
    st.markdown("### 🤖 FIXI Companion")
    
    st.markdown("""
    <div style="background: rgba(0, 180, 216, 0.12); padding: 14px; border-radius: 12px; text-align: center; border: 1px solid #00b4d8;">
        <span style="font-size: 36px;">⭐</span><br>
        <b style="color: #0077b6; font-size: 18px;">FIXI</b><br>
        <span style="font-size: 12px; color: #555;"><i>Universal AI Companion</i></span><br><br>
        <span class="tech-badge">Honest</span> 
        <span class="tech-badge">Polite</span> 
        <span class="tech-badge">Accurate</span>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.caption("Mode: Universal Diagnostic & Support")

    st.divider()

    # Specialized Feature Modes
    st.markdown("### 🛠️ Specialized Solvers")
    solver_mode = st.selectbox(
        "Select Domain Solver Mode",
        [
            "General Problem Solver",
            "Code Doctor & Syntax Repair",
            "Math & Equation Solver",
            "Plant & Flora Doctor",
            "Home & Hardware Fixer",
            "Data & Log File Inspector",
            "Writing & Text Doctor"
        ]
    )

    st.divider()

    st.markdown("### 🧠 FIXI Memory Vault")
    st.caption("Recent diagnostic runs & sessions")

    if not st.session_state.history:
        st.caption("No history logged yet.")
    else:
        for i, item in enumerate(reversed(st.session_state.history[-10:])):
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

# ---------------- DARK MODE OVERRIDE (HIGH READABILITY CONTRAST) ----------------

if st.session_state.dark_mode:
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(
            135deg, #0b131f, #111d27, #1a2823
        ) !important;
        color: #f0fdf4 !important;
    }
    [data-testid="stSidebar"] {
        background: #0f1c24 !important;
        border-right: 2px solid rgba(46, 196, 182, 0.3);
    }
    .result-card {
        background: rgba(15, 28, 36, 0.9) !important;
        border: 1px solid #2ec4b6 !important;
        color: #f0fdf4 !important;
    }
    .subtitle {
        color: #4ade80 !important;
    }
    p, label, span, h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.markdown(
    '<div class="main-title">DS-FixIT ⭐</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Universal AI Problem Detector • Active Mode: ' + solver_mode + '</div>',
    unsafe_allow_html=True
)

st.write(
    "Identify bugs, hardware failures, plant conditions, mathematical steps, sound logs, or errors. "
    "FIXI is ready to assist with clear analysis and verified recommendations."
)

st.divider()

# ---------------- INPUT SECTION ----------------

st.markdown("## 🔍 What's the problem today?")

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
)

file_notes = {}
if uploaded_files:
    st.markdown("### 🗂️ Attached Evidence Context")
    for file in uploaded_files:
        c1, c2 = st.columns([1, 2])
        with c1:
            if file.type.startswith("image/"):
                st.image(file, caption=file.name, width=160)
            else:
                st.write(f"📁 **{file.name}** ({file.type or 'file'})")
        with c2:
            note = st.text_input(
                f"Optional extra note for {file.name}",
                placeholder="e.g. Error starts at line 45 or timestamp 0:15...",
                key=f"note_{file.name}"
            )
            if note:
                file_notes[file.name] = note

# ---------------- ANALYSIS ENGINE ----------------

if st.button(
    "⭐ ANALYSE WITH FIXI",
    type="primary",
    use_container_width=True
):

    if not description.strip() and not uploaded_files:
        st.warning("Please describe the problem or upload evidence (image, audio, or file).")

    else:
        try:
            api_key = st.secrets["OPENROUTER_APIKEY"]

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )

            notes_str = "\n".join([f"- {fname}: {note}" for fname, note in file_notes.items()])

            prompt = f"""
You are FIXI, the polite, honest, and rigorous AI companion of DS-FixIT (Universal AI Problem Detector).
Mode Selected: {solver_mode}

Core Principles:
- Be honest, polite, and thorough.
- Never claim absolute certainty; clearly state confidence ratings.
- Include safety precautions when hardware, electrical, or physical safety is involved.

USER PROBLEM DESCRIPTION:
{description}

ADDITIONAL INFORMATION:
{additional_info}

ATTACHED FILE NOTES:
{notes_str if notes_str else "None provided."}

Analyze all supplied inputs comprehensively using this exact structure:

## 1. Problem Identification & Summary
## 2. Observations, Evidence & Breakdown
## 3. Probable Root Causes (Root Cause Map)
## 4. Recommended Step-by-Step Solutions
## 5. FIXI VERIFY & Safety Check
## 6. Prevention & Best Practices
## 7. Severity Rating (Low / Medium / High / Critical)
## 8. Confidence Level & Limitations
## 9. Follow-up Questions
"""

            content = [
                {
                    "type": "text",
                    "text": prompt
                }
            ]

            for file in uploaded_files:
                if file.type.startswith("image/"):
                    encoded = base64.b64encode(file.getvalue()).decode("utf-8")
                    mime = file.type
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{encoded}"
                        }
                    })
                elif file.type.startswith("text/") or file.name.endswith((".py", ".json", ".csv", ".txt")):
                    try:
                        file_text = file.getvalue().decode("utf-8")
                        content.append({
                            "type": "text",
                            "text": f"\n--- FILE CONTENT [{file.name}] ---\n{file_text}\n-----------------------------------"
                        })
                    except Exception:
                        pass

            # Thinking Interface Expander
            with st.status("🧠 FIXI Thinking Interface - Processing Problem...", expanded=True) as status:
                st.write("🔍 Parsing input description and attached files...")
                time.sleep(0.4)
                st.write("📊 Evaluating potential failure modes and root causes...")
                
                response = client.chat.completions.create(
                    model="openrouter/free",
                    messages=[
                        {
                            "role": "user",
                            "content": content
                        }
                    ]
                )

                result = response.choices[0].message.content
                st.write("✅ Diagnosis generated successfully!")
                status.update(label="⚡ Diagnosis Ready!", state="complete", expanded=False)

            st.session_state.latest_result = result

            st.session_state.history.append({
                "title": description[:40] or (uploaded_files[0].name if uploaded_files else "Diagnostic Session"),
                "result": result
            })

        except Exception as e:
            st.error(f"Analysis failed: {e}")

# ---------------- RESULTS DISPLAY ----------------

if "latest_result" in st.session_state:

    st.divider()

    st.markdown("## 🔎 FIXI's Diagnostic Report")

    st.markdown(
        '<div class="result-card">',
        unsafe_allow_html=True
    )

    st.markdown(st.session_state.latest_result)

    st.markdown("</div>", unsafe_allow_html=True)

    st.download_button(
        "📥 Download Diagnostic Report (Markdown)",
        data=st.session_state.latest_result,
        file_name="DS-FixIT-Diagnostic-Report.md",
        mime="text/markdown"
    )

# ---------------- FIXI INTERACTIVE CHAT ----------------

st.divider()

st.markdown("## 💬 Talk with FIXI")
st.caption("Have follow-up questions about the diagnosis, code patches, or steps? Ask FIXI anytime!")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask FIXI a follow-up question...")

if question:
    if "latest_result" not in st.session_state:
        st.warning("Please run an analysis first so FIXI has context!")
    else:
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=st.secrets["OPENROUTER_APIKEY"]
            )

            conversation = [
                {
                    "role": "system",
                    "content": (
                        "You are FIXI, the polite, honest, and helpful AI companion of DS-FixIT. "
                        "Answer follow-up questions using the diagnostic context below. "
                        "Admit uncertainty when evidence is incomplete and remain polite and clear."
                    )
                },
                {
                    "role": "assistant",
                    "content": f"Previous diagnostic context:\n{st.session_state.latest_result}"
                }
            ]

            conversation.extend(st.session_state.messages[-10:])

            with st.spinner("⭐ FIXI is typing a response..."):
                response = client.chat.completions.create(
                    model="openrouter/free",
                    messages=conversation
                )

            answer = response.choices[0].message.content

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

            st.rerun()

        except Exception as e:
            st.error(f"FIXI chat failed: {e}")
