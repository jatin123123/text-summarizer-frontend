import streamlit as st
import requests

API_URL = "https://jatin12312-text-summarizer.hf.space" 

# --- Custom Styles ---
st.markdown("""
    <style>
        .main {
            background-color: #F7F8FC;
        }
        .stTextArea textarea {
            font-size: 1.2em !important;
            color: #293241;
            background-color: #EDF2F7 !important;
            border-radius: 10px !important;
        }
        .stButton>button {
            color: white !important;
            background: linear-gradient(90deg, #3D5A80 0%, #293241 100%);
            border-radius: 8px;
            font-size: 1.1em;
            padding: 0.6em 2em;
        }
        .stNumberInput input {
            font-size: 1.1em;
            background-color: #EDF2F7;
            border-radius: 7px;
            color: #293241;
        }
        h1 {
            color: #293241;
        }
        h2, h3 {
            color: #3D5A80;
        }
        .stMarkdown {
            font-size: 1.1em;
            color: #293241 !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Page Header ---
st.markdown("<h1>📝 Modern Text Summarizer</h1>", unsafe_allow_html=True)
st.markdown("#### Summarize any lengthy document with powerful AI in seconds.")

# --- Sidebar: Model Health & Info ---
with st.sidebar:
    st.image("https://huggingface.co/front/assets/hf-logo.svg", width=120)
    st.markdown("<h3>API Health</h3>", unsafe_allow_html=True)
    try:
        health = requests.get(f"{API_URL}/health", timeout=3)
        if health.ok:
            status = health.json().get("status", "unknown")
            model_info = health.json().get("model_info", {})
            st.success(f"API: {status.capitalize()}")
            st.info(f"Model: {model_info.get('model_name', 'N/A')}")
            if "version" in model_info:
                st.info(f"Version: {model_info['version']}")
        else:
            st.error("API unhealthy or model not loaded.")
    except Exception:
        st.error("Unable to connect to API.")

    st.markdown("---")
    st.markdown("##### About\nBuilt with FastAPI 🚀 & Hugging Face Transformers 🤗")

# --- Main Input Form ---
with st.form("summarize-form", clear_on_submit=False):
    st.markdown("<h2>🔗 Paste Text Below</h2>", unsafe_allow_html=True)
    text = st.text_area("Minimum 10 characters", height=220, max_chars=4096)
    
    col1, col2 = st.columns(2)
    with col1:
        min_length = st.number_input("Min summary length", min_value=10, max_value=100, value=50, help="Minimum number of tokens in summary.")
    with col2:
        max_length = st.number_input("Max summary length", min_value=30, max_value=500, value=150, help="Maximum number of tokens in summary.")
    
    submitted = st.form_submit_button("✨ Summarize Text")

# --- Summary Output ---
if submitted:
    if not text or len(text.strip()) < 10:
        st.error("🚫 Please enter at least 10 characters of text.")
    elif min_length >= max_length:
        st.warning("⚠️ Minimum length must be less than maximum length.")
    else:
        with st.spinner("Summarizing... Please wait."):
            payload = {
                "text": text.strip(),
                "min_length": int(min_length),
                "max_length": int(max_length)
            }
            try:
                resp = requests.post(f"{API_URL}/summarize", json=payload, timeout=15)
                if resp.ok:
                    result = resp.json()
                    st.markdown("<h3>✅ Summary</h3>", unsafe_allow_html=True)
                    st.markdown(f"<div style='background-color:#EDF2F7;border-radius:7px;padding:1em;color:#293241;font-size:1.1em;'>{result['summary']}</div>", unsafe_allow_html=True)
                    st.markdown(
                        f"""
                        <span style='color:#3D5A80;font-weight:bold;'>Original Length:</span> {result['original_length']} characters  
                        <span style='color:#3D5A80;font-weight:bold;'>Summary Length:</span> {result['summary_length']} characters  
                        <span style='color:#3D5A80;font-weight:bold;'>Model Used:</span> {result['model_used']}
                        """, unsafe_allow_html=True
                    )
                else:
                    error_msg = resp.json().get('error', 'Unknown error')
                    detail_msg = resp.json().get('detail', '')
                    st.error(f"🚫 Error: {error_msg}")
                    st.markdown(f"<div style='color:#EE6C4D;'>{detail_msg}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Failed to connect: {str(e)}")

st.markdown("---")
st.markdown("Powered by [Hugging Face Transformers](https://huggingface.co/) × [FastAPI](https://fastapi.tiangolo.com/) × [Streamlit](https://streamlit.io/)")
