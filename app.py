
import streamlit as st
import requests
import base64
import mimetypes
import time
from openai import OpenAI

st.set_page_config(
    page_title="DS-FixIT | Universal AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CONFIG ----------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg,
        #e5fcfa 0%,
        #eafff4 50%,
        #fffde8 100%
    );
}

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg, #d2f8f4, #e7fff0, #fff9d8
    );
}

.main-title {
    font-size: 46px;
    font-weight: 900;
    background: linear-gradient(
        90deg, #00aeca, #13b98b, #d6ae16
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    color: #397d78;
    font-size: 17px;
}

div.stButton > button {
    border-radius: 12px;
    background: linear-gradient(90deg,#13c4cf,#47dca9);
    color: #083c3c;
    font-weight: bold;
    border: none;
}

.result-card {
    padding: 20px;
    border-radius: 16px;
    background: rgba(255,255,255,0.75);
    border: 1px solid #a7e8d8;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------

if "history" not in st.session_state:
    st.session_state.history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("## ⚡ DS-FixIT")
    st.caption("Universal AI Problem Detector")

    st.divider()

    st.toggle("🌙 Dark mode", key="dark_mode")

    st.markdown("### 🧠 FIXI")
    st.write("Your intelligent AI companion.")
    st.caption("Honest • Polite • Helpful")

    st.divider()

    st.markdown("### 📚 Recent diagnoses")

    for i, item in enumerate(
        reversed(st.session_state.history[-10:])
    ):
        if st.button(
            item["title"][:28],
            key=f"history_{i}",
            use_container_width=True
        ):
            st.session_state.selected_history = item

    st.divider()

    st.markdown("### About")
    st.write("Creator: J.P. Dheepak Saianand")
    st.caption("DS-FixIT © 2026")

# ---------------- DARK MODE ----------------

if st.session_state.dark_mode:
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(
            135deg,#101f2d,#122d35,#20332c
        );
        color: white;
    }
    [data-testid="stSidebar"] {
        background: #142b35;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.markdown(
    '<div class="main-title">DS-FixIT ⚡</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Detect. Understand. Resolve.</div>',
    unsafe_allow_html=True
)

st.write(
    "One platform. Multiple problems. "
    "One intelligent companion."
)

st.divider()

# ---------------- INPUT ----------------

st.markdown("## 🔍 What's the problem?")

description = st.text_area(
    "Describe your problem",
    placeholder="Explain what's happening...",
    height=130
)

additional_info = st.text_area(
    "Additional information (optional)",
    placeholder="Provide context, observations, previous attempts...",
    height=90
)

uploaded_files = st.file_uploader(
    "📎 Upload images or supporting files",
    type=[
        "png", "jpg", "jpeg", "webp",
        "pdf", "txt", "csv", "mp3",
        "wav", "m4a"
    ],
    accept_multiple_files=True
)

if uploaded_files:
    st.write("### Uploaded evidence")

    for file in uploaded_files:
        if file.type.startswith("image/"):
            st.image(
                file,
                caption=file.name,
                width=300
            )
        else:
            st.write(f"📄 {file.name}")

# ---------------- ANALYSIS ----------------

if st.button(
    "⚡ ANALYSE WITH FIXI",
    type="primary",
    use_container_width=True
):

    if not description.strip() and not uploaded_files:
        st.warning("Please describe a problem or upload an image.")

    else:
        try:
            api_key = st.secrets["OPENROUTER_APIKEY"]

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )

            prompt = f"""
You are FIXI, the AI companion of DS-FixIT,
a universal problem detection assistant.

Personality:
- Honest and polite.
- Helpful and patient.
- Never pretend certainty.
- Clearly distinguish facts from possibilities.

USER PROBLEM:
{description}

ADDITIONAL INFORMATION:
{additional_info}

Analyze the supplied information.

Use this structure:

## 1. Problem Identification
## 2. Observations and Evidence
## 3. Probable Causes
## 4. Recommended Solutions
## 5. Prevention
## 6. Severity
## 7. Confidence and Limitations
## 8. Questions for the User

If evidence is insufficient, ask questions.
Never claim a diagnosis is absolutely accurate.
Mention safety precautions when relevant.
"""

            content = [
                {
                    "type": "text",
                    "text": prompt
                }
            ]

            for file in uploaded_files:
                if file.type.startswith("image/"):
                    encoded = base64.b64encode(
                        file.getvalue()
                    ).decode("utf-8")

                    mime = file.type

                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": (
                                f"data:{mime};base64,{encoded}"
                            )
                        }
                    })

            with st.spinner(
                "FIXI is examining your problem..."
            ):

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

            st.session_state.latest_result = result

            st.session_state.history.append({
                "title": description[:40] or "Uploaded evidence",
                "result": result
            })

        except Exception as e:
            st.error(f"Analysis failed: {e}")

# ---------------- RESULTS ----------------

if "latest_result" in st.session_state:

    st.divider()

    st.markdown("## 🔎 FIXI's Analysis")

    st.markdown(
        '<div class="result-card">',
        unsafe_allow_html=True
    )

    st.markdown(st.session_state.latest_result)

    st.markdown("</div>", unsafe_allow_html=True)

    st.download_button(
        "📥 Download analysis",
        data=st.session_state.latest_result,
        file_name="DS-FixIT-Analysis.md",
        mime="text/markdown"
    )

# ---------------- FIXI CHAT ----------------

st.divider()

st.markdown("## 💬 Talk to FIXI")

st.caption(
    "Have follow-up questions? FIXI is here to help."
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input(
    "Ask FIXI something..."
)

if question:

    if "latest_result" not in st.session_state:
        st.warning("Analyse a problem first!")
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
                        "You are FIXI, the honest, polite "
                        "AI companion of DS-FixIT. "
                        "Answer follow-up questions using "
                        "the diagnosis context. Admit uncertainty."
                    )
                },
                {
                    "role": "assistant",
                    "content": (
                        "Previous diagnosis:\n"
                        + st.session_state.latest_result
                    )
                }
            ]

            conversation.extend(
                st.session_state.messages[-10:]
            )

            with st.spinner("FIXI is thinking..."):
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
