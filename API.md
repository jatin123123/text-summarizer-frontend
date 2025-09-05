# 📚 API Documentation

## FastAPI Backend API Reference

**Base URL**: `https://jatin12312-text-summarizer.hf.space`

---

## 🔍 Endpoints

### 1. Root Endpoint
```http
GET /
```

**Description**: Get API information and available endpoints

**Response**:
```json
{
  "message": "🤖 Text Summarizer API",
  "version": "1.0.0",
  "description": "Powered by Hugging Face Transformers",
  "endpoints": {
    "POST /summarize": "Summarize text with customizable parameters",
    "GET /health": "Check API health and model status",
    "GET /docs": "Interactive API documentation"
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
```

---

### 2. Health Check
```http
GET /health
```

**Description**: Check API health and model status

**Response**:
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

**Error Response** (503):
```json
{
  "error": "Service unhealthy: Model not loaded"
}
```

---

### 3. Summarize Text
```http
POST /summarize
```

**Description**: Generate a summary of the provided text

**Request Body**:
```json
{
  "text": "string (required, min: 10 chars)",
  "max_length": "integer (optional, 30-500, default: 150)",
  "min_length": "integer (optional, 10-100, default: 30)"
}
```

**Example Request**:
```json
{
  "text": "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of intelligent agents: any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals. Colloquially, the term artificial intelligence is often used to describe machines that mimic cognitive functions that humans associate with the human mind, such as learning and problem solving.",
  "max_length": 100,
  "min_length": 30
}
```

**Success Response** (200):
```json
{
  "summary": "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. The term artificial intelligence is often used to describe machines that mimic cognitive functions.",
  "original_length": 456,
  "summary_length": 184,
  "model_used": "facebook/bart-large-cnn"
}
```

**Error Responses**:

**400 - Bad Request**:
```json
{
  "error": "Text cannot be empty or contain only whitespace"
}
```

**400 - Invalid Parameters**:
```json
{
  "error": "min_length must be less than max_length"
}
```

**503 - Service Unavailable**:
```json
{
  "error": "Summarizer model not loaded. Please try again later."
}
```

**500 - Internal Server Error**:
```json
{
  "error": "Internal server error: [error details]"
}
```

---

## 📋 Request/Response Models

### SummarizeRequest
```typescript
{
  text: string;        // Required, min 10 characters
  max_length: number;  // Optional, 30-500, default: 150
  min_length: number;  // Optional, 10-100, default: 30
}
```

### SummarizeResponse
```typescript
{
  summary: string;          // Generated summary text
  original_length: number;  // Character count of input
  summary_length: number;   // Character count of summary
  model_used: string;       // Model name used
}
```

### HealthResponse
```typescript
{
  status: string;           // "healthy" or "unhealthy"
  model_info: {
    model_name: string;
    device: string;
    max_chunk_length: number;
    model_loaded: boolean;
  }
}
```

---

## 🔧 Usage Examples

### Python (requests)
```python
import requests

# Health check
health = requests.get("https://jatin12312-text-summarizer.hf.space/health")
print(health.json())

# Summarize text
response = requests.post(
    "https://jatin12312-text-summarizer.hf.space/summarize",
    json={
        "text": "Your long text here...",
        "max_length": 150,
        "min_length": 30
    }
)
result = response.json()
print(result["summary"])
```

### JavaScript (fetch)
```javascript
// Health check
const health = await fetch("https://jatin12312-text-summarizer.hf.space/health");
const healthData = await health.json();
console.log(healthData);

// Summarize text
const response = await fetch("https://jatin12312-text-summarizer.hf.space/summarize", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    text: "Your long text here...",
    max_length: 150,
    min_length: 30
  })
});
const result = await response.json();
console.log(result.summary);
```

### cURL
```bash
# Health check
curl -X GET "https://jatin12312-text-summarizer.hf.space/health"

# Summarize text
curl -X POST "https://jatin12312-text-summarizer.hf.space/summarize" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Your long text here...",
       "max_length": 150,
       "min_length": 30
     }'
```

---

## ⚡ Performance Notes

- **First Request**: May take 2-3 minutes if model needs to load
- **Subsequent Requests**: Typically under 5 seconds
- **Text Length**: Automatically handles long texts through chunking
- **Rate Limiting**: Managed by Hugging Face Spaces
- **Timeout**: Requests timeout after 120 seconds

---

## 🛡️ Error Handling

The API provides comprehensive error handling:

1. **Input Validation**: Checks text length and parameter ranges
2. **Model Status**: Verifies model is loaded before processing
3. **Processing Errors**: Handles summarization failures gracefully
4. **HTTP Standards**: Uses appropriate HTTP status codes
5. **Detailed Messages**: Provides clear error descriptions

---

## 🌐 Interactive Documentation

Visit the auto-generated interactive API documentation:
- **Swagger UI**: https://jatin12312-text-summarizer.hf.space/docs
- **ReDoc**: https://jatin12312-text-summarizer.hf.space/redoc

These interfaces allow you to:
- Test API endpoints directly
- View request/response schemas
- Generate code samples
- Explore all available features
