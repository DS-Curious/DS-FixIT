import streamlit as st
import requests
import base64
import mimetypes
import time
import io
from PIL import Image, ImageDraw, ImageOps
from openai import OpenAI

st.set_page_config(
    page_title="DS-FixIT | Universal AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CONFIG & STYLING ----------------

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
    st.caption("Universal AI Problem Detector • v4.1")
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

    if not st.session_state.history:
        st.caption("No history logged yet.")
    else:
        filtered_history = [
            item for item in st.session_state.history 
            if search_query.lower() in item["title"].lower() or search_query.lower() in item["result"].lower()
        ] if search_query else st.session_state.history

        for i, item in enumerate(reversed(filtered_history[-10:])):
            if st.button(f"📌 {item['title'][:25]}...", key=f"history_{i}", use_container_width=True):
                st.session_state.latest_result = item["result"]

    st.divider()

    with st.expander("ℹ️ About DS-FixIT & Creator"):
        st.write("**DS-FixIT** is a universal multi-modal AI problem detector powered by advanced vision and reasoning.")
        st.write("**Creator:** J.P. Dheepak Saianand")
        st.write("**Companion:** FIXI")
        st.caption("DS-FixIT © 2026 • Built with Streamlit & OpenRouter")

# ---------------- HEADER ----------------

st.markdown('<div class="main-title">DS-FixIT 🚀</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Detect. Analyse. Fix. • Active Mode: ' + solver_mode + '</div>', unsafe_allow_html=True)
st.write("Instant multi-modal diagnosis with precision HUD reticle targeting.")
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
prepared_images = []

if uploaded_files:
    st.markdown("### 🗂️ Attached Evidence & Precision FIXI-Vision HUD")
    for file in uploaded_files:
        c1, c2 = st.columns([1, 2])
        with c1:
            if file.type.startswith("image/"):
                img = Image.open(file).convert("RGB")
                w, h = img.size
                
                # Default to Bottom Half / Fracture Zone if uploading bone X-rays
                focus_area = st.selectbox(
                    f"🎯 Target Focus Zone for {file.name}",
                    ["Bottom Half (Fracture / Error Zone)", "Center Focal Point", "Top Half", "Left Side", "Right Side"],
                    key=f"focus_{file.name}"
                )

                draw = ImageDraw.Draw(img)
                
                # Precise targeting box coordinates
                if "Bottom Half" in focus_area:
                    box = [w*0.2, h*0.45, w*0.85, h*0.9] # Snaps directly to lower leg fracture area
                elif "Top Half" in focus_area:
                    box = [w*0.2, h*0.05, w*0.8, h*0.5]
                elif "Left Side" in focus_area:
                    box = [w*0.05, h*0.2, w*0.5, h*0.8]
                elif "Right Side" in focus_area:
                    box = [w*0.5, h*0.2, w*0.95, h*0.8]
                else:
                    box = [w*0.3, h*0.3, w*0.7, h*0.7]

                # Draw high-tech Iron Man HUD targeting box & crosshairs
                draw.rectangle(box, outline="#ef4444", width=max(4, int(w*0.01)))
                
                cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
                draw.line([(cx - 20, cy), (cx + 20, cy)], fill="#ef4444", width=4)
                draw.line([(cx, cy - 20), (cx, cy + 20)], fill="#ef4444", width=4)
                
                draw.text((box[0] + 8, box[1] + 8), "FIXI-TARGET LOCK", fill="#ef4444")
                
                st.image(img, caption=f"Targeted: {file.name} ({focus_area})", width=240)
                prepared_images.append(img)
            else:
                st.write(f"📁 **{file.name}** ({file.type or 'file'})")
        with c2:
            note = st.text_input(f"Note for {file.name}", placeholder="e.g. Oblique fracture at distal tibia...", key=f"note_{file.name}")
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
                "CRITICAL TAG REQUIREMENTS:\n"
                "You MUST start your response with these exact lines:\n"
                "RISK_LEVEL: [High / Medium / Low]\n"
                "CONFIDENCE_SCORE: [e.g. 95%]\n\n"
                "CRITICAL FORMATTING GUIDELINES:\n"
                "- Keep explanations punchy and direct. Avoid long paragraphs.\n"
                "- Use bold markdown (**...**) exclusively on critical failure points, key root causes, and primary action items.\n"
                "- Use LaTeX ($...$ or $$...$$) for all math equations and formulas.\n"
                "- Analyze the exact area inside the red HUD box and crosshairs (marked as FIXI-TARGET LOCK) for fractures, defects, or errors.\n\n"
                f"USER PROBLEM:\n{description}\n\nADDITIONAL INFO:\n{additional_info}\n\n"
                f"FILE NOTES:\n{notes_str if notes_str else 'None'}\n\n"
                "Provide sections:\n"
                "## 1. Executive Summary\n"
                "## 2. Root Cause Analysis\n"
                "## 3. Actionable Solution / Steps\n"
                "## 4. Safety & Verification\n"
            )

            content = [{"type": "text", "text": prompt}]
            
            for img in prepared_images:
                buf = io.BytesIO()
                img.save(buf, format="JPEG")
                encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}
                })

            for file in uploaded_files:
                if not file.type.startswith("image/"):
                    if file.type.startswith("text/") or file.name.endswith((".py", ".json", ".csv", ".txt")):
                        try:
                            file_text = file.getvalue().decode("utf-8")
                            content.append({
                                "type": "text",
                                "text": f"\n--- FILE CONTENT [{file.name}] ---\n{file_text}\n-----------------------------------"
                            })
                        except Exception:
                            pass

            with st.status("🧠 FIXI Thinking Interface...", expanded=True) as status:
                st.write("🔍 Evaluating precision HUD target reticles...")
                response = client.chat.completions.create(model="openrouter/free", messages=[{"role": "user", "content": content}])
                result = response.choices[0].message.content
                status.update(label="🚀 Diagnosis Ready!", state="complete", expanded=False)

            st.session_state.latest_result = result
            st.session_state.fixi_mood = "🎯 Ready for Next Task"
            st.session_state.history.append({
                "title": description[:40] or (uploaded_files[0].name if uploaded_files else "Session"),
                "result": result
            })
            st.rerun()
        except Exception as e:
            st.session_state.fixi_mood = "⚠️ Error Encountered"
            st.error(f"Analysis failed: {e}")

