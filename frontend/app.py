import streamlit as st
import requests

API_URL = "https://jatin12312-text-summarizer.hf.space"

st.set_page_config(
    page_title="Text Summarizer AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def fetch_health():
    try:
        resp = requests.get(f"{API_URL}/health", timeout=4)
        if resp.ok:
            data = resp.json()
            return ("healthy", data.get("model_info", {}))
        return ("unhealthy", {})
    except Exception as e:
        return ("unreachable", {})

def summarize_api(text, min_length, max_length):
    try:
        payload = {
            "text": text,
            "min_length": int(min_length),
            "max_length": int(max_length)
        }
        resp = requests.post(f"{API_URL}/summarize", json=payload, timeout=20)
        if resp.ok:
            return resp.json(), None
        else:
            error_data = resp.json()
            return None, error_data.get('error', 'Unknown error')
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def stylish_card(title, value, icon):
    st.markdown(
        f"""
        <div style="background: var(--background-secondary); border-radius: 8px; padding: 18px; margin-bottom: 12px; box-shadow: 0 0 4px rgba(0,0,0,0.08); display: flex; align-items: center;">
            <div style="font-size: 1.6rem;">{icon}</div>
            <div style="margin-left: 12px;">
                <span style="font-weight: 600; font-size: 1.05rem;">{title}</span>
                <br>
                <span style="color: var(--text-secondary);">{value}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

status, model_info = fetch_health()

# Tabs for layout
tab1, tab2 = st.tabs(["Summarize Text", "About Model"])

with tab1:
    st.title("🧠 Modern Text Summarizer")
    st.write("Paste your text below and generate concise, accurate summaries using advanced AI.")

    st.markdown("#### Input")
    text = st.text_area(
        "Enter text to summarize", height=160, 
        placeholder="Paste an article, news story, or long paragraph (≥10 characters)..."
    )

    col1, col2, _ = st.columns([1,1,2])
    with col1:
        min_length = st.slider("Minimum summary length", 10, 100, 30)
    with col2:
        max_length = st.slider("Maximum summary length", 30, 500, 150)

    st.markdown("")

    submit = st.button("✨ Summarize!", type="primary")

    if submit:
        if not text or len(text.strip()) < 10:
            st.warning("Please enter at least 10 characters of text.")
        elif min_length >= max_length:
            st.warning("Minimum length must be less than maximum length.")
        elif status != "healthy":
            st.error("API unavailable or model not loaded. Please try again later.")
        else:
            with st.spinner("Generating summary..."):
                result, error = summarize_api(text, min_length, max_length)
                if error:
                    st.error(f"Error: {error}")
                elif result:
                    stylish_card("Summary", result["summary"], "📝")
                    # Expandable metadata section
                    with st.expander("Summary Metadata"):
                        stylish_card("Original Length", str(result["original_length"]) + " characters", "📜")
                        stylish_card("Summary Length", str(result["summary_length"]) + " characters", "✂️")
                        stylish_card("Model Used", result["model_used"], "🤖")
                else:
                    st.error("Unknown error occurred.")

    st.markdown("---")

    # Quick health/status display
    if status == "healthy":
        stylish_card("API Status", "Healthy and Connected", "✅")
        stylish_card("Model", model_info.get("model_name", "N/A"), "🤖")
    elif status == "unhealthy":
        stylish_card("API Status", "Unhealthy (Model not loaded)", "⚠️")
    else:
        stylish_card("API Status", "Unreachable", "❌")

with tab2:
    st.header("Model Information")
    st.write("This app uses Hugging Face Transformers for abstractive text summarization. Ideal for articles, news, and research content.")
    if model_info:
        stylish_card("Model Name", model_info.get("model_name", "N/A"), "🤖")
        # Display more properties if present
        for k, v in model_info.items():
            if k != "model_name":
                stylish_card(k.replace("_"," ").title(), v, "ℹ️")
    st.markdown("---")
    st.write("Visit the [project page](https://huggingface.co/facebook/bart-large-cnn) for technical details.")

# Footer in sidebar
with st.sidebar:
    st.header("Help & Settings")
    st.markdown(
        """
        **Instructions**  
        - Paste text, select summary length, and click Summarize  
        - Use the tabs above for information and troubleshooting  
        - Works best with texts longer than a paragraph

        **Appearance**  
        - Toggle site theme in Streamlit settings 🌗
        """
    )
    st.markdown("---")
    st.write("Made with ❤️ by [Jatin](https://huggingface.co/spaces/jatin12312/text-summarizer)")

# Optional: advanced styling
st.markdown("""
    <style>
    [data-testid="stSidebar"] span, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h3 {
        color: var(--primary-color);
    }
    </style>
""", unsafe_allow_html=True)
