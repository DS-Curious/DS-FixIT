import streamlit as st
import requests
import base64
import mimetypes
import time
from PIL import Image, ImageDraw, ImageOps
from openai import OpenAI

st.set_page_config(
    page_title="DS-FixIT | Universal AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CONFIG & STYLING (IRON MAN THEME & BRIGHT CARDS) ----------------

st.markdown("""
<style>
.stApp {
    background-color: var(--background-color);
    color: var(--text-color);
}

[data-testid="stSidebar"] {
    background-color: var(--secondary-background-color);
    border-right: 2px solid rgba(0, 159, 255, 0.2);
}

.main-title {
    font-size: 48px;
    font-weight: 900;
    background: linear-gradient(90deg, #009fff, #ec2f4b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 1px;
}

.subtitle {
    color: var(--text-color);
    opacity: 0.8;
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

/* Bright Structured Metric Boxes */
.metric-row {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
}

.box-risk-high {
    flex: 1;
    background: linear-gradient(135deg, #7f1d1d, #ef4444);
    color: white;
    padding: 16px;
    border-radius: 14px;
    text-align: center;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
}

.box-risk-med {
    flex: 1;
    background: linear-gradient(135deg, #78350f, #f59e0b);
    color: white;
    padding: 16px;
    border-radius: 14px;
    text-align: center;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
}

.box-risk-low {
    flex: 1;
    background: linear-gradient(135deg, #065f46, #10b981);
    color: white;
    padding: 16px;
    border-radius: 14px;
    text-align: center;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
}

.box-confidence {
    flex: 1;
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    color: white;
    padding: 16px;
    border-radius: 14px;
    text-align: center;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
}

.result-card {
    padding: 24px;
    border-radius: 18px;
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(0, 159, 255, 0.3);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
    color: var(--text-color);
}

.tech-badge {
    background: #009fff;
    color: white;
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: bold;
}

.fixi-box {
    background-color: var(--secondary-background-color);
    padding: 14px;
    border-radius: 12px;
    text-align: center;
    border: 1px solid #009fff;
    color: var(--text-color);
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------

if "history" not in st.session_state:
    st.session_state.history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "fixi_mood" not in st.session_state:
    st.session_state.fixi_mood = "🚀 Online & Ready"

# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("## 🚀 DS-FixIT")
    st.caption("Universal AI Problem Detector • v3.5")
    st.divider()

    st.markdown("### 🤖 FIXI Companion")
    st.markdown(f"""
    <div class="fixi-box">
        <span style="font-size: 38px;">🔮</span><br>
        <b style="color: #009fff; font-size: 18px;">FIXI</b><br>
        <span style="font-size: 12px; opacity: 0.8;"><i>Status: {st.session_state.fixi_mood}</i></span><br><br>
        <span class="tech-badge">Honest</span> 
        <span class="tech-badge">Polite</span> 
        <span class="tech-badge">Multi-Perspective</span>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
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
    search_query = st.text_input("🔍 Search past sessions", placeholder="Keyword...")

    if st.session_state.history:
        filtered_history = [
            item for item in st.session_state.history 
            if search_query.lower() in item["title"].lower() or search_query.lower() in item["result"].lower()
        ] if search_query else st.session_state.history

        for i, item in enumerate(reversed(filtered_history[-10:])):
            if st.button(f"📌 {item['title'][:25]}...", key=f"history_{i}", use_container_width=True):
                st.session_state.latest_result = item["result"]

# ---------------- HEADER ----------------

st.markdown('<div class="main-title">DS-FixIT 🚀</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Detect. Analyse. Fix. • Active Mode: ' + solver_mode + '</div>', unsafe_allow_html=True)
st.write("Instant multi-modal diagnosis with bright metrics and visual error highlighting.")
st.divider()

# ---------------- INPUT SECTION ----------------

st.markdown("## 🚀 What's the problem today?")
col_desc, col_extra = st.columns(2)

with col_desc:
    description = st.text_area("Describe your problem", placeholder="Explain issue or paste code/equations...", height=140)

with col_extra:
    additional_info = st.text_area("Additional Information (Optional Context)", placeholder="Environment, OS, error logs...", height=140)

uploaded_files = st.file_uploader(
    "📎 Upload Evidence (Images, Audio, PDF, Text, or Code Files)",
    type=["png", "jpg", "jpeg", "webp", "pdf", "txt", "csv", "py", "json", "mp3", "wav", "m4a"],
    accept_multiple_files=True
)

file_notes = {}
processed_images = []

if uploaded_files:
    st.markdown("### 🗂️ Attached Evidence & FIXI-Vision Analysis")
    for file in uploaded_files:
        c1, c2 = st.columns([1, 2])
        with c1:
            if file.type.startswith("image/"):
                # FIXI-Vision: Highlight image with targeting reticle overlay
                img = Image.open(file).convert("RGB")
                draw = ImageDraw.Draw(img)
                w, h = img.size
                # Draw high-tech Iron Man style red/gold warning bounding box / reticle
                draw.rectangle([w*0.1, h*0.1, w*0.9, h*0.9], outline="#ef4444", width=max(3, int(w*0.01))))
                draw.text((w*0.12, h*0.12), "FIXI-TARGET", fill="#ef4444")
                st.image(img, caption=f"Highlighted: {file.name}", width=220)
                processed_images.append((file.name, img))
            else:
                st.write(f"📁 **{file.name}** ({file.type or 'file'})")
        with c2:
            note = st.text_input(f"Note for {file.name}", placeholder="e.g. Error at line 45...", key=f"note_{file.name}")
            if note:
                file_notes[file.name] = note

# ---------------- ANALYSIS ENGINE ----------------

if st.button("🚀 ANALYSE WITH FIXI", type="primary", use_container_width=True):
    if not description.strip() and not uploaded_files:
        st.warning("Please describe the problem or upload evidence.")
    else:
        st.session_state.fixi_mood = "💻 Processing & Analyzing..."
        try:
            api_key = st.secrets["OPENROUTER_APIKEY"]
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

            notes_str = "\n".join([f"- {fname}: {note}" for fname, note in file_notes.items()])

            prompt = (
                "You are FIXI, the polite, honest, and rigorous AI companion of DS-FixIT.\n"
                f"Selected Solver Mode: {solver_mode}\n\n"
                "CRITICAL OUTPUT FORMAT:\
                You must begin your response with these exact structured tags on the very first lines:\n"
                "RISK_LEVEL: [High / Medium / Low]\n"
                "CONFIDENCE_SCORE: [e.g. 95%]\n\n"
                "CRITICAL MATH RULE: Always use LaTeX ($...$ or $$...$$) for equations, powers, and differentiation.\n\n"
                f"USER PROBLEM:\n{description}\n\nADDITIONAL INFO:\n{additional_info}\n\n"
                f"FILE NOTES:\n{notes_str if notes_str else 'None'}\n\n"
                "Provide sections:\n"
                "## 1. Quick Summary\n"
                "## 2. Root Cause\n"
                "## 3. Step-by-Step Solution\n"
                "## 4. Safety & Verification\n"
            )

            content = [{"type": "text", "text": prompt}]
            for file in uploaded_files:
                if file.type.startswith("image/"):
                    encoded = base64.b64encode(file.getvalue()).decode("utf-8")
                    content.append({"type": "image_url", "image_url": {"url": f"data:{file.type};base64,{encoded}"}})

            with st.status("🧠 FIXI Thinking Interface...", expanded=True) as status:
                st.write("🔍 Evaluating metrics and visual features...")
                response = client.chat.completions.create(model="openrouter/free", messages=[{"role": "user", "content": content}])
                result = response.choices[0].message.content
                status.update(label="🚀 Diagnosis Ready!", state="complete", expanded=False)

            st.session_state.latest_result = result
            st.session_state.fixi_mood = "🎯 Ready for Next Task"
            st.session_state.history.append({
                "title": description[:40] or (uploaded_files[0].name if uploaded_files else "Session"),
                "result": result
            })
        except Exception as e:
            st.session_state.fixi_mood = "⚠️ Error Encountered"
            st.error(f"Analysis failed: {e}")

# ---------------- RESULTS DISPLAY WITH BRIGHT BOXES ----------------

if "latest_result" in st.session_state and st.session_state.latest_result:
    st.divider()
    st.markdown("## 🔍 FIXI's Diagnostic Report")

    res_text = str(st.session_state.latest_result)
    
    # Extract Risk and Confidence dynamically
    risk_display = "MEDIUM"
    conf_display = "90%"
    
    for line in res_text.split('\n'):
        if "RISK_LEVEL:" in line:
            risk_display = line.replace("RISK_LEVEL:", "").strip().upper()
        if "CONFIDENCE_SCORE:" in line:
            conf_display = line.replace("CONFIDENCE_SCORE:", "").strip()

    # Determine risk box class
    risk_class = "box-risk-med"
    risk_symbol = "🟡 MEDIUM RISK"
    if "HIGH" in risk_display:
        risk_class = "box-risk-high"
        risk_symbol = "🔴 HIGH RISK"
    elif "LOW" in risk_display:
        risk_class = "box-risk-low"
        risk_symbol = "🟢 LOW RISK"

    # Render Bright Colored Boxes
    st.markdown(f"""
    <div class="metric-row">
        <div class="{risk_class}">{risk_symbol}</div>
        <div class="box-confidence">🎯 CONFIDENCE: {conf_display}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown(res_text)
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📥 Download Report (.md)", data=res_text, file_name="Report.md", mime="text/markdown")
    with c2:
        st.download_button("📄 Download HTML Report", data=f"<html><body>{res_text.replace(chr(10), '<br>')}</body></html>", file_name="Report.html", mime="text/html")

# ---------------- INTERACTIVE CHAT ----------------

st.divider()
st.markdown("## 💬 Talk with FIXI")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask FIXI a follow-up question...")
if question:
    if "latest_result" not in st.session_state:
        st.warning("Run an analysis first!")
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        try:
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=st.secrets["OPENROUTER_APIKEY"])
            conv = [{"role": "system", "content": "You are FIXI. Use LaTeX ($...$) for math equations. Be direct and concise."}]
            conv.extend(st.session_state.messages[-10:])
            res = client.chat.completions.create(model="openrouter/free", messages=conv)
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except Exception as e:
            st.error(f"Chat failed: {e}")
