
import streamlit as st
import requests
import base64
import mimetypes
import time
import re
from openai import OpenAI

# ==========================================
# DS-FIXIT | UNIVERSAL AI v4.0
# ==========================================

st.set_page_config(
    page_title="DS-FixIT | Universal AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# DESIGN SYSTEM
# ==========================================

st.markdown("""
<style>

/* MAIN APP */

.stApp {
    background: linear-gradient(
        135deg,
        var(--background-color),
        var(--secondary-background-color)
    );
}

/* HEADER */

.main-title {
    font-size: 48px;
    font-weight: 900;
    background: linear-gradient(
        90deg,
        #009fff,
        #ec2f4b
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 1px;
}

.subtitle {
    font-size: 18px;
    font-weight: 600;
}

/* BUTTONS */

.stButton > button,
.stDownloadButton > button {
    border-radius: 12px;
    font-weight: 700;
    transition: all 0.2s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-2px);
}

/* RESULT CARDS */

.result-card {
    padding: 24px;
    border-radius: 18px;
    border: 1px solid var(--border-color);
    background: var(--secondary-background-color);
    margin: 14px 0;
}

/* IMPORTANT DIAGNOSTIC HIGHLIGHTS */

.diagnostic-risk {
    border-left: 6px solid #ef4444;
    background: rgba(239, 68, 68, 0.10);
    padding: 16px;
    border-radius: 10px;
    margin: 14px 0;
}

.diagnostic-cause {
    border-left: 6px solid #f59e0b;
    background: rgba(245, 158, 11, 0.10);
    padding: 16px;
    border-radius: 10px;
    margin: 14px 0;
}

.diagnostic-solution {
    border-left: 6px solid #22c55e;
    background: rgba(34, 197, 94, 0.10);
    padding: 16px;
    border-radius: 10px;
    margin: 14px 0;
}

.diagnostic-verify {
    border-left: 6px solid #009fff;
    background: rgba(0, 159, 255, 0.10);
    padding: 16px;
    border-radius: 10px;
    margin: 14px 0;
}

/* REPORT TYPOGRAPHY */

.report-content h2 {
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-color);
    margin-top: 28px;
}

.report-content h3 {
    margin-top: 20px;
}

.report-content li {
    margin-bottom: 8px;
    line-height: 1.7;
}

.report-content p {
    line-height: 1.75;
}

.report-content pre {
    border-radius: 12px;
    padding: 16px;
    overflow-x: auto;
}

/* FIXI BADGES */

.tech-badge {
    display: inline-block;
    background: #009fff;
    color: white !important;
    padding: 4px 9px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: bold;
    margin: 2px;
}

/* UPLOADER */

[data-testid="stFileUploader"] section {
    border-radius: 12px;
    border: 1px dashed #009fff;
}

/* CHAT INPUT */

[data-testid="stChatInput"] {
    border-radius: 12px;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    border-right: 1px solid var(--border-color);
}

/* GENERAL SPACING */

div[data-testid="stVerticalBlock"] {
    gap: 0.8rem;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SESSION STATE
# ==========================================

if "history" not in st.session_state:
    st.session_state.history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "fixi_mood" not in st.session_state:
    st.session_state.fixi_mood = "🚀 Online & Ready"

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("## 🚀 DS-FixIT")

    st.caption("Universal AI Problem Detector • v4.0")

    st.divider()

    st.markdown("### 🤖 FIXI Companion")

    st.markdown(f"""
    <div style="
        background: rgba(0,159,255,0.10);
        padding: 18px;
        border-radius: 14px;
        text-align: center;
        border: 1px solid #009fff;
    ">
        <div style="font-size: 42px;">🔮</div>

        <div style="
            color: #009fff;
            font-size: 21px;
            font-weight: 900;
        ">FIXI</div>

        <div style="font-size: 12px;">
            Status: {st.session_state.fixi_mood}
        </div>

        <br>

        <span class="tech-badge">Honest</span>
        <span class="tech-badge">Polite</span>
        <span class="tech-badge">Multi-Perspective</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

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

    st.markdown("### 🧠 FIXI Memory Vault")

    search_query = st.text_input(
        "🔍 Search past sessions",
        placeholder="Search diagnostic history..."
    )

    if not st.session_state.history:

        st.caption("No history logged yet.")

    else:

        filtered_history = [
            item for item in st.session_state.history
            if search_query.lower() in item["title"].lower()
            or search_query.lower() in item["result"].lower()
        ] if search_query else st.session_state.history

        for i, item in enumerate(
            reversed(filtered_history[-10:])
        ):

            if st.button(
                f"📌 {item['title'][:28]}",
                key=f"history_{i}",
                use_container_width=True
            ):

                st.session_state.latest_result = item["result"]

                st.rerun()

    st.divider()

    with st.expander("ℹ️ About DS-FixIT & Creator"):

        st.write(
            "**DS-FixIT** is a universal multi-modal AI "
            "problem detector powered by advanced AI."
        )

        st.write("**Creator:** J.P. Dheepak Saianand")

        st.write("**Companion:** FIXI")

        st.caption(
            "DS-FixIT © 2026 • Built with Streamlit & OpenRouter"
        )


# ==========================================
# MAIN HEADER
# ==========================================

st.markdown(
    '<div class="main-title">DS-FixIT 🚀</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="subtitle">'
    f'Detect. Analyse. Fix. • Active Mode: {solver_mode}'
    f'</div>',
    unsafe_allow_html=True
)

st.write(
    "Your universal AI problem detector. Diagnose code, "
    "mathematics, hardware, plants, writing, data, sound "
    "and study problems with FIXI."
)

st.divider()

# ==========================================
# INPUT & EVIDENCE SECTION
# ==========================================

st.markdown("## 🚀 What's the problem today?")

col_desc, col_extra = st.columns(2)

with col_desc:
    description = st.text_area(
        "Describe your problem",
        placeholder="Explain what's happening or paste code, equations, errors...",
        height=150
    )

with col_extra:
    additional_info = st.text_area(
        "Additional Information (Optional Context)",
        placeholder="OS, device, environment, previous attempts, error logs...",
        height=150
    )


# ==========================================
# FILE UPLOAD
# ==========================================

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

    st.markdown("### 🗂️ Attached Evidence")

    for file in uploaded_files:

        c1, c2 = st.columns([1, 2])

        with c1:

            if file.type.startswith("image/"):
                st.image(
                    file,
                    caption=file.name,
                    width=160
                )
            else:
                st.write(
                    f"📁 **{file.name}** ({file.type or 'file'})"
                )

        with c2:

            note = st.text_input(
                f"Extra note for {file.name}",
                placeholder="Describe relevant details...",
                key=f"note_{file.name}"
            )

            if note:
                file_notes[file.name] = note


# ==========================================
# REPORT HIGHLIGHTING ENGINE
# ==========================================

def highlight_report(report):

    lines = report.splitlines()

    formatted = []

    for line in lines:

        clean = line.strip()
        lower = clean.lower()

        # RISK / SEVERITY

        if (
            "risk level" in lower
            or "severity rating" in lower
            or "severity:" in lower
            or "critical risk" in lower
            or "high risk" in lower
        ):

            formatted.append(
                '<div class="diagnostic-risk">'
                '<strong>🚨 RISK & SEVERITY</strong><br>'
                + clean +
                '</div>'
            )

        # ROOT CAUSE

        elif (
            "root cause" in lower
            or "underlying cause" in lower
            or "primary cause" in lower
            or "cause:" in lower
        ):

            formatted.append(
                '<div class="diagnostic-cause">'
                '<strong>🔎 ROOT CAUSE</strong><br>'
                + clean +
                '</div>'
            )

        # SOLUTIONS

        elif (
            "recommended solution" in lower
            or "recommended fix" in lower
            or "solution:" in lower
            or "step-by-step solutions" in lower
            or "recommended step" in lower
        ):

            formatted.append(
                '<div class="diagnostic-solution">'
                '<strong>🛠️ SOLUTION</strong><br>'
                + clean +
                '</div>'
            )

        # VERIFICATION / SAFETY

        elif (
            "fixi verify" in lower
            or "safety check" in lower
            or "verification:" in lower
        ):

            formatted.append(
                '<div class="diagnostic-verify">'
                '<strong>🛡️ FIXI VERIFY</strong><br>'
                + clean +
                '</div>'
            )

        else:

            formatted.append(line)

    return "\n".join(formatted)


# ==========================================
# ANALYSIS ENGINE
# ==========================================

if st.button(
    "🚀 ANALYSE WITH FIXI",
    type="primary",
    use_container_width=True
):

    if not description.strip() and not uploaded_files:

        st.warning(
            "Please describe the problem or upload evidence."
        )

    else:

        st.session_state.fixi_mood = (
            "💻 Processing & Analyzing..."
        )

        try:

            api_key = st.secrets["OPENROUTER_APIKEY"]

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )

            notes_str = "\n".join([
                f"- {fname}: {note}"
                for fname, note in file_notes.items()
            ])

            prompt = f"""
You are FIXI, the polite, honest, rigorous AI companion
of DS-FixIT Universal AI Problem Detector.

Selected Solver Mode: {solver_mode}

IMPORTANT REPORT FORMATTING RULES:

- Make the report easy to scan.
- Use concise headings and bullet points.
- Clearly identify the risk level.
- Explain the actual root cause separately from symptoms.
- Give practical, prioritized solutions.
- Highlight urgent warnings.
- Use clear language and avoid unnecessary repetition.
- Never invent evidence.
- State uncertainty and confidence honestly.
- Include safety precautions when hardware, electrical,
  medical, or physical safety is involved.

USER PROBLEM DESCRIPTION:
{description}

ADDITIONAL INFORMATION:
{additional_info}

ATTACHED FILE NOTES:
{notes_str if notes_str else "None provided."}

Produce the diagnostic report using this structure:

# 1. Problem Identification & Summary

Give a concise explanation of the problem.

# 2. Observations & Evidence

List the important observations and evidence.

# 3. Risk Level & Severity

Clearly state:
- Risk level: LOW / MEDIUM / HIGH / CRITICAL
- Severity rating
- Why this risk level applies
- Immediate precautions, if necessary

# 4. Root Cause Analysis

Identify:
- Primary root cause
- Contributing factors
- Symptoms versus actual causes
- Possible cascading failures

# 5. Multi-Perspective Analysis

Discuss:
- Security
- Performance
- Reliability
- Practical considerations

# 6. Recommended Solutions

Provide prioritized, numbered steps.

For each solution include:
- What to do
- Why it works
- Expected result
- Relevant warnings

# 7. FIXI VERIFY & Safety Check

Explain how to verify the solution.
Mention any remaining risks.

# 8. Prevention & Best Practices

Provide useful preventive recommendations.

# 9. Confidence & Limitations

State confidence and missing evidence.

# 10. Follow-up Questions

Ask only relevant questions that would improve diagnosis.
"""

            content = [
                {
                    "type": "text",
                    "text": prompt
                }
            ]

            # Process uploaded evidence

            for file in uploaded_files:

                if file.type.startswith("image/"):

                    encoded = base64.b64encode(
                        file.getvalue()
                    ).decode("utf-8")

                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": (
                                f"data:{file.type};base64,{encoded}"
                            )
                        }
                    })

                elif (
                    file.type.startswith("text/")
                    or file.name.endswith(
                        (".py", ".json", ".csv", ".txt")
                    )
                ):

                    try:

                        file_text = file.getvalue().decode(
                            "utf-8"
                        )

                        content.append({
                            "type": "text",
                            "text": (
                                f"\n--- FILE: {file.name} ---\n"
                                f"{file_text}\n"
                                "--------------------------"
                            )
                        })

                    except UnicodeDecodeError:

                        st.warning(
                            f"Could not decode {file.name} as UTF-8."
                        )

                elif file.name.lower().endswith(".pdf"):

                    st.warning(
                        f"{file.name}: PDF text extraction is not "
                        "implemented in this version."
                    )

                elif file.type.startswith("audio/"):

                    st.warning(
                        f"{file.name}: Audio transcription is not "
                        "implemented in this version."
                    )

            # FIXI THINKING INTERFACE

            with st.status(
                "🧠 FIXI is analyzing your problem...",
                expanded=True
            ) as status:

                st.write("🔍 Parsing description and evidence...")

                st.write("🗺️ Identifying possible root causes...")

                st.write("🛠️ Constructing prioritized solutions...")

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

                if not result:
                    raise ValueError(
                        "The AI returned an empty response."
                    )

                status.update(
                    label="🚀 FIXI Diagnosis Ready!",
                    state="complete",
                    expanded=False
                )

            # SAVE RESULT

            st.session_state.latest_result = result

            st.session_state.fixi_mood = (
                "🎯 Ready for Next Task"
            )

            st.session_state.messages = []

            st.session_state.history.append({
                "title": (
                    description[:40]
                    or (
                        uploaded_files[0].name
                        if uploaded_files
                        else "Diagnostic Session"
                    )
                ),
                "result": result
            })

            st.success(
                "FIXI successfully generated your diagnostic report!"
            )

        except Exception as e:

            st.session_state.fixi_mood = (
                "⚠️ Error Encountered"
            )

            st.error(
                f"Analysis failed: {e}"
            )


