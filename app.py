import streamlit as st
import requests
import time
from openai import OpenAI

st.set_page_config(
    page_title="DS-FixIT",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ DS-FixIT")
st.subheader("Universal AI Problem Detector")
st.markdown("### Detect. Analyse. Fix.")
st.caption("Created by J.P. Dheepak Saianand")

st.divider()

st.header("🔍 Submit your issue")

description = st.text_area(
    "Describe your problem",
    placeholder="What's happening?"
)

files = st.file_uploader(
    "Upload evidence",
    accept_multiple_files=True
)

if st.button("Analyse Issue", type="primary"):
    st.write("DEBUG: Analyse button clicked")

    if not description.strip() and not files:
        st.warning("Please describe or upload an issue.")

    else:
        try:
            with st.spinner("FIXI is analysing your issue..."):
                # Initialize OpenRouter API client via OpenAI SDK
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=st.secrets["OPENROUTER_APIKEY"],
                )

                response = client.chat.completions.create(
                    model="google/gemini-2.0-flash-001",  # Or any desired model on OpenRouter
                    messages=[
                        {
                            "role": "user",
                            "content": f"Problem description: {description}"
                        }
                    ]
                )

                result = response.choices[0].message.content

            st.subheader("🔎 Analysis Results")
            st.markdown(result)

        except Exception as e:
            st.error(f"Analysis failed: {e}")

st.divider()
st.write("FIXI: Checking OpenRouter connectivity...")

try:
    start = time.time()

    r = requests.get(
        "https://openrouter.ai/api/v1/models",
        timeout=10
    )

    st.write("OpenRouter reachable:", r.status_code)
    st.write("Time:", round(time.time() - start, 2), "seconds")

except Exception as e:
    st.error(f"Network diagnostic failed: {repr(e)}")
