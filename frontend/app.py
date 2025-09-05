import streamlit as st
import httpx
import asyncio
import time
from typing import Optional
import json

# Configure Streamlit page
st.set_page_config(
    page_title="Text Summarizer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
BACKEND_URL = "https://jatin12312-text-summarizer.hf.space"
MAX_TEXT_LENGTH = 50000  # Character limit for input text
st.markdown("""
<style>
    /* Import Premium Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Roboto:wght@300;400;500;700&display=swap');
    
    /* Global Reset & Base Styling */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
    }
    
    /* Root Variables for Consistent Theme */
    :root {
        --primary-color: #2563eb;
        --secondary-color: #1e40af;
        --accent-color: #3b82f6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --border-color: #e5e7eb;
        --shadow-light: 0 1px 3px rgba(0, 0, 0, 0.1);
        --shadow-medium: 0 4px 6px rgba(0, 0, 0, 0.1);
        --shadow-heavy: 0 10px 25px rgba(0, 0, 0, 0.15);
        --border-radius: 12px;
        --border-radius-lg: 16px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Main App Container */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        min-height: 100vh;
    }
    
    /* Main Content Container */
    .main .block-container {
        background: var(--bg-primary);
        border-radius: var(--border-radius-lg);
        padding: 2.5rem;
        margin: 1.5rem auto;
        max-width: 1400px;
        box-shadow: var(--shadow-heavy);
        border: 1px solid var(--border-color);
        position: relative;
        overflow: hidden;
    }
    
    .main .block-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
        border-radius: var(--border-radius-lg) var(--border-radius-lg) 0 0;
    }
    
    /* Premium Header Styling */
    .premium-header {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem 0;
        position: relative;
    }
    
    .premium-header h1 {
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin-bottom: 1rem !important;
        font-family: 'Poppins', sans-serif !important;
        letter-spacing: -0.02em !important;
        line-height: 1.2 !important;
    }
    
    .premium-header .subtitle {
        font-size: 1.2rem;
        color: var(--text-secondary);
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    /* Sidebar Premium Styling */
    .css-1d391kg, .css-1cypcdb {
        background: var(--bg-primary) !important;
        border-radius: var(--border-radius-lg) !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: var(--shadow-medium) !important;
        margin: 1rem !important;
        padding: 1.5rem !important;
    }
    
    /* Enhanced Input Cards */
    .input-card, .output-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-lg);
        padding: 2rem;
        box-shadow: var(--shadow-medium);
        margin-bottom: 2rem;
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }
    
    .input-card::before, .output-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
    }
    
    .input-card:hover, .output-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-heavy);
    }
    
    /* Premium Summary Card */
    .premium-summary-card {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-lg);
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: var(--shadow-medium);
        position: relative;
        overflow: hidden;
    }
    
    .premium-summary-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, var(--success-color), var(--accent-color));
    }
    
    .premium-summary-card h4 {
        color: var(--text-primary);
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .premium-summary-card .summary-text {
        font-size: 1.1rem;
        line-height: 1.8;
        color: var(--text-primary);
        background: rgba(59, 130, 246, 0.05);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        border-left: 3px solid var(--accent-color);
    }
    
    /* Enhanced Statistics Grid */
    .premium-stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .premium-stat-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 2rem 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-light);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }
    
    .premium-stat-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-medium);
    }
    
    .premium-stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
    }
    
    .premium-stat-card .stat-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
        color: var(--accent-color);
    }
    
    .premium-stat-card .stat-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-weight: 500;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .premium-stat-card .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }
    
    /* Premium Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius) !important;
        padding: 1rem 2.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: var(--transition) !important;
        box-shadow: var(--shadow-medium) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-heavy) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Enhanced Input Styling */
    .stTextArea > div > div > textarea {
        background: var(--bg-secondary) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: var(--border-radius) !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        transition: var(--transition) !important;
        font-family: 'Roboto', monospace !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }
    
    /* Premium Slider Styling */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color)) !important;
    }
    
    .stSlider > div > div > div > div > div > div {
        background: white !important;
        border: 2px solid var(--accent-color) !important;
        box-shadow: var(--shadow-light) !important;
    }
    
    /* File Uploader Enhancement */
    .stFileUploader > div {
        background: var(--bg-secondary) !important;
        border: 2px dashed var(--accent-color) !important;
        border-radius: var(--border-radius) !important;
        padding: 2rem !important;
        text-align: center !important;
        transition: var(--transition) !important;
    }
    
    .stFileUploader > div:hover {
        background: rgba(59, 130, 246, 0.05) !important;
        border-color: var(--primary-color) !important;
    }
    
    /* Message Styling */
    .premium-error {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        color: var(--error-color);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--error-color);
        box-shadow: var(--shadow-light);
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .premium-success {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        color: var(--success-color);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        border-left: 4px solid var(--success-color);
        box-shadow: var(--shadow-light);
        font-weight: 500;
        margin: 1rem 0;
    }
    
    /* Premium Footer */
    .premium-footer {
        text-align: center;
        padding: 3rem 0 2rem;
        border-top: 1px solid var(--border-color);
        margin-top: 4rem;
        color: var(--text-secondary);
    }
    
    .premium-footer .footer-content {
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    .premium-footer .footer-links {
        margin-top: 1.5rem;
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
    }
    
    .premium-footer a {
        color: var(--accent-color);
        text-decoration: none;
        font-weight: 500;
        transition: var(--transition);
    }
    
    .premium-footer a:hover {
        color: var(--primary-color);
    }
    
    /* Loading Animation */
    .loading-animation {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid var(--border-color);
        border-radius: 50%;
        border-top-color: var(--accent-color);
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .premium-header h1 {
            font-size: 2.5rem !important;
        }
        
        .premium-header .subtitle {
            font-size: 1rem;
        }
        
        .main .block-container {
            margin: 0.5rem;
            padding: 1.5rem;
        }
        
        .premium-stats-grid {
            grid-template-columns: 1fr;
        }
        
        .premium-footer .footer-links {
            flex-direction: column;
            gap: 1rem;
        }
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }
</style>
""", unsafe_allow_html=True)


class SummarizerClient:
    """Client class to handle communication with the FastAPI backend."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def check_health(self) -> dict:
        """Check if the backend is healthy and ready."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health", timeout=10.0)
                if response.status_code == 200:
                    return {"status": "healthy", "data": response.json()}
                else:
                    return {"status": "error", "message": f"Backend returned status {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def summarize(self, text: str, max_length: int = 150, min_length: int = 30) -> dict:
        """Send text to backend for summarization."""
        try:
            payload = {
                "text": text,
                "max_length": max_length,
                "min_length": min_length
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/summarize",
                    json=payload,
                    timeout=120.0  # Extended timeout for large texts
                )
                
                if response.status_code == 200:
                    return {"status": "success", "data": response.json()}
                else:
                    error_data = response.json() if response.headers.get("content-type") == "application/json" else {"error": response.text}
                    return {"status": "error", "message": error_data.get("error", "Unknown error occurred")}
                    
        except httpx.TimeoutException:
            return {"status": "error", "message": "Request timed out. The text might be too long."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

def run_async(coro):
    """Helper function to run async code in Streamlit."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

def display_statistics(original_length: int, summary_length: int, model_name: str):
    """Display statistics about the summarization."""
    compression_ratio = (1 - summary_length / original_length) * 100 if original_length > 0 else 0
    
    st.markdown("""
    <div class="premium-stats-grid">
        <div class="premium-stat-card">
            <div class="stat-icon">📄</div>
            <div class="stat-label">Original Length</div>
            <div class="stat-value">{:,}</div>
        </div>
        <div class="premium-stat-card">
            <div class="stat-icon">✨</div>
            <div class="stat-label">Summary Length</div>
            <div class="stat-value">{:,}</div>
        </div>
        <div class="premium-stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-label">Compression</div>
            <div class="stat-value">{:.1f}%</div>
        </div>
        <div class="premium-stat-card">
            <div class="stat-icon">🤖</div>
            <div class="stat-label">Model Used</div>
            <div class="stat-value">{}</div>
        </div>
    </div>
    """.format(original_length, summary_length, compression_ratio, model_name.split('/')[-1]), 
    unsafe_allow_html=True)

def create_download_link(text: str, filename: str = "summary.txt") -> str:
    """Create a download link for the summary text."""
    import base64
    
    # Encode text for download
    b64 = base64.b64encode(text.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">📄 Download Summary as TXT</a>'
    return href


def main():
    """Main Streamlit application."""
    
    # Premium Header
    st.markdown("""
    <div class="premium-header">
        <h1>🤖 AI Text Summarizer</h1>
        <div class="subtitle">
            Transform lengthy documents into concise, meaningful summaries using state-of-the-art AI models.
            Experience the power of advanced natural language processing.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize client
    client = SummarizerClient(BACKEND_URL)
    
    # Sidebar for settings and status
    with st.sidebar:
        st.markdown("### ⚙️ Settings & Controls")
        
        # Check backend health
        st.markdown("#### 🔍 Backend Status")
        if st.button("🔄 Check Backend Status", use_container_width=True):
            with st.spinner("Checking backend..."):
                health_result = run_async(client.check_health())
                
                if health_result["status"] == "healthy":
                    st.markdown('<div class="premium-success">✅ Backend is healthy and ready!</div>', unsafe_allow_html=True)
                    if "data" in health_result:
                        model_info = health_result["data"].get("model_info", {})
                        st.json(model_info)
                else:
                    st.markdown(f'<div class="premium-error">❌ Backend Error: {health_result["message"]}</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Summarization parameters
        st.markdown("#### 📊 Summary Parameters")
        max_length = st.slider(
            "Maximum Summary Length",
            min_value=50,
            max_value=500,
            value=150,
            step=10,
            help="Maximum number of tokens in the summary"
        )
        
        min_length = st.slider(
            "Minimum Summary Length",
            min_value=10,
            max_value=100,
            value=30,
            step=5,
            help="Minimum number of tokens in the summary"
        )
        
        # Validate lengths
        if min_length >= max_length:
            st.markdown('<div class="premium-error">⚠️ Minimum length must be less than maximum length!</div>', unsafe_allow_html=True)
    
    # Main content area with premium cards
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("""
        <div class="input-card">
            <h3 style="margin-bottom: 1.5rem; color: var(--text-primary); font-weight: 600;">
                📝 Input Your Text
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Text input options
        input_method = st.radio(
            "Choose your preferred input method:",
            ["✏️ Type/Paste Text", "📎 Upload Text File"],
            horizontal=True
        )
        
        input_text = ""
        
        if input_method == "✏️ Type/Paste Text":
            input_text = st.text_area(
                "Enter the text you want to summarize:",
                height=300,
                max_chars=MAX_TEXT_LENGTH,
                placeholder="Paste your long text here and watch the magic happen..."
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload a text file (.txt)",
                type=['txt'],
                help="Upload a .txt file to summarize"
            )
            
            if uploaded_file is not None:
                try:
                    input_text = str(uploaded_file.read(), "utf-8")
                    st.markdown(f'<div class="premium-success">📄 File uploaded successfully! ({len(input_text):,} characters)</div>', unsafe_allow_html=True)
                    
                    # Show preview
                    with st.expander("👀 Preview uploaded text"):
                        st.text(input_text[:500] + "..." if len(input_text) > 500 else input_text)
                        
                except Exception as e:
                    st.markdown(f'<div class="premium-error">❌ Error reading file: {str(e)}</div>', unsafe_allow_html=True)
        
        # Display character count with premium styling
        if input_text:
            char_count = len(input_text)
            if char_count <= MAX_TEXT_LENGTH:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: var(--bg-secondary); 
                border-radius: var(--border-radius); border: 1px solid var(--border-color); margin: 1rem 0;">
                    <span style="color: var(--text-secondary); font-weight: 500;">
                        Character count: <strong style="color: var(--accent-color);">{char_count:,}</strong>
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="premium-error">📏 Text is too long! Please limit to {MAX_TEXT_LENGTH:,} characters.</div>', unsafe_allow_html=True)
        
        # Premium Summarize button
        summarize_button = st.button(
            "🚀 Generate Summary",
            type="primary",
            disabled=not input_text or len(input_text.strip()) < 10 or min_length >= max_length,
            use_container_width=True
        )
    
    with col2:
        st.markdown("""
        <div class="output-card">
            <h3 style="margin-bottom: 1.5rem; color: var(--text-primary); font-weight: 600;">
                ✨ Summary Output
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        if summarize_button and input_text:
            if len(input_text.strip()) < 10:
                st.markdown('<div class="premium-error">⚠️ Please provide at least 10 characters of text to summarize.</div>', unsafe_allow_html=True)
            elif min_length >= max_length:
                st.markdown('<div class="premium-error">⚠️ Please fix the summary length parameters in the sidebar.</div>', unsafe_allow_html=True)
            else:
                # Show premium progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Update progress with premium messaging
                    progress_bar.progress(25)
                    status_text.markdown("🔗 Connecting to AI backend...")
                    
                    # Perform summarization
                    progress_bar.progress(50)
                    status_text.markdown("🧠 AI is analyzing your text...")
                    
                    progress_bar.progress(75)
                    status_text.markdown("✨ Generating intelligent summary...")
                    
                    result = run_async(client.summarize(input_text, max_length, min_length))
                    
                    progress_bar.progress(100)
                    status_text.markdown("🎉 Summary complete!")
                    
                    # Hide progress indicators
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                    if result["status"] == "success":
                        data = result["data"]
                        summary = data["summary"]
                        
                        # Display summary in premium card
                        st.markdown(f"""
                        <div class="premium-summary-card">
                            <h4>📋 AI-Generated Summary</h4>
                            <div class="summary-text">
                                {summary}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display premium statistics
                        display_statistics(
                            data["original_length"],
                            data["summary_length"],
                            data["model_used"]
                        )
                        
                        # Premium download button
                        download_link = create_download_link(summary)
                        st.markdown(f"""
                        <div style="text-align: center; margin: 2rem 0;">
                            {download_link}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Store in session state for persistence
                        st.session_state["last_summary"] = summary
                        st.session_state["last_stats"] = data
                        
                    else:
                        st.markdown(f'<div class="premium-error">❌ Error: {result["message"]}</div>', unsafe_allow_html=True)
                        
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.markdown(f'<div class="premium-error">❌ Unexpected error: {str(e)}</div>', unsafe_allow_html=True)
        
        # Show last summary if available
        elif "last_summary" in st.session_state:
            st.markdown('<div class="premium-success">💾 Previous summary available (click "Generate Summary" for a new one)</div>', unsafe_allow_html=True)
            
            summary = st.session_state["last_summary"]
            stats = st.session_state["last_stats"]
            
            st.markdown(f"""
            <div class="premium-summary-card">
                <h4>📋 Previous Summary</h4>
                <div class="summary-text">
                    {summary}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            display_statistics(
                stats["original_length"],
                stats["summary_length"],
                stats["model_used"]
            )
            
            download_link = create_download_link(summary)
            st.markdown(f"""
            <div style="text-align: center; margin: 2rem 0;">
                {download_link}
            </div>
            """, unsafe_allow_html=True)
    
    # Premium Footer
    st.markdown("""
    <div class="premium-footer">
        <div class="footer-content">
            <h4 style="color: var(--text-primary); margin-bottom: 1rem;">🤖 Powered by Advanced AI Technology</h4>
            <p>This application uses state-of-the-art BART (Bidirectional and Auto-Regressive Transformers) 
            models to provide intelligent, contextual text summarization.</p>
            <div class="footer-links">
                <a href="https://github.com/jatin123123" target="_blank">🔗 GitHub</a>
                <a href="mailto:contact@jatinjangid.com">📧 Contact</a>
                <a href="#" onclick="window.location.reload()">🔄 Refresh</a>
            </div>
        </div>
        <div style="margin-top: 2rem; font-size: 0.9rem; opacity: 0.7;">
            <em>💡 Tip: For optimal results, use well-structured text with clear paragraphs and complete sentences.</em>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