# ==========================================
# DIAGNOSTIC REPORT DISPLAY
# ==========================================

if st.session_state.latest_result:

    st.divider()

    st.markdown("## 🔍 FIXI Diagnostic Report")

    st.caption(
        "Your diagnosis, visually organized for easier reading."
    )

    formatted_report = highlight_report(
        st.session_state.latest_result
    )

    st.markdown(
        f'<div class="report-content">{formatted_report}</div>',
        unsafe_allow_html=True
    )

    # DOWNLOAD OPTIONS

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            "📥 Download Markdown Report",
            data=st.session_state.latest_result,
            file_name="DS-FixIT-Diagnostic-Report.md",
            mime="text/markdown",
            use_container_width=True
        )

    with col2:

        st.download_button(
            "📄 Download HTML Report",
            data=f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>DS-FixIT Diagnostic Report</title>
<style>
body {{
    font-family: Arial, sans-serif;
    max-width: 950px;
    margin: 40px auto;
    padding: 25px;
    color: #172033;
    line-height: 1.7;
}}
h1 {{ color: #009fff; }}
</style>
</head>
<body>
<h1>DS-FixIT 🚀 Diagnostic Report</h1>
<pre style="white-space:pre-wrap;font-family:inherit;">{
    st.session_state.latest_result
}</pre>
<hr>
<p>Generated by FIXI • DS-FixIT © 2026</p>
</body>
</html>
""",
            file_name="DS-FixIT-Diagnostic-Report.html",
            mime="text/html",
            use_container_width=True
        )

# ==========================================
# FIXI INTERACTIVE CHAT
# ==========================================

st.divider()

st.markdown("## 💬 Talk with FIXI")

st.caption(
    "Ask follow-up questions about your diagnosis, "
    "root causes, solutions, or recommended patches."
)


# ==========================================
# CHAT STYLING
# ==========================================

st.markdown("""
<style>

/* Chat messages */

[data-testid="stChatMessage"] {
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 12px;
    border: 1px solid var(--border-color);
}

/* Chat input */

[data-testid="stChatInput"] {
    background: var(--secondary-background-color) !important;
    border-radius: 12px !important;
}

[data-testid="stChatInput"] > div {
    background: var(--secondary-background-color) !important;
    border: 1px solid #009fff !important;
    border-radius: 12px !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] textarea {
    color: var(--text-color) !important;
    background: transparent !important;
    caret-color: #009fff !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    opacity: 0.7;
}

[data-testid="stChatInput"] > div:focus-within {
    border: 1px solid #009fff !important;
    box-shadow: 0 0 0 2px rgba(0,159,255,0.15) !important;
    outline: none !important;
}

[data-testid="stChatInput"] button {
    color: #009fff !important;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# DISPLAY CHAT HISTORY
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ==========================================
# FOLLOW-UP QUESTION INPUT
# ==========================================

question = st.chat_input(
    "Ask FIXI a follow-up question..."
)


# ==========================================
# PROCESS FOLLOW-UP
# ==========================================

if question:

    if not st.session_state.latest_result:

        st.warning(
            "🚀 Please run an analysis first so FIXI "
            "has a diagnostic report to reference."
        )

    else:

        # Save user message

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        # Display user message immediately

        with st.chat_message("user"):
            st.markdown(question)

        try:

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=st.secrets["OPENROUTER_APIKEY"]
            )

            # SYSTEM INSTRUCTIONS

            conversation = [
                {
                    "role": "system",
                    "content": """
You are FIXI, the intelligent AI companion of DS-FixIT.

Your personality:
- Polite
- Honest
- Friendly
- Technically rigorous
- Helpful
- Clear and concise

Your responsibilities:

1. Answer follow-up questions using the diagnostic report.
2. Explain technical concepts in understandable language.
3. Provide corrected code when requested.
4. Explain root causes rather than just symptoms.
5. Never invent evidence or claim certainty without support.
6. Highlight safety warnings when relevant.
7. Use Markdown headings, bullets, and code blocks.
8. Clearly distinguish confirmed facts from possibilities.

When the user asks for a solution:
- Give practical steps.
- Explain why each step works.
- Include verification instructions.
"""
                },

                {
                    "role": "assistant",
                    "content": (
                        "PREVIOUS DIAGNOSTIC REPORT:\n\n"
                        + st.session_state.latest_result
                    )
                }
            ]

            # Include recent conversation history

            conversation.extend(
                st.session_state.messages[-10:]
            )

            # AI RESPONSE

            with st.chat_message("assistant"):

                with st.spinner(
                    "🚀 FIXI is thinking..."
                ):

                    response = client.chat.completions.create(
                        model="openrouter/free",
                        messages=conversation
                    )

                    answer = (
                        response.choices[0].message.content
                    )

                    if not answer:
                        raise ValueError(
                            "FIXI returned an empty response."
                        )

                st.markdown(answer)

            # SAVE ASSISTANT RESPONSE

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

        except Exception as e:

            st.error(
                f"FIXI chat failed: {e}"
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    "I encountered an error while processing "
                    "your question. Please try again."
                )
            })


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        padding:18px;
        opacity:0.75;
    ">
        <div style="
            font-size:20px;
            font-weight:900;
            background:linear-gradient(90deg,#009fff,#ec2f4b);
            -webkit-background-clip:text;
            -webkit-text-fill-color:transparent;
        ">
            DS-FixIT 🚀
        </div>

        <p style="font-size:12px;">
            Detect. Analyse. Fix.
        </p>

        <p style="font-size:11px;">
            Powered by FIXI • © 2026
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
