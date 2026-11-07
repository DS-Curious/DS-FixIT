
import streamlit as st
from providers.gemini import GeminiProvider

st.set_page_config(
    page_title="DS-FixIT",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ DS-FixIT")
st.caption("DEBUG BUILD: FIXIT-1107-A")
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
                ai = GeminiProvider(
                    st.secrets["GEMINI_API_KEY"]
                )

                result = ai.analyse(
                    description,
                    files
                )

            st.subheader("🔎 Analysis Results")
            st.markdown(result)

        except Exception as e:
            st.error(f"Analysis failed: {e}")
