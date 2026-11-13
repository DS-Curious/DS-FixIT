import streamlit as st
import sqlite3
import hashlib
import json
import base64
import time
import io
from PIL import Image
from openai import OpenAI

st.set_page_config(
    page_title="DS-FixIT | Universal AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- DATABASE & AUTH ENGINE ----------------

DB_FILE = "ds_fixit_vault.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT,
            description TEXT,
            result TEXT,
            images_json TEXT,
            messages_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username.strip(), hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username.strip(),))
    row = c.fetchone()
    conn.close()
    return bool(row and row[0] == hash_password(password))

def encode_images_to_b64(pil_images: list) -> list:
    encoded_list = []
    for img in pil_images:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        encoded_list.append(base64.b64encode(buf.getvalue()).decode("utf-8"))
    return encoded_list

def decode_b64_to_images(b64_list: list) -> list:
    pil_list = []
    for b64_str in b64_list:
        try:
            img_bytes = base64.b64decode(b64_str)
            pil_list.append(Image.open(io.BytesIO(img_bytes)).convert("RGB"))
        except Exception:
            pass
    return pil_list

def save_session_to_db(username: str, title: str, description: str, result: str, images: list, messages: list) -> int:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    images_json = json.dumps(encode_images_to_b64(images))
    messages_json = json.dumps(messages)
    c.execute(
        "INSERT INTO history (username, title, description, result, images_json, messages_json) VALUES (?, ?, ?, ?, ?, ?)",
        (username, title, description, result, images_json, messages_json)
    )
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return session_id

def update_session_messages_in_db(session_id: int, messages: list):
    if not session_id:
        return
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE history SET messages_json = ? WHERE id = ?", (json.dumps(messages), session_id))
    conn.commit()
    conn.close()

def load_user_history(username: str) -> list:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT id, title, description, result, images_json, messages_json FROM history WHERE username = ? ORDER BY id ASC",
        (username,)
    )
    rows = c.fetchall()
    conn.close()
    loaded = []
    for r in rows:
        loaded.append({
            "id": r[0],
            "title": r[1],
            "description": r[2],
            "result": r[3],
            "images": decode_b64_to_images(json.loads(r[4] or "[]")),
            "messages": json.loads(r[5] or "[]")
        })
    return loaded

init_db()

# ---------------- SESSION STATE ----------------

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "history" not in st.session_state:
    st.session_state.history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "fixi_mood" not in st.session_state:
    st.session_state.fixi_mood = "🚀 Online & Ready"

if "active_images" not in st.session_state:
    st.session_state.active_images = []

if "active_description" not in st.session_state:
    st.session_state.active_description = ""

if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = None

if "uploader_counter" not in st.session_state:
    st.session_state.uploader_counter = 0

# ---------------- SIDEBAR (THEME SELECTOR) ----------------

