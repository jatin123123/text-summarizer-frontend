import streamlit as st
import requests

DEFAULT_API_URL = "https://jatin12312-text-summarizer.hf.space"

st.set_page_config(page_title="Text Summarizer", page_icon="🧠", layout="centered")

# -----------------------------
# Helpers
# -----------------------------
@st.cache_data(ttl=30)
def check_health(api_url: str):
    try:
        r = requests.get(f"{api_url}/health", timeout=6)
        if r.ok:
            data = r.json()
            return {"status": "healthy", "model_info": data.get("model_info", {})}, None
        else:
            # Attempt to read structured error
            data = {}
            try:
                data = r.json()
            except Exception:
                pass
            return {"status": "unhealthy", "detail": data.get("detail") or data.get("error")}, None
    except Exception as e:
        return None, f"Health check failed: {e}"

def summarize(api_url: str, text: str, min_len: int, max_len: int):
    try:
        payload = {"text": text, "min_length": int(min_len), "max_length": int(max_len)}
        r = requests.post(f"{api_url}/summarize", json=payload, timeout=30)
        if r.ok:
            return r.json(), None
        else:
            # Backend may return {"error": "...", "detail": "..."} in handlers
            try:
                err = r.json()
                return None, err.get("error") or err.get("detail") or f"HTTP {r.status_code}"
            except Exception:
                return None, f"HTTP {r.status_code}"
    except Exception as e:
        return None, f"Request failed: {e}"

# -----------------------------
# Sidebar (classic inputs/status)
# -----------------------------
with st.sidebar:
    st.title("Controls")
    api_url = st.text_input("API URL", value=DEFAULT_API_URL)
    st.caption("Change only if the backend URL differs.")

    st.divider()
    st.subheader("Summary length")
    min_length = st.slider("Minimum", min_value=10, max_value=100, value=30, step=1)
    max_length = st.slider("Maximum", min_value=30, max_value=500, value=150, step=5)

    st.divider()
    st.subheader("API status")
    health, health_err = check_health(api_url)
    if health_err:
        st.error("Unreachable")
        st.caption(health_err)
    else:
        if health and health.get("status") == "healthy":
            st.success("Healthy")
            model_name = (health.get("model_info") or {}).get("model_name", "Unknown model")
            st.caption(f"Model: {model_name}")
        elif health and health.get("status") == "unhealthy":
            st.warning("Unhealthy")
            if health.get("detail"):
                st.caption(health.get("detail"))

# -----------------------------
# Main content (classic single column)
# -----------------------------
st.title("Text Summarizer 🧠")
st.write("Paste text, set preferred summary length, and generate a concise summary.")

# Input form to avoid reruns on every widget interaction
with st.form("summarize_form", clear_on_submit=False):
    text = st.text_area(
        "Text to summarize",
        height=220,
        placeholder="Paste an article, post, or paragraph (≥ 10 characters)...",
    )
    # Helpful counters
    col_a, col_b = st.columns(2)
    with col_a:
        st.caption(f"Characters: {len(text.strip()) if text else 0}")
    with col_b:
        st.caption(f"Min {min_length} • Max {max_length}")

    submitted = st.form_submit_button("Summarize")

# Validation and request
if submitted:
    cleaned = (text or "").strip()
    if len(cleaned) < 10:
        st.warning("Input text must be at least 10 characters.")
    elif min_length >= max_length:
        st.warning("Minimum length must be less than maximum length.")
    elif not health or health.get("status") != "healthy":
        st.error("API unavailable or model not loaded.")
    else:
        with st.spinner("Generating summary..."):
            result, err = summarize(api_url, cleaned, min_length, max_length)
        if err:
            st.error("Failed to generate summary.")
            st.caption(err)
        else:
            st.subheader("Summary")
            st.write(result["summary"])

            st.divider()
            st.subheader("Details")
            c1, c2, c3 = st.columns(3)
            c1.metric("Original length", f"{result['original_length']} chars")
            c2.metric("Summary length", f"{result['summary_length']} chars")
            c3.metric("Model", result["model_used"])

st.divider()
st.caption("Created by Jatin Jangid")
