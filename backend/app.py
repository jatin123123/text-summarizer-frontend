from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import logging
import os
from summarizer import TextSummarizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Text Summarizer API",
    description="A powerful text summarization API using Hugging Face Transformers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global summarizer instance (loaded once at startup)
summarizer = None

# Pydantic models for request/response
class SummarizeRequest(BaseModel):
    text: str = Field(..., description="The text to summarize", min_length=10)
    max_length: int = Field(150, description="Maximum length of the summary", ge=30, le=500)
    min_length: int = Field(30, description="Minimum length of the summary", ge=10, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Your long text here that needs to be summarized. This should be at least a few sentences long to generate a meaningful summary. The summarizer works best with articles, news stories, research papers, or any substantial text content that contains multiple ideas or concepts that can be condensed into a shorter form.",
                "max_length": 150,
                "min_length": 30
            }
        }

class SummarizeResponse(BaseModel):
    summary: str = Field(..., description="The generated summary")
    original_length: int = Field(..., description="Length of the original text")
    summary_length: int = Field(..., description="Length of the summary")
    model_used: str = Field(..., description="Name of the model used for summarization")

class HealthResponse(BaseModel):
    status: str
    model_info: dict

class ErrorResponse(BaseModel):
    error: str
    detail: str

@app.on_event("startup")
async def startup_event():
    """Initialize the summarizer model on startup."""
    global summarizer
    try:
        logger.info("Starting up the Text Summarizer API...")
        logger.info("Loading summarization model...")
        
        # Use a smaller model for faster loading on Hugging Face Spaces
        model_name = os.getenv("MODEL_NAME", "facebook/bart-large-cnn")
        summarizer = TextSummarizer(model_name=model_name)
        
        logger.info("Model loaded successfully!")
        logger.info("Application startup complete.")
        
    except Exception as e:
        logger.error(f"Failed to load model during startup: {str(e)}")
        # Continue startup but log the error
        logger.warning("Application started without model - health checks will fail")

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "🤖 Text Summarizer API",
        "version": "1.0.0",
        "description": "Powered by Hugging Face Transformers",
        "endpoints": {
            "POST /summarize": "Summarize text with customizable parameters",
            "GET /health": "Check API health and model status",
            "GET /docs": "Interactive API documentation",
            "GET /redoc": "Alternative API documentation"
        },
        "example_usage": {
            "url": "/summarize",
            "method": "POST",
            "body": {
                "text": "Your text to summarize...",
                "max_length": 150,
                "min_length": 30
            }
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify the API and model status."""
    global summarizer
    
    try:
        if summarizer is None:
            raise HTTPException(
                status_code=503, 
                detail="Summarizer model not loaded"
            )
        
        model_info = summarizer.get_model_info()
        
        return HealthResponse(
            status="healthy",
            model_info=model_info
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    """
    Summarize the provided text using the loaded model.
    
    - **text**: The input text to summarize (minimum 10 characters)
    - **max_length**: Maximum length of the summary (30-500, default: 150)
    - **min_length**: Minimum length of the summary (10-100, default: 30)
    
    Returns a JSON response with the summary and metadata.
    """
    global summarizer
    
    try:
        # Validate that summarizer is loaded
        if summarizer is None:
            logger.error("Summarizer not initialized")
            raise HTTPException(
                status_code=503, 
                detail="Summarizer model not loaded. Please try again later."
            )
        
        # Validate input
        if not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty or contain only whitespace"
            )
        
        if request.min_length >= request.max_length:
            raise HTTPException(
                status_code=400,
                detail="min_length must be less than max_length"
            )
        
        # Log the request
        logger.info(f"Summarization request received - Text length: {len(request.text)} characters")
        
        # Perform summarization
        summary = summarizer.summarize(
            text=request.text,
            max_length=request.max_length,
            min_length=request.min_length
        )
        
        # Validate output
        if not summary or summary.startswith("Error"):
            logger.error(f"Summarization failed: {summary}")
            raise HTTPException(
                status_code=500,
                detail=f"Summarization failed: {summary}"
            )
        
        # Prepare response
        response = SummarizeResponse(
            summary=summary,
            original_length=len(request.text),
            summary_length=len(summary),
            model_used=summarizer.model_name
        )
        
        logger.info(f"Summarization completed - Summary length: {len(summary)} characters")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error during summarization: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler for unexpected errors."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "error": "Internal server error",
        "detail": str(exc)
    }

if __name__ == "__main__":
    # Run the application
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Set to False for production
        log_level="info"
    )