with st.sidebar:
    st.markdown("## 🚀 DS-FixIT")
    st.caption("Universal AI Problem Detector • v6.4 MARK-HUD")
    st.divider()

    st.markdown("### 🎨 Interface Mode")
    theme_choice = st.selectbox(
        "Select Interface Aesthetic",
        ["Blue Cyber", "Stark Iron Man Mode"],
        label_visibility="collapsed"
    )

    # Theme Styling Profiles
    if theme_choice == "Stark Iron Man Mode":
        primary_color = "#ffb700"  # Stark Gold
        secondary_accent = "#ff3b30" # Stark Crimson Red
        title_gradient = "linear-gradient(90deg, #ff3b30, #ffb700, #ffea00)"
        box_border = "#ffb700"
        box_glow = "rgba(255, 183, 0, 0.4)"
        badge_bg = "#d90429"
        companion_title = "JARVIS / FRIDAY"
        companion_avatar = "⚡🤖"
    else:
        primary_color = "#009fff"
        secondary_accent = "#ec2f4b"
        title_gradient = "linear-gradient(90deg, #009fff, #ec2f4b)"
        box_border = "#009fff"
        box_glow = "rgba(0, 159, 255, 0.3)"
        badge_bg = "#009fff"
        companion_title = "FIXI"
        companion_avatar = "🧿🌐"

    st.divider()

    st.markdown("### 🔐 Account & Cloud Vault")
    if st.session_state.current_user:
        st.success(f"Logged in as **{st.session_state.current_user}**")
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.current_user = None
            st.session_state.history = []
            st.session_state.messages = []
            st.session_state.latest_result = None
            st.session_state.active_images = []
            st.session_state.active_description = ""
            st.session_state.active_session_id = None
            st.session_state.uploader_counter += 1
            st.rerun()
    else:
        auth_tab1, auth_tab2 = st.tabs(["Login", "Sign Up"])
        with auth_tab1:
            login_user = st.text_input("Username", key="login_u")
            login_pass = st.text_input("Password", type="password", key="login_p")
            if st.button("🔓 Login", use_container_width=True):
                if authenticate_user(login_user, login_pass):
                    st.session_state.current_user = login_user.strip()
                    st.session_state.history = load_user_history(st.session_state.current_user)
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        with auth_tab2:
            reg_user = st.text_input("New Username", key="reg_u")
            reg_pass = st.text_input("New Password", type="password", key="reg_p")
            if st.button("✨ Create Account", use_container_width=True):
                if not reg_user.strip() or not reg_pass.strip():
                    st.warning("Enter both username and password.")
                elif register_user(reg_user, reg_pass):
                    st.session_state.current_user = reg_user.strip()
                    st.session_state.history = []
                    st.success("Account created! Vault unlocked.")
                    st.rerun()
                else:
                    st.error("Username already taken.")
        st.caption("💡 Guest mode active (history clears on refresh unless logged in).")

    st.divider()

    st.markdown(f"### 🤖 {companion_title} Companion")
    st.markdown(f"""
    <div class="fixi-box">
        <div class="cyber-anime-face">{companion_avatar}</div>
        <b style="color: {primary_color}; font-size: 18px; letter-spacing: 1px;">{companion_title}</b><br>
        <span style="font-size: 11px; opacity: 0.85; color: {primary_color}; font-family: monospace;"><i>[{theme_choice} HUD]</i></span><br>
        <span style="font-size: 12px; opacity: 0.8;">Status: {st.session_state.fixi_mood}</span><br><br>
        <span class="tech-badge">Honest</span> 
        <span class="tech-badge">Polite</span> 
        <span class="tech-badge">Turbo Stream</span>
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
    if st.button("➕ New Clean Scan", use_container_width=True):
        st.session_state.latest_result = None
        st.session_state.active_description = ""
        st.session_state.active_report = ""
        st.session_state.active_images = []
        st.session_state.messages = []
        st.session_state.active_session_id = None
        st.session_state.uploader_counter += 1
        st.rerun()

    search_query = st.text_input("🔍 Search past sessions", placeholder="Keyword...")

    if not st.session_state.history:
        st.caption("No history logged yet.")
    else:
        filtered_history = [
            item for item in st.session_state.history 
            if search_query.lower() in item["title"].lower() or search_query.lower() in item["result"].lower()
        ] if search_query else st.session_state.history

        for i, item in enumerate(reversed(filtered_history[-15:])):
            if st.button(f"📌 {item['title'][:25]}...", key=f"history_{item.get('id', i)}_{i}", use_container_width=True):
                st.session_state.latest_result = item["result"]
                st.session_state.active_description = item.get("description", "")
                st.session_state.active_report = item["result"]
                st.session_state.active_images = item.get("images", [])
                st.session_state.messages = item.get("messages", [])
                st.session_state.active_session_id = item.get("id")
                st.session_state.uploader_counter += 1
                st.rerun()

    st.divider()

    with st.expander("ℹ️ About DS-FixIT & Creator"):
        st.write("**DS-FixIT** is a universal multi-modal AI problem detector powered by advanced vision and reasoning.")
        st.write("**Creator:** J.P. Dheepak Saianand")
        st.write(f"**Companion:** {companion_title}")
        st.caption("DS-FixIT © 2026 • Built with Streamlit & OpenRouter")

# ---------------- CONFIG & DYNAMIC STYLING (IRON MAN MARK-HUD) ----------------

scanlines_css = """
background: linear-gradient(
    rgba(18, 16, 16, 0) 50%, 
    rgba(0, 0, 0, 0.15) 50%
), linear-gradient(
    90deg,
    rgba(255, 0, 0, 0.03),
    rgba(0, 255, 0, 0.01),
    rgba(0, 0, 255, 0.03)
);
background-size: 100% 3px, 3px 100%;
""" if theme_choice == "Stark Iron Man Mode" else ""

st.markdown(f"""
<style>
.stApp {{
    background-color: var(--background-color);
    color: var(--text-color);
    {scanlines_css}
}}

[data-testid="stSidebar"] {{
    background-color: var(--secondary-background-color);
    border-right: 2px solid {box_border}55;
}}

.main-title {{
    font-size: 48px;
    font-weight: 900;
    background: {title_gradient};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 1.5px;
    font-family: 'Courier New', monospace;
    text-shadow: 0 0 20px {box_glow};
}}

.subtitle {{
    color: var(--text-color);
    opacity: 0.9;
    font-size: 16px;
    font-weight: 600;
    font-family: monospace;
    letter-spacing: 0.5px;
}}

div.stButton > button {{
    border-radius: {'4px' if theme_choice == 'Stark Iron Man Mode' else '12px'};
    background: {title_gradient};
    color: {'#000000' if theme_choice == 'Stark Iron Man Mode' else '#ffffff'};
    font-weight: 900;
    border: {'1px solid #ffb700' if theme_choice == 'Stark Iron Man Mode' else 'none'};
    box-shadow: 0 0 15px {box_glow};
    transition: all 0.2s ease;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

div.stButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 0 25px {box_glow};
}}

.metric-row {{
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
}}

.box-risk-high {{
    flex: 1;
    background: linear-gradient(135deg, #7f1d1d, #ef4444);
    color: white;
    padding: 16px;
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
}}

.box-risk-med {{
    flex: 1;
    background: linear-gradient(135deg, #78350f, #f59e0b);
    color: white;
    padding: 16px;
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
}}

.box-risk-low {{
    flex: 1;
    background: linear-gradient(135deg, #065f46, #10b981);
    color: white;
    padding: 16px;
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
}}

.box-confidence {{
    flex: 1;
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    color: white;
    padding: 16px;
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
}}

.tech-badge {{
    background: {badge_bg};
    color: {'#000000' if theme_choice == 'Stark Iron Man Mode' else '#ffffff'};
    padding: 3px 9px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: bold;
    font-family: monospace;
}}

.fixi-box {{
    background-color: var(--secondary-background-color);
    padding: 16px;
    border-radius: {'6px' if theme_choice == 'Stark Iron Man Mode' else '14px'};
    text-align: center;
    border: 2px solid {primary_color};
    box-shadow: 0 0 25px {box_glow};
    color: var(--text-color);
}}

.cyber-anime-face {{
    font-size: 44px;
    background: {title_gradient};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 15px {box_glow});
    margin-bottom: 5px;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.markdown('<div class="main-title">DS-FixIT 🚀 MARK-HUD</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">SYSTEM ACTIVE // MODE: {solver_mode.upper()} // VISOR: {theme_choice.upper()}</div>', unsafe_allow_html=True)
st.write("Advanced multi-modal telemetry inspection with visor HUD scanlines and active reasoning.")
st.divider()

# ---------------- INPUT SECTION ----------------

st.markdown("## 🚀 What's the problem today?")
col_desc, col_extra = st.columns(2)

with col_desc:
    description = st.text_area("Describe your problem", value=st.session_state.get("active_description", ""), placeholder="Explain issue or paste code/equations...", height=140)

with col_extra:
    additional_info = st.text_area("Additional Information (Optional Context)", placeholder="Environment, OS, error logs...", height=140)

uploaded_files = st.file_uploader(
    "📎 Upload Evidence (Images, Audio, PDF, Text, or Code Files)",
    type=["png", "jpg", "jpeg", "webp", "pdf", "txt", "csv", "py", "json", "mp3", "wav", "m4a"],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_counter}"
)

def optimize_image_for_vision(uploaded_file, max_dim=1024) -> Image.Image:
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
    return img

file_notes = {}
current_prepared_images = []
first_uploaded_filename = None

if uploaded_files:
    first_uploaded_filename = uploaded_files[0].name
    st.markdown("### 🗂️ Attached Evidence")
    for file in uploaded_files:
        c1, c2 = st.columns([1, 2])
        with c1:
            if file.type.startswith("image/"):
                img = optimize_image_for_vision(file, max_dim=1024)
                st.image(img, caption=f"Evidence: {file.name} (Optimized)", width=240)
                current_prepared_images.append(img)
            else:
                st.write(f"📁 **{file.name}** ({file.type or 'file'})")
        with c2:
            note = st.text_input(f"Note for {file.name}", placeholder="e.g. Oblique fracture at distal tibia...", key=f"note_{file.name}")
            if note:
                file_notes[file.name] = note
elif "active_images" in st.session_state and st.session_state.active_images:
    st.markdown("### 🗂️ Loaded Session Evidence")
    for idx, img in enumerate(st.session_state.active_images):
        st.image(img, caption=f"Historical Evidence #{idx+1}", width=240)
        current_prepared_images.append(img)

# ---------------- ANALYSIS ENGINE (STREAMING WITH VISIBLE STATUS) ----------------

if st.button("🚀 ANALYSE WITH TELEMETRY", type="primary", use_container_width=True):
    if not description.strip() and not uploaded_files and not st.session_state.get("active_images"):
        st.warning("Please describe the problem or upload evidence.")
    else:
        st.session_state.fixi_mood = "⚡ Telemetry Active..."
        
        status_container = st.empty()
        status_container.markdown(f"### 🧠 {companion_title} is running visor diagnostics...")

        try:
            api_key = st.secrets["OPENROUTER_APIKEY"]
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

            notes_str = "\n".join([f"- {fname}: {note}" for fname, note in file_notes.items()])

            prompt = (
                f"You are {companion_title}, an advanced, rigorous {theme_choice} AI assistant integrated into DS-FixIT.\n"
                f"Selected Solver Mode: {solver_mode}\n\n"
                "CRITICAL TAG REQUIREMENTS:\n"
                "You MUST start your response with these exact lines:\n"
                "RISK_LEVEL: [High / Medium / Low]\n"
                "CONFIDENCE_SCORE: [e.g. 95%]\n\n"
                "CRITICAL FORMATTING GUIDELINES:\n"
                "- Keep explanations punchy, fast, and direct. Avoid filler.\n"
                "- Use bold markdown (**...**) exclusively on critical failure points, key root causes, and primary action items.\n"
                "- Use LaTeX ($...$ or $$...$$) for all math equations and formulas.\n"
                "- Inspect the uploaded image(s) thoroughly to independently detect and locate fractures, anomalies, structural defects, or errors.\n\n"
                f"USER PROBLEM:\n{description}\n\nADDITIONAL INFO:\n{additional_info}\n\n"
                f"FILE NOTES:\n{notes_str if notes_str else 'None'}\n\n"
                "Provide sections:\n"
                "## 1. Executive Summary\n"
                "## 2. Root Cause Analysis\n"
                "## 3. Actionable Solution / Steps\n"
                "## 4. Safety & Verification\n"
            )

            content = [{"type": "text", "text": prompt}]
            
            for img in current_prepared_images:
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85)
                encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}
                })

            if uploaded_files:
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

            status_container.markdown(f"### ⚡ {companion_title} is streaming telemetry stream...")
            st.divider()
            st.markdown("## ⚡ Live Telemetry Diagnostic Stream")
            
            def stream_generator():
                stream = client.chat.completions.create(
                    model="openrouter/free",
                    messages=[{"role": "user", "content": content}],
                    stream=True
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta

            result = st.write_stream(stream_generator())
            status_container.empty()

            if description.strip():
                session_title = description.strip()
            elif first_uploaded_filename:
                session_title = first_uploaded_filename
            else:
                session_title = "General Diagnostic Session"

            st.session_state.latest_result = result
            st.session_state.active_description = description
            st.session_state.active_report = result
            st.session_state.active_images = current_prepared_images
            st.session_state.messages = []
            st.session_state.fixi_mood = "🎯 Ready for Next Task"

            new_id = None
            if st.session_state.current_user:
                new_id = save_session_to_db(
                    st.session_state.current_user,
                    session_title,
                    description,
                    result,
                    current_prepared_images,
                    []
                )

            st.session_state.active_session_id = new_id
            st.session_state.history.append({
                "id": new_id,
                "title": session_title,
                "description": description,
                "result": result,
                "images": current_prepared_images,
                "messages": []
            })
            st.rerun()
        except Exception as e:
            status_container.empty()
            st.session_state.fixi_mood = "⚠️ Error Encountered"
            st.error(f"Analysis failed: {e}")

# ---------------- RESULTS DISPLAY ----------------

if "latest_result" in st.session_state and st.session_state.latest_result:
    st.divider()
    st.markdown("## 🔍 Diagnostic Telemetry Report")

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
            <h1 style="color: {primary_color};">DS-FixIT 🚀 Diagnostic Report</h1>
            <p><b>Mode:</b> {solver_mode} | <b>Visor HUD:</b> {theme_choice}</p>
            <hr/>
            <div>{clean_report.replace(chr(10), '<br>')}</div>
            <hr/>
            <p style="font-size: 11px; color: #777;">Generated by {companion_title} • DS-FixIT © 2026</p>
        </body>
        </html>
        """
        st.download_button("📄 Download Official PDF Report", data=pdf_html_content, file_name="Report.html", mime="text/html", key="html_rep_btn")

# ---------------- INTERACTIVE CHAT ----------------

st.divider()
st.markdown(f"## 💬 Talk with {companion_title}")
for message in st.session_state.messages:
    avatar_icon = "⚡" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

question = st.chat_input(f"Ask {companion_title} a follow-up question...")
if question:
    if "latest_result" not in st.session_state or not st.session_state.latest_result:
        st.warning(f"Run an analysis first so {companion_title} has context!")
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user", avatar="👤"):
            st.markdown(question)

        try:
            api_key = st.secrets["OPENROUTER_APIKEY"]
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
            
            active_desc = st.session_state.get("active_description", "Previous analysis")
            active_rep = st.session_state.get("active_report", st.session_state.latest_result)
            
            system_context = (
                f"You are {companion_title}, an advanced, rigorous {theme_choice} AI assistant integrated into DS-FixIT.\n"
                f"Active Solver Mode: {solver_mode}\n"
                f"Original User Problem/Context: {active_desc}\n"
                f"Previous Diagnostic Report:\n{active_rep}\n\n"
                "Answer the user's follow-up questions referencing this active context. Use bold markdown for key takeaways and be direct and concise."
            )
            
            conv = [{"role": "system", "content": system_context}]
            conv.extend(st.session_state.messages[-10:])
            
            with st.chat_message("assistant", avatar="⚡"):
                def chat_stream():
                    stream = client.chat.completions.create(
                        model="openrouter/free",
                        messages=conv,
                        stream=True
                    )
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            yield delta

                reply = st.write_stream(chat_stream())

            st.session_state.messages.append({"role": "assistant", "content": reply})
            
            active_id = st.session_state.get("active_session_id")
            if active_id:
                update_session_messages_in_db(active_id, st.session_state.messages)
                for h in st.session_state.history:
                    if h.get("id") == active_id:
                        h["messages"] = st.session_state.messages
            elif st.session_state.history:
                st.session_state.history[-1]["messages"] = st.session_state.messages
                
            st.rerun()
        except Exception as e:
            st.error(f"Chat failed: {e}")
