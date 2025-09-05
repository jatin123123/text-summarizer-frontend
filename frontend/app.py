import streamlit as st
import requests

API_URL = "http://localhost:7860"  # Update to your FastAPI backend url if different

st.set_page_config(page_title="Text Summarizer", page_icon="🤖", layout="centered")

st.title("Text Summarizer 🤖")
st.write("Summarize long texts quickly and efficiently using an AI-powered summarizer.")

# Sidebar: explanation and API health check
with st.sidebar:
    st.header("API Health Status")
    try:
        health = requests.get(f"{API_URL}/health", timeout=3)
        if health.ok:
            status = health.json().get("status", "unknown")
            model_info = health.json().get("model_info", {})
            st.success(f"Status: {status}")
            st.write(f"Model: {model_info.get('model_name', 'N/A')}")
        else:
            st.error("API unhealthy or model not loaded.")
    except Exception:
        st.error("Unable to connect to API.")

st.subheader("Enter Text to Summarize")
text = st.text_area("Paste your text here (minimum 10 characters)", height=200)

col1, col2 = st.columns(2)
with col1:
    min_length = st.number_input("Minimum summary length", min_value=10, max_value=100, value=30)
with col2:
    max_length = st.number_input("Maximum summary length", min_value=30, max_value=500, value=150)

if st.button("Summarize"):
    if not text or len(text.strip()) < 10:
        st.warning("Please enter at least 10 characters of text.")
    elif min_length >= max_length:
        st.warning("Minimum length must be less than maximum length.")
    else:
        with st.spinner("Generating summary..."):
            payload = {
                "text": text,
                "min_length": int(min_length),
                "max_length": int(max_length)
            }
            try:
                resp = requests.post(f"{API_URL}/summarize", json=payload, timeout=15)
                if resp.ok:
                    result = resp.json()
                    st.success("Summary generated!")
                    st.markdown(f"**Summary:**\n\n{result['summary']}")
                    st.write(f"Original Length: {result['original_length']} characters")
                    st.write(f"Summary Length: {result['summary_length']} characters")
                    st.write(f"Model Used: {result['model_used']}")
                else:
                    st.error(f"Error: {resp.json().get('error', 'Unknown error')}")
                    st.write(resp.json().get('detail', 'No details provided'))
            except Exception as e:
                st.error(f"Failed to connect to API: {str(e)}")

st.markdown("""
---
Powered by Hugging Face Transformers.  
""")
