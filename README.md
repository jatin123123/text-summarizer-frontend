# 🤖 AI Text Summarizer - Complete Application

A full-stack AI-powered text summarization application with FastAPI backend and Streamlit frontend.

## 🌟 Features

- **🧠 Advanced AI Summarization**: Uses Facebook's BART-large-CNN model
- **🎨 Beautiful Web Interface**: Modern Streamlit frontend
- **📤 File Upload Support**: Process .txt files directly
- **⚙️ Configurable Parameters**: Adjust summary length and quality
- **📊 Real-time Statistics**: View compression ratios and performance metrics
- **☁️ Cloud Deployed**: Backend on Hugging Face Spaces, Frontend on Streamlit Cloud

## 🏗️ Architecture

```
Frontend (Streamlit)           Backend (FastAPI)
┌─────────────────────┐       ┌──────────────────────┐
│  Web Interface      │──────▶│  BART Model          │
│  File Upload        │       │  Text Processing     │
│  Parameter Controls │       │  API Endpoints       │
│  Results Display    │       │  Docker Container    │
└─────────────────────┘       └──────────────────────┘
```

## 📁 Project Structure

```
├── backend/                 # FastAPI Backend
│   ├── app.py              # Main FastAPI application
│   ├── summarizer.py       # Text summarization logic
│   ├── requirements.txt    # Backend dependencies
│   └── Dockerfile          # Container configuration
│
├── frontend/               # Streamlit Frontend
│   ├── app.py             # Main Streamlit application
│   ├── requirements.txt   # Frontend dependencies
│   └── .streamlit/        # Streamlit configuration
│       └── config.toml
│
└── docs/                  # Documentation
    ├── DEPLOYMENT.md      # Deployment instructions
    └── API.md            # API documentation
```

## 🚀 Deployment Status

### ✅ Backend (Deployed)
- **Platform**: Hugging Face Spaces
- **URL**: https://jatin12312-text-summarizer.hf.space
- **Status**: Live and running
- **API Docs**: https://jatin12312-text-summarizer.hf.space/docs

### 🔄 Frontend (Ready to Deploy)
- **Platform**: Streamlit Cloud
- **Repository**: This repository
- **Status**: Ready for deployment

## 🛠️ Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

### Frontend
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

## 📚 API Endpoints

- `POST /summarize` - Summarize text
- `GET /health` - Health check
- `GET /` - API information
- `GET /docs` - Interactive documentation

## 🔧 Technologies Used

- **Backend**: FastAPI, PyTorch, Transformers, Uvicorn
- **Frontend**: Streamlit, HTTPX, AsyncIO
- **AI Model**: Facebook BART-large-CNN
- **Deployment**: Docker, Hugging Face Spaces, Streamlit Cloud

## 📖 Usage

1. **Text Input**: Type or upload text files
2. **Configure**: Set summary parameters
3. **Process**: Generate AI-powered summaries
4. **Download**: Save results as text files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the Apache License 2.0.

## 👨‍💻 Author

**Jatin Jangid**
- GitHub: [@Jatin12312](https://github.com/Jatin12312)

---

🌟 **Star this repository if you find it helpful!**