# ---------------- RESULTS DISPLAY ----------------

if "latest_result" in st.session_state and st.session_state.latest_result:
    st.divider()
    st.markdown("## 🔍 FIXI's Diagnostic Report")

    res_text = str(st.session_state.latest_result)
    
    risk_display = "MEDIUM"
    conf_display = "90%"
    clean_report_lines = []
    
    for line in res_text.split('\n'):
        if "RISK_LEVEL:" in line:
            risk_display = line.replace("RISK_LEVEL:", "").strip().upper()
        elif "CONFIDENCE_SCORE:" in line:
            conf_display = line.replace("CONFIDENCE_SCORE:", "").strip()
        else:
            clean_report_lines.append(line)

    clean_report = "\n".join(clean_report_lines).strip()

    risk_class = "box-risk-med"
    risk_symbol = "🟡 MEDIUM RISK"
    if "HIGH" in risk_display:
        risk_class = "box-risk-high"
        risk_symbol = "🔴 HIGH RISK"
    elif "LOW" in risk_display:
        risk_class = "box-risk-low"
        risk_symbol = "🟢 LOW RISK"

    st.markdown(f"""
    <div class="metric-row">
        <div class="{risk_class}">{risk_symbol}</div>
        <div class="box-confidence">🎯 CONFIDENCE: {conf_display}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(clean_report)

    st.write("")

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📥 Download Report (.md)", data=clean_report, file_name="Report.md", mime="text/markdown", key="dl_md_rep")
    with c2:
        pdf_html_content = f"""
        <html>
        <head><title>DS-FixIT Diagnostic Report</title></head>
        <body style="font-family: Arial, sans-serif; padding: 30px; color: #333;">
            <h1 style="color: #009fff;">DS-FixIT 🚀 Diagnostic Report</h1>
            <p><b>Mode:</b> {solver_mode}</p>
            <hr/>
            <div>{clean_report.replace(chr(10), '<br>')}</div>
            <hr/>
            <p style="font-size: 11px; color: #777;">Generated by FIXI • DS-FixIT © 2026</p>
        </body>
        </html>
        """
        st.download_button("📄 Download Official PDF Report", data=pdf_html_content, file_name="Report.html", mime="text/html", key="dl_html_rep")

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
            conv = [{"role": "system", "content": "You are FIXI. Use bold markdown for key takeaways. Be direct and concise."}]
            conv.extend(st.session_state.messages[-10:])
            res = client.chat.completions.create(model="openrouter/free", messages=conv)
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except Exception as e:
            st.error(f"Chat failed: {e}")
