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
    /* Global */
    body {
        font-family: 'Inter', sans-serif;
        background: #f9fafb;
        color: #1f2937;
    }
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 1.5rem;
        color: #4f46e5 !important;
        text-shadow: 2px 2px 4px rgba(79, 70, 229, 0.3);
        background: linear-gradient(90deg, #4f46e5 0%, #9333ea 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        /* Fallback for browsers that don't support gradient text */
    }
    .summary-card {
        background-color: #ffffff;
        padding: 1.8rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        margin: 1.2rem 0;
        font-size: 1.05rem;
        line-height: 1.6;
        color: #111827;
    }
    .summary-card h4 {
        margin-bottom: 0.8rem;
        color: #4f46e5;
    }
    .stats-container {
        display: flex;
        justify-content: space-evenly;
        margin: 1.2rem 0;
        gap: 1rem;
    }
    .stat-box {
        background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #e5e7eb;
        min-width: 140px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.05);
    }
    .stat-box h4 {
        font-size: 1rem;
        margin-bottom: 0.4rem;
        color: #374151;
    }
    .stat-box p {
        font-size: 1.1rem;
        font-weight: 600;
        color: #111827;
    }
    .error-message {
        background-color: #fef2f2;
        color: #b91c1c;
        padding: 1rem;
        border-radius: 10px;
        border-left: 6px solid #ef4444;
        font-weight: 500;
    }
    .success-message {
        background-color: #ecfdf5;
        color: #065f46;
        padding: 1rem;
        border-radius: 10px;
        border-left: 6px solid #10b981;
        font-weight: 500;
    }
    a {
        text-decoration: none;
        color: #2563eb;
        font-weight: 600;
    }
    a:hover {
        color: #1e40af;
    }
    /* Footer */
    .footer {
        text-align: center;
        color: #6b7280;
        margin-top: 2rem;
        font-size: 0.9rem;
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
    <div class="stats-container">
        <div class="stat-box">
            <h4>Original Length</h4>
            <p><strong>{:,}</strong> characters</p>
        </div>
        <div class="stat-box">
            <h4>Summary Length</h4>
            <p><strong>{:,}</strong> characters</p>
        </div>
        <div class="stat-box">
            <h4>Compression</h4>
            <p><strong>{:.1f}%</strong> reduction</p>
        </div>
        <div class="stat-box">
            <h4>Model Used</h4>
            <p><strong>{}</strong></p>
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
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Text Summarizer</h1>', unsafe_allow_html=True)
    st.markdown("Transform lengthy documents into concise, meaningful summaries using advanced AI models.")
    
    # Initialize client
    client = SummarizerClient(BACKEND_URL)
    
    # Sidebar for settings and status
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Check backend health
        st.subheader("🔍 Backend Status")
        if st.button("Check Backend Status"):
            with st.spinner("Checking backend..."):
                health_result = run_async(client.check_health())
                
                if health_result["status"] == "healthy":
                    st.markdown('<div class="success-message">✅ Backend is healthy and ready!</div>', unsafe_allow_html=True)
                    if "data" in health_result:
                        model_info = health_result["data"].get("model_info", {})
                        st.json(model_info)
                else:
                    st.markdown(f'<div class="error-message">❌ Backend Error: {health_result["message"]}</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Summarization parameters
        st.subheader("📊 Summary Parameters")
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
            st.error("Minimum length must be less than maximum length!")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Input Text")
        
        # Text input options
        input_method = st.radio(
            "Choose input method:",
            ["Type/Paste Text", "Upload Text File"],
            horizontal=True
        )
        
        input_text = ""
        
        if input_method == "Type/Paste Text":
            input_text = st.text_area(
                "Enter the text you want to summarize:",
                height=300,
                max_chars=MAX_TEXT_LENGTH,
                placeholder="Paste your long text here..."
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload a text file",
                type=['txt'],
                help="Upload a .txt file to summarize"
            )
            
            if uploaded_file is not None:
                try:
                    input_text = str(uploaded_file.read(), "utf-8")
                    st.success(f"File uploaded successfully! ({len(input_text)} characters)")
                    
                    # Show preview
                    with st.expander("Preview uploaded text"):
                        st.text(input_text[:500] + "..." if len(input_text) > 500 else input_text)
                        
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        
        # Display character count
        if input_text:
            char_count = len(input_text)
            st.caption(f"Character count: {char_count:,}")
            
            if char_count > MAX_TEXT_LENGTH:
                st.error(f"Text is too long! Please limit to {MAX_TEXT_LENGTH:,} characters.")
        
        # Summarize button
        summarize_button = st.button(
            "🚀 Summarize Text",
            type="primary",
            disabled=not input_text or len(input_text.strip()) < 10 or min_length >= max_length,
            use_container_width=True
        )
    
    with col2:
        st.subheader("📄 Summary Output")
        
        if summarize_button and input_text:
            if len(input_text.strip()) < 10:
                st.error("Please provide at least 10 characters of text to summarize.")
            elif min_length >= max_length:
                st.error("Please fix the summary length parameters in the sidebar.")
            else:
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Update progress
                    progress_bar.progress(25)
                    status_text.text("Connecting to backend...")
                    
                    # Perform summarization
                    progress_bar.progress(50)
                    status_text.text("Generating summary...")
                    
                    result = run_async(client.summarize(input_text, max_length, min_length))
                    
                    progress_bar.progress(100)
                    status_text.text("Complete!")
                    
                    # Hide progress indicators
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
                    if result["status"] == "success":
                        data = result["data"]
                        summary = data["summary"]
                        
                        # Display summary in a card
                        st.markdown(f"""
                        <div class="summary-card">
                            <h4>📋 Generated Summary</h4>
                            <p>{summary}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display statistics
                        display_statistics(
                            data["original_length"],
                            data["summary_length"],
                            data["model_used"]
                        )
                        
                        # Download button
                        download_link = create_download_link(summary)
                        st.markdown(download_link, unsafe_allow_html=True)
                        
                        # Store in session state for persistence
                        st.session_state["last_summary"] = summary
                        st.session_state["last_stats"] = data
                        
                    else:
                        st.markdown(f'<div class="error-message">❌ Error: {result["message"]}</div>', unsafe_allow_html=True)
                        
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.markdown(f'<div class="error-message">❌ Unexpected error: {str(e)}</div>', unsafe_allow_html=True)
        
        # Show last summary if available
        elif "last_summary" in st.session_state:
            st.info("Previous summary (click 'Summarize Text' to generate a new one)")
            
            summary = st.session_state["last_summary"]
            stats = st.session_state["last_stats"]
            
            st.markdown(f"""
            <div class="summary-card">
                <h4>📋 Previous Summary</h4>
                <p>{summary}</p>
            </div>
            """, unsafe_allow_html=True)
            
            display_statistics(
                stats["original_length"],
                stats["summary_length"],
                stats["model_used"]
            )
            
            download_link = create_download_link(summary)
            st.markdown(download_link, unsafe_allow_html=True)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🤖 Powered by Jatin Jangid </p>
        <p><em>Tip: For best results, use well-structured text with clear paragraphs.</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
