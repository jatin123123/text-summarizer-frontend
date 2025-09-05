import streamlit as st
import httpx
import asyncio
import time
from typing import Optional

# -----------------------------
# Simple, Classic Streamlit UI
# -----------------------------
# Replace this with your backend endpoint if needed
BACKEND_URL = "https://jatin12312-text-summarizer.hf.space"
MAX_TEXT_LENGTH = 50000

st.set_page_config(page_title="Text Summarizer", page_icon="📝", layout="wide")

# Minimal card-like CSS for a clean look
st.markdown(
    """
    <style>
    .card { background: #ffffff; border-radius: 10px; padding: 18px; box-shadow: 0 4px 18px rgba(20,20,20,0.06); }
    .muted { color: #6b7280; }
    .title-row { display:flex; align-items:center; gap:12px; }
    .small-note { font-size:0.9rem; color: #6b7280; }
    </style>
    """,
    unsafe_allow_html=True,
)


class SummarizerClient:
    """Minimal async client for talking to the backend."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def check_health(self) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{self.base_url}/health", timeout=8.0)
                if r.status_code == 200:
                    return {"ok": True, "data": r.json()}
                return {"ok": False, "error": f"Status {r.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def summarize(self, text: str, max_length: int = 150, min_length: int = 30) -> dict:
        payload = {"text": text, "max_length": max_length, "min_length": min_length}
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(f"{self.base_url}/summarize", json=payload, timeout=120.0)
                if r.status_code == 200:
                    return {"ok": True, "data": r.json()}
                try:
                    return {"ok": False, "error": r.json()}
                except Exception:
                    return {"ok": False, "error": r.text}
        except httpx.TimeoutException:
            return {"ok": False, "error": "Request timed out."}
        except Exception as e:
            return {"ok": False, "error": str(e)}


def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def show_stats(original_len: int, summary_len: int, model: Optional[str] = None):
    if original_len <= 0:
        return
    compression = (1 - (summary_len / original_len)) * 100
    c1, c2, c3 = st.columns(3)
    c1.metric("Original chars", f"{original_len:,}")
    c2.metric("Summary chars", f"{summary_len:,}")
    c3.metric("Compression", f"{compression:.1f}%")
    if model:
        st.caption(f"Model: {model}")


# -------
# Layout
# -------

st.markdown("""
<div class="card">
  <div class="title-row">
    <h2 style="margin:0">📝 Classic Text Summarizer</h2>
  </div>
  <p class="muted">Paste or upload long text and get a concise AI-powered summary. Clean, simple and fast.</p>
</div>
""", unsafe_allow_html=True)

client = SummarizerClient(BACKEND_URL)

with st.sidebar:
    st.header("Settings")
    max_len = st.slider("Max summary tokens", min_value=50, max_value=500, value=150, step=10)
    min_len = st.slider("Min summary tokens", min_value=10, max_value=100, value=30, step=5)

    st.markdown("---")
    st.write("Backend health")
    if st.button("Check backend"):
        with st.spinner("Checking..."):
            resp = run_async(client.check_health())
            if resp.get("ok"):
                st.success("Backend OK")
                st.json(resp.get("data"))
            else:
                st.error(f"Backend error: {resp.get('error')}")


col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("""
    <div class="card">
      <h4 style="margin-top:0">Input</h4>
      <p class="small-note">Type/paste text or upload a .txt file (max 50k chars)</p>
    </div>
    """, unsafe_allow_html=True)

    input_method = st.radio("Input method", ["Paste text", "Upload file"], horizontal=True)

    text = ""
    if input_method == "Paste text":
        text = st.text_area("Enter your text", height=300, max_chars=MAX_TEXT_LENGTH, placeholder="Paste long text here...")
    else:
        f = st.file_uploader("Upload a .txt file", type=["txt"])
        if f is not None:
            try:
                text = f.read().decode("utf-8")
                st.success(f"Loaded file — {len(text):,} characters")
                with st.expander("Preview"):
                    st.write(text[:1000] + ("..." if len(text) > 1000 else ""))
            except Exception as e:
                st.error(f"Could not read file: {e}")

    if text and len(text) > MAX_TEXT_LENGTH:
        st.error(f"Text too long. Please keep under {MAX_TEXT_LENGTH:,} characters")

    generate = st.button("Generate summary 🚀", disabled=(not text or len(text.strip()) < 10 or min_len >= max_len))

with col2:
    st.markdown("""
    <div class="card">
      <h4 style="margin-top:0">Summary</h4>
      <p class="small-note">AI-generated summary will appear here.</p>
    </div>
    """, unsafe_allow_html=True)

    output_area = st.empty()

    if "last_summary" in st.session_state and not generate:
        with output_area.container():
            st.success("Previous summary (use Generate to create a new one)")
            st.write(st.session_state.get("last_summary"))
            show_stats(
                st.session_state.get("last_stats", {}).get("original_length", 0),
                st.session_state.get("last_stats", {}).get("summary_length", 0),
                st.session_state.get("last_stats", {}).get("model_used"),
            )
            st.download_button("Download summary", data=st.session_state.get("last_summary"), file_name="summary.txt")

if generate:
    if not text or len(text.strip()) < 10:
        st.error("Please provide at least 10 characters to summarize.")
    elif min_len >= max_len:
        st.error("Min length must be less than max length.")
    else:
        with st.spinner("Contacting AI backend and generating summary..."):
            prog = st.progress(0)
            try:
                prog.progress(10)
                resp = run_async(client.summarize(text, max_length=max_len, min_length=min_len))
                prog.progress(60)
                time.sleep(0.2)
                prog.progress(90)

                if resp.get("ok"):
                    data = resp.get("data") or {}
                    summary = data.get("summary") or data.get("summary_text") or data.get("result") or ""
                    orig_len = data.get("original_length") or len(text)
                    summ_len = data.get("summary_length") or len(summary)
                    model_used = data.get("model_used") or data.get("model") or "unknown"

                    if not summary:
                        st.error("Backend responded but no summary was returned.")
                    else:
                        output_area.markdown("""
                        <div class="card">
                        <h4 style="margin-top:0">Your Summary</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        with output_area.container():
                            st.write(summary)
                            show_stats(orig_len, summ_len, model_used)
                            st.download_button("Download summary", data=summary, file_name="summary.txt")

                            st.session_state["last_summary"] = summary
                            st.session_state["last_stats"] = {
                                "original_length": orig_len,
                                "summary_length": summ_len,
                                "model_used": model_used,
                            }
                else:
                    err = resp.get("error")
                    st.error(f"Error from backend: {err}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
            finally:
                prog.empty()

st.markdown("---")
st.markdown("**Tip:** For best results, paste well-structured paragraphs with complete sentences.")
