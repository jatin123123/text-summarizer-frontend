# 🎨 Streamlit Frontend

Beautiful web interface for the AI Text Summarizer application.

## 🌟 Features

- **Modern UI**: Beautiful, responsive design
- **File Upload**: Support for .txt files
- **Real-time Processing**: Live connection to backend API
- **Parameter Controls**: Adjustable summary settings
- **Statistics Display**: Compression ratios and metrics
- **Download Results**: Save summaries as text files
- **Health Monitoring**: Backend status checking

## 🛠️ Technologies

- **Streamlit**: Modern Python web app framework
- **HTTPX**: Async HTTP client
- **Asyncio**: Asynchronous processing
- **Custom CSS**: Beautiful styling

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## 🔧 Configuration

The frontend connects to:
- **Backend API**: https://jatin12312-text-summarizer.hf.space
- **Theme**: Custom styling with modern design
- **Port**: 8501 (default)

## 📱 Features

### Input Methods
- Type/paste text directly
- Upload .txt files
- Character count validation

### Processing Controls
- Maximum summary length (30-500 tokens)
- Minimum summary length (10-100 tokens)
- Real-time parameter validation

### Output Features
- Formatted summary display
- Statistics (original/summary length, compression ratio)
- Model information
- Download as .txt file

## 🎯 Deployment

Ready for deployment on Streamlit Cloud:
- Repository: Connected to GitHub
- Main file: `app.py`
- Dependencies: Listed in `requirements.txt`
- Configuration: `.streamlit/config.toml`

## 🧪 Testing

Test these features after deployment:
1. Backend health check
2. Text summarization
3. File upload
4. Parameter adjustment
5. Download functionality
