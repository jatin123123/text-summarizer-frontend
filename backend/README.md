# 🚀 FastAPI Backend

AI-powered text summarization backend using Facebook's BART model.

## 🌟 Features

- **Advanced AI Model**: Facebook BART-large-CNN
- **REST API**: FastAPI with automatic documentation
- **Text Chunking**: Handles long documents intelligently
- **Health Monitoring**: Real-time status endpoints
- **Docker Ready**: Containerized for easy deployment

## 🛠️ Technologies

- **FastAPI**: Modern Python web framework
- **PyTorch**: Deep learning framework
- **Transformers**: Hugging Face model library
- **Uvicorn**: ASGI server
- **Docker**: Containerization

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app:app --reload

# Visit API docs
open http://localhost:8000/docs
```

## 📡 API Endpoints

- `POST /summarize` - Summarize text
- `GET /health` - Health check
- `GET /` - API information
- `GET /docs` - Interactive documentation

## 🔧 Configuration

Environment variables:
- `MODEL_NAME`: AI model to use (default: facebook/bart-large-cnn)
- `PORT`: Server port (default: 7860)

## 🐳 Docker

```bash
# Build image
docker build -t text-summarizer-backend .

# Run container
docker run -p 7860:7860 text-summarizer-backend
```

## 📚 Model Information

- **Model**: facebook/bart-large-cnn
- **Task**: Text summarization
- **Language**: English
- **Max Input**: 1024 tokens per chunk
- **Output**: Variable length summaries

## 🔍 Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "model_info": {
    "model_name": "facebook/bart-large-cnn",
    "device": "cpu",
    "max_chunk_length": 1024,
    "model_loaded": true
  }
}
```

## 🎯 Deployment

This backend is deployed on Hugging Face Spaces:
- **URL**: https://jatin12312-text-summarizer.hf.space
- **Status**: Live and operational
- **Docs**: https://jatin12312-text-summarizer.hf.space/docs
