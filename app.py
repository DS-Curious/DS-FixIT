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

/* Explicit Light Mode Input Styling for perfect visibility */
.stTextArea textarea, .stTextInput input {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
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
    st.caption("Universal AI Problem Detector • v3.9")

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

# ---------------- DARK MODE OVERRIDE (CRITICAL INPUT TEXT VISIBILITY FIX) ----------------

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
    /* Explicit Dark Mode Input Styling for 100% Text Visibility */
    .stTextArea textarea, .stTextInput input {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #009fff !important;
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
)

file_notes = {}
if uploaded_files:
    st.markdown("### 🗂️ Attached Evidence Context & Notes")
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
                placeholder="e.g. Error starts at line 45 or audio timestamp 0:15...",
                key=f"note_{file.name}"
            )
            if note:
                file_notes[file.name] = note

# ---------------- ANALYSIS ENGINE ----------------

if st.button(
    "🚀 ANALYSE WITH FIXI",
    type="primary",
    use_container_width=True
):

    if not description.strip() and not uploaded_files:
        st.warning("Please describe the problem or upload evidence (image, audio, or file).")

    else:
        st.session_state.fixi_mood = "💻 Processing & Analyzing..."
        try:
            api_key = st.secrets["OPENROUTER_APIKEY"]

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )

            notes_str = "\n".join([f"- {fname}: {note}" for fname, note in file_notes.items()])

            prompt = f"""
You are FIXI, the polite, honest, and rigorous neural AI companion of DS-FixIT (Universal AI Problem Detector).
Selected Solver Mode: {solver_mode}

Core Guidelines:
- Be honest, polite, and thorough.
- Never claim absolute certainty; clearly state confidence ratings.
- Include safety precautions when hardware, electrical, medical, or physical safety is involved.

USER PROBLEM DESCRIPTION:
{description}

ADDITIONAL INFORMATION:
{additional_info}

ATTACHED FILE NOTES:
{notes_str if notes_str else "None provided."}

Analyze all supplied inputs comprehensively using this exact multi-perspective structure:

## 1. Problem Identification & Summary
## 2. Observations, Evidence & Multi-Modal Breakdown
## 3. Root Cause Map (Underlying triggers & cascading failures)
## 4. Multi-Perspective Analysis (Security, Performance, & Practical viewpoints)
## 5. Recommended Step-by-Step Solutions / Patches
## 6. FIXI VERIFY & Safety Check
## 7. Prevention & Best Practices
## 8. Severity Rating & Confidence Limitations
## 9. Follow-up Questions for the User
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
                st.write("🗺️ Constructing Root Cause Map & Multi-Perspective Viewpoints...")
                
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
                st.write("✅ Comprehensive diagnosis generated successfully!")
                status.update(label="🚀 Diagnosis Ready!", state="complete", expanded=False)

            st.session_state.latest_result = result
            st.session_state.fixi_mood = "🎯 Ready for Next Task"

            st.session_state.history.append({
                "title": description[:40] or (uploaded_files[0].name if uploaded_files else "Diagnostic Session"),
                "result": result
            })

        except Exception as e:
            st.session_state.fixi_mood = "⚠️ Error Encountered"
            st.error(f"Analysis failed: {e}")

# ---------------- RESULTS DISPLAY & HIGHLIGHTS ----------------

if "latest_result" in st.session_state:

    st.divider()

    st.markdown("## 🔍 FIXI's Diagnostic Report")

    result_text = st.session_state.latest_result
    
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    
    # Executive Highlights Banner
    st.markdown("### ⚡ Executive Diagnostic Highlights")
    c_col1, c_col2, c_col3 = st.columns(3)
    with c_col1:
        st.markdown("**🛡️ Risk Level:**")
        st.info("Medium / Evaluated")
    with c_col2:
        st.markdown("**🎯 Primary Probable Cause:**")
        st.warning("Review Root Cause Section below")
    with c_col3:
        st.markdown("**💡 Key Solution:**")
        st.success("Check Recommended Steps below")

    st.markdown("---")

    # Full Report Display
    st.markdown(result_text)

    st.markdown("</div>", unsafe_allow_html=True)

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            "📥 Download Report (Markdown)",
            data=st.session_state.latest_result,
            file_name="DS-FixIT-Diagnostic-Report.md",
            mime="text/markdown"
        )
    with col_dl2:
        pdf_html_content = f"""
        <html>
        <head><title>DS-FixIT Diagnostic Report</title></head>
        <body style="font-family: Arial, sans-serif; padding: 30px; color: #333;">
            <h1 style="color: #009fff;">DS-FixIT 🚀 Diagnostic Report</h1>
            <p><b>Mode:</b> {solver_mode}</p>
            <hr/>
            <div>{st.session_state.latest_result.replace(chr(10), '<br>')}</div>
            <hr/>
            <p style="font-size: 11px; color: #777;">Generated by FIXI • DS-FixIT © 2026</p>
        </body>
        </html>
        """
        st.download_button(
            "📄 Download Official PDF Report",
            data=pdf_html_content,
            file_name="DS-FixIT-Diagnostic-Report.html",
            mime="text/html",
            help="Downloads the official formatted report (can be printed to PDF instantly in any browser)."
        )

# ---------------- FIXI INTERACTIVE CHAT ----------------

st.divider()

st.markdown("## 💬 Talk with FIXI")
st.caption("Have follow-up questions about the diagnosis, code patches, or root causes? Ask FIXI anytime!")

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
                        "You are FIXI, the polite, honest, and helpful neural AI companion of DS-FixIT. "
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

            with st.spinner("🚀 FIXI is typing a response..."):
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
