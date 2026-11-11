
import streamlit as st
import base64
import time
import html
from openai import OpenAI

# ==========================================
# DS-FIXIT | UNIVERSAL AI v4.1
# ==========================================

st.set_page_config(
    page_title="DS-FixIT | Universal AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# SESSION STATE
# ==========================================

defaults = {
    "history": [],
    "messages": [],
    "dark_mode": False,
    "fixi_mood": "🚀 Online & Ready",
    "latest_result": None,
    "latest_mode": "General Problem Solver"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================
# THEME COLORS
# ==========================================

if st.session_state.dark_mode:
    BG = "#090d16"
    PANEL = "#172338"
    TEXT = "#f1f5f9"
    MUTED = "#a8b5c7"
    BORDER = "#334155"
    INPUT = "#1e293b"
else:
    BG = "#f0f8ff"
    PANEL = "#ffffff"
    TEXT = "#172033"
    MUTED = "#64748b"
    BORDER = "#cbdff0"
    INPUT = "#ffffff"


# ==========================================
# COMPLETE THEME STYLING
# ==========================================

st.markdown(f"""
<style>

/* MAIN APPLICATION */

.stApp {{
    background: {BG} !important;
    color: {TEXT} !important;
}}

[data-testid="stHeader"] {{
    background: transparent !important;
}}

[data-testid="stSidebar"] {{
    background: {PANEL} !important;
    border-right: 1px solid {BORDER} !important;
}}

/* TEXT */

html, body, p, label, li,
h1, h2, h3, h4, h5, h6 {{
    color: {TEXT};
}}

.stCaption, small {{
    color: {MUTED} !important;
}}

/* MAIN TITLE */

.main-title {{
    font-size: 46px;
    font-weight: 900;
    background: linear-gradient(90deg,#009fff,#ec2f4b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 1px;
}}

.subtitle {{
    font-size: 18px;
    font-weight: 600;
    color: {MUTED} !important;
}}

/* INPUTS */

.stTextInput input,
.stTextArea textarea,
[data-baseweb="select"] > div {{
    background: {INPUT} !important;
    color: {TEXT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
}}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
    color: {MUTED} !important;
    opacity: 1 !important;
}}

/* BUTTONS */

.stButton > button,
.stDownloadButton > button {{
    border-radius: 11px !important;
    font-weight: 700 !important;
    border: 1px solid #009fff !important;
    transition: 0.2s ease !important;
}}

.stButton > button:hover,
.stDownloadButton > button:hover {{
    border-color: #ec2f4b !important;
    transform: translateY(-2px);
}}

/* UPLOADER */

[data-testid="stFileUploader"] section {{
    background: {PANEL} !important;
    border: 1px dashed #009fff !important;
    border-radius: 12px !important;
}}

[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] section * {{
    color: {TEXT} !important;
}}

[data-testid="stFileUploader"] section button {{
    background: #009fff !important;
    color: white !important;
}}

/* EXPANDERS */

[data-testid="stExpander"] {{
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
}}

/* CHAT */

[data-testid="stChatMessage"] {{
    background: {PANEL} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 13px !important;
    padding: 12px !important;
}}

[data-testid="stChatInput"] {{
    background: transparent !important;
}}

[data-testid="stChatInput"] > div {{
    background: {INPUT} !important;
    border: 1px solid #009fff !important;
    border-radius: 12px !important;
    box-shadow: none !important;
}}

[data-testid="stChatInput"] textarea {{
    background: transparent !important;
    color: {TEXT} !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    caret-color: #009fff !important;
}}

[data-testid="stChatInput"] textarea::placeholder {{
    color: {MUTED} !important;
    opacity: 1 !important;
}}

[data-testid="stChatInput"] > div:focus-within {{
    border: 1px solid #009fff !important;
    box-shadow: 0 0 0 2px rgba(0,159,255,0.15) !important;
}}

[data-testid="stChatInput"] button {{
    color: #009fff !important;
}}

/* REPORT PANEL */

.result-card {{
    background: {PANEL};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 22px;
    margin: 12px 0;
}}

/* REPORT HIGHLIGHTS */

.report-highlight {{
    padding: 15px 18px;
    border-radius: 10px;
    margin: 14px 0;
    color: {TEXT};
}}

.risk-highlight {{
    background: rgba(239,68,68,0.12);
    border-left: 5px solid #ef4444;
}}

.cause-highlight {{
    background: rgba(245,158,11,0.12);
    border-left: 5px solid #f59e0b;
}}

.solution-highlight {{
    background: rgba(34,197,94,0.12);
    border-left: 5px solid #22c55e;
}}

.verify-highlight {{
    background: rgba(0,159,255,0.12);
    border-left: 5px solid #009fff;
}}

.report-content h1,
.report-content h2 {{
    border-bottom: 1px solid {BORDER};
    padding-bottom: 9px;
    margin-top: 26px;
}}

.report-content p,
.report-content li {{
    line-height: 1.75;
}}

.report-content pre {{
    background: {INPUT};
    border: 1px solid {BORDER};
    padding: 14px;
    border-radius: 10px;
    overflow-x: auto;
}}

.tech-badge {{
    display: inline-block;
    background: #009fff;
    color: white !important;
    border-radius: 6px;
    padding: 4px 9px;
    font-size: 11px;
    font-weight: bold;
}}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("## 🚀 DS-FixIT")
    st.caption("Universal AI Problem Detector • v4.1")

    st.divider()

    st.toggle(
        "🌙 Dark mode",
        key="dark_mode"
    )

    st.divider()

    # Native Streamlit elements for FIXI logo.
    # No custom HTML or SVG that can display as source code.

    st.markdown("### 🤖 FIXI Companion")

    st.markdown(
        "<div style='text-align:center;font-size:54px;'>🔮</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div style='text-align:center;color:#009fff;"
        "font-size:24px;font-weight:900;'>FIXI</div>",
        unsafe_allow_html=True
    )

    st.caption(
        f"Status: {st.session_state.fixi_mood}"
    )

    st.markdown(
        '<span class="tech-badge">Honest</span> '
        '<span class="tech-badge">Polite</span> '
        '<span class="tech-badge">Multi-Perspective</span>',
        unsafe_allow_html=True
    )

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

    st.session_state.latest_mode = solver_mode

    st.divider()

    st.markdown("### 🧠 FIXI Memory Vault")

    search_query = st.text_input(
        "🔍 Search past sessions",
        placeholder="Search keywords..."
    )

    if not st.session_state.history:

        st.caption("No history logged yet.")

    else:

        filtered_history = [
            item for item in st.session_state.history
            if search_query.lower() in item["title"].lower()
            or search_query.lower() in item["result"].lower()
        ]

        if not search_query:
            filtered_history = st.session_state.history

        for i, item in enumerate(
            reversed(filtered_history[-10:])
        ):

            if st.button(
                f"📌 {item['title'][:28]}",
                key=f"history_{i}",
                use_container_width=True
            ):

                st.session_state.latest_result = item["result"]
                st.session_state.latest_mode = item["mode"]
                st.session_state.messages = []
                st.rerun()

    st.divider()

    with st.expander("ℹ️ About DS-FixIT"):

        st.write(
            "DS-FixIT is a universal AI problem detector "
            "powered by AI reasoning and multimodal analysis."
        )

        st.write("**Creator:** J.P. Dheepak Saianand")
        st.write("**Companion:** FIXI")

        st.caption("DS-FixIT © 2026")


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
    "Detect code errors, mathematical problems, study "
    "queries, hardware faults, plant diseases, data issues, "
    "sound anomalies, and writing problems with FIXI."
)

st.divider()


# ==========================================
# PROBLEM INPUT
# ==========================================

st.markdown("## 🚀 What's the problem today?")

col_desc, col_extra = st.columns(2)

with col_desc:

    description = st.text_area(
        "Describe your problem",
        placeholder=(
            "Explain what's happening or paste code, "
            "equations, or error messages..."
        ),
        height=150,
        key="problem_description"
    )

with col_extra:

    additional_info = st.text_area(
        "Additional Information (Optional Context)",
        placeholder=(
            "OS, device, environmental factors, "
            "previous attempts, or error logs..."
        ),
        height=150,
        key="additional_information"
    )


# ==========================================
# EVIDENCE UPLOAD
# ==========================================

uploaded_files = st.file_uploader(
    "📎 Upload Evidence",
    type=[
        "png", "jpg", "jpeg", "webp",
        "pdf", "txt", "csv", "py", "json",
        "mp3", "wav", "m4a"
    ],
    accept_multiple_files=True,
    key="evidence_upload"
)

file_notes = {}

if uploaded_files:

    st.markdown("### 🗂️ Attached Evidence")

    for file in uploaded_files:

        col1, col2 = st.columns([1, 2])

        with col1:

            if file.type.startswith("image/"):

                st.image(
                    file,
                    caption=file.name,
                    width=160
                )

            else:

                st.write(
                    f"📁 **{file.name}**"
                )

                st.caption(
                    file.type or "Unknown file type"
                )

        with col2:

            note = st.text_input(
                f"Extra note for {file.name}",
                placeholder="Describe important details...",
                key=f"file_note_{file.name}"
            )

            if note:
                file_notes[file.name] = note

# ==========================================
# REPORT FORMATTER
# ==========================================

def render_diagnostic_report(report):

    """
    Safely renders FIXI's Markdown report.
    Important sections receive visual highlighting.
    """

    lines = report.splitlines()

    output = []
    current_block = []
    current_type = None

    def flush_block():

        nonlocal current_block, current_type

        if not current_block:
            return

        block_text = "\n".join(current_block)

        safe_text = html.escape(block_text)

        if current_type == "risk":

            output.append(
                '<div class="report-highlight risk-highlight">'
                '<strong>🚨 RISK & SEVERITY</strong>'
                f'<pre style="white-space:pre-wrap;'
                f'font-family:inherit;border:0;'
                f'background:transparent;">{safe_text}</pre>'
                '</div>'
            )

        elif current_type == "cause":

            output.append(
                '<div class="report-highlight cause-highlight">'
                '<strong>🔎 ROOT CAUSE</strong>'
                f'<pre style="white-space:pre-wrap;'
                f'font-family:inherit;border:0;'
                f'background:transparent;">{safe_text}</pre>'
                '</div>'
            )

        elif current_type == "solution":

            output.append(
                '<div class="report-highlight solution-highlight">'
                '<strong>🛠️ RECOMMENDED SOLUTION</strong>'
                f'<pre style="white-space:pre-wrap;'
                f'font-family:inherit;border:0;'
                f'background:transparent;">{safe_text}</pre>'
                '</div>'
            )

        elif current_type == "verify":

            output.append(
                '<div class="report-highlight verify-highlight">'
                '<strong>🛡️ FIXI VERIFICATION</strong>'
                f'<pre style="white-space:pre-wrap;'
                f'font-family:inherit;border:0;'
                f'background:transparent;">{safe_text}</pre>'
                '</div>'
            )

        else:

            output.append(
                f'<pre style="white-space:pre-wrap;'
                f'font-family:inherit;">{safe_text}</pre>'
            )

        current_block = []
        current_type = None

    for line in lines:

        lower = line.strip().lower()

        # Detect important sections

        if any(term in lower for term in [
            "risk level",
            "severity rating",
            "risk & severity",
            "critical risk",
            "high risk"
        ]):

            flush_block()
            current_type = "risk"

        elif any(term in lower for term in [
            "root cause",
            "primary cause",
            "underlying cause",
            "cause analysis"
        ]):

            flush_block()
            current_type = "cause"

        elif any(term in lower for term in [
            "recommended solution",
            "recommended solutions",
            "step-by-step solutions",
            "recommended fixes",
            "solution steps"
        ]):

            flush_block()
            current_type = "solution"

        elif any(term in lower for term in [
            "fixi verify",
            "verification",
            "safety check"
        ]):

            flush_block()
            current_type = "verify"

        # A new numbered heading ends the previous section

        elif (
            line.strip().startswith("#")
            and current_type is not None
            and any(char.isdigit() for char in line[:6])
        ):

            flush_block()

        current_block.append(line)

    flush_block()

    return "\n".join(output)


# ==========================================
# ANALYSIS ENGINE
# ==========================================

st.divider()

if st.button(
    "🚀 ANALYSE WITH FIXI",
    type="primary",
    use_container_width=True
):

    if not description.strip() and not uploaded_files:

        st.warning(
            "Please describe your problem or upload evidence."
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

            notes_str = "\n".join(
                f"- {name}: {note}"
                for name, note in file_notes.items()
            )

            prompt = f"""
You are FIXI, the intelligent and rigorous AI
companion of DS-FixIT Universal AI Problem Detector.

SELECTED SOLVER MODE:
{solver_mode}

PERSONALITY:
- Honest
- Polite
- Helpful
- Technically rigorous
- Clear and practical

IMPORTANT INSTRUCTIONS:

1. Analyze all supplied information carefully.
2. Never invent observations or evidence.
3. Distinguish symptoms from actual causes.
4. Give a clear risk classification.
5. Prioritize solutions by importance.
6. Explain why each recommended solution works.
7. Include appropriate safety precautions.
8. Clearly state uncertainty and confidence.
9. Do not claim that an action has been verified
   unless actual verification evidence exists.
10. Adapt your analysis to the selected solver mode.

USER PROBLEM:
{description}

ADDITIONAL CONTEXT:
{additional_info}

ATTACHED FILE NOTES:
{notes_str if notes_str else "None provided."}

GENERATE THE REPORT USING THIS STRUCTURE:

# 1. Problem Identification & Summary

Provide a short, clear explanation of the problem.

# 2. Observations & Evidence

List the important findings from the supplied evidence.

# 3. Risk Level & Severity

Include:

- Risk Level: LOW / MEDIUM / HIGH / CRITICAL
- Severity rating
- Explanation of the risk
- Immediate precautions if needed

# 4. Root Cause Analysis

Include:

- Primary root cause
- Contributing factors
- Symptoms versus actual causes
- Possible cascading failures

# 5. Multi-Perspective Analysis

Consider:

- Security
- Performance
- Reliability
- Practical impact

# 6. Recommended Solutions

Provide prioritized numbered solutions.

For each solution explain:

- What needs to be done
- Why it should work
- Expected result
- Any relevant warnings

# 7. FIXI Verify & Safety Check

Explain how the user can verify the proposed solution.
Identify any remaining uncertainty.

# 8. Prevention & Best Practices

Give practical prevention recommendations.

# 9. Confidence & Limitations

State confidence level and missing information.

# 10. Follow-up Questions

Ask relevant questions only when necessary.

FORMATTING:

Use readable Markdown.
Use short paragraphs.
Use bullets and numbered steps.
Make important warnings noticeable.
Avoid excessively long explanations.
"""

            content = [
                {
                    "type": "text",
                    "text": prompt
                }
            ]

            # ==================================
            # PROCESS EVIDENCE
            # ==================================

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
                    file.name.lower().endswith(
                        (".txt", ".py", ".json", ".csv")
                    )
                    or file.type.startswith("text/")
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
                            f"Unable to read {file.name} as UTF-8."
                        )

                elif file.name.lower().endswith(".pdf"):

                    st.warning(
                        f"{file.name}: PDF extraction requires "
                        "a separate PDF processing library."
                    )

                elif file.type.startswith("audio/"):

                    st.warning(
                        f"{file.name}: Audio transcription "
                        "requires a transcription service."
                    )

            # ==================================
            # THINKING INTERFACE
            # ==================================

            with st.status(
                "🧠 FIXI is analyzing your problem...",
                expanded=True
            ) as status:

                st.write("🔍 Examining problem description...")

                st.write("📎 Processing supported evidence...")

                st.write("🗺️ Mapping potential root causes...")

                st.write("🛠️ Preparing prioritized solutions...")

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

            # ==================================
            # SAVE DIAGNOSTIC
            # ==================================

            st.session_state.latest_result = result

            st.session_state.latest_mode = solver_mode

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
                "result": result,
                "mode": solver_mode
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
        f"Analysis Mode: {st.session_state.latest_mode}"
    )

    st.markdown(
        '<div class="result-card">',
        unsafe_allow_html=True
    )

    # Render highlighted report

    formatted_report = render_diagnostic_report(
        st.session_state.latest_result
    )

    st.markdown(
        f'<div class="report-content">'
        f'{formatted_report}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # ==================================
    # DOWNLOAD REPORTS
    # ==================================

    st.divider()

    st.markdown("### 📥 Export Diagnostic Report")

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            "📥 Download Markdown",
            data=st.session_state.latest_result,
            file_name="DS-FixIT-Diagnostic-Report.md",
            mime="text/markdown",
            use_container_width=True
        )

    with col2:

        report_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>DS-FixIT Diagnostic Report</title>
<style>
body {{
    font-family: Arial, sans-serif;
    max-width: 900px;
    margin: 40px auto;
    padding: 25px;
    color: #172033;
    line-height: 1.7;
}}
h1 {{ color: #009fff; }}
pre {{
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}}
</style>
</head>
<body>
<h1>DS-FixIT 🚀 Diagnostic Report</h1>
<p><strong>Mode:</strong> {html.escape(st.session_state.latest_mode)}</p>
<hr>
<pre>{html.escape(st.session_state.latest_result)}</pre>
<hr>
<p>Generated by FIXI • DS-FixIT © 2026</p>
</body>
</html>
"""

        st.download_button(
            "📄 Download HTML Report",
            data=report_html,
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
# CHAT HISTORY DISPLAY
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ==========================================
# FOLLOW-UP QUESTION INPUT
# ==========================================

question = st.chat_input(
    "Ask FIXI a follow-up question...",
    key="fixi_chat_input"
)


# ==========================================
# FOLLOW-UP PROCESSING
# ==========================================

if question:

    if not st.session_state.latest_result:

        st.warning(
            "🚀 Please run an analysis first so FIXI "
            "has diagnostic context."
        )

    else:

        # Save user question

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        try:

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=st.secrets["OPENROUTER_APIKEY"]
            )

            # System instructions

            conversation = [
                {
                    "role": "system",
                    "content": f"""
You are FIXI, the AI companion of DS-FixIT.

Your personality:
- Honest
- Polite
- Friendly
- Technically rigorous
- Helpful
- Clear and understandable

CURRENT SOLVER MODE:
{st.session_state.latest_mode}

PREVIOUS DIAGNOSTIC REPORT:
{st.session_state.latest_result}

YOUR RESPONSIBILITIES:

1. Answer questions using the diagnostic report.
2. Explain root causes clearly.
3. Provide practical solutions.
4. Provide corrected code when requested.
5. Explain technical concepts in simple language.
6. Never invent evidence.
7. Admit uncertainty when information is incomplete.
8. Include relevant safety precautions.
9. Use readable Markdown.
10. Keep answers focused on the user's question.

When suggesting a solution, explain:
- What to do
- Why it works
- How to verify it
"""
                }
            ]

            # Include recent conversation history

            conversation.extend(
                st.session_state.messages[-10:]
            )

            # Generate response

            with st.spinner("🚀 FIXI is thinking..."):

                response = client.chat.completions.create(
                    model="openrouter/free",
                    messages=conversation
                )

                answer = response.choices[0].message.content

                if not answer:

                    raise ValueError(
                        "FIXI returned an empty response."
                    )

            # Save answer

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

            st.rerun()

        except Exception as e:

            st.error(
                f"FIXI chat failed: {e}"
            )

            # Remove the unanswered user message so
            # the conversation does not become misleading.

            if (
                st.session_state.messages
                and st.session_state.messages[-1]["role"] == "user"
            ):

                st.session_state.messages.pop()


# ==========================================
# CHAT RESET
# ==========================================

if st.session_state.messages:

    if st.button(
        "🗑️ Clear FIXI Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ==========================================
# FINAL FOOTER
# ==========================================

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        padding:25px 10px;
    ">

        <div style="
            font-size:30px;
            font-weight:900;
            background:linear-gradient(90deg,#009fff,#ec2f4b);
            -webkit-background-clip:text;
            -webkit-text-fill-color:transparent;
        ">
            DS-FixIT 🚀
        </div>

        <div style="
            font-size:14px;
            margin-top:8px;
        ">
            Detect. Analyse. Fix.
        </div>

        <div style="
            font-size:12px;
            opacity:0.7;
            margin-top:12px;
        ">
            Powered by FIXI • © 2026
        </div>

    </div>
    """,
    unsafe_allow_html=True
)
