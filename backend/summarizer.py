import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextSummarizer:
    """
    A class to handle text summarization using Hugging Face transformers.
    Supports efficient model loading and text chunking for long documents.
    """
    
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        """
        Initialize the summarizer with a pre-trained model.
        
        Args:
            model_name (str): The name of the pre-trained model to use
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.max_chunk_length = 1024  # Maximum tokens per chunk
        self.load_model()
    
    def load_model(self):
        """Load the tokenizer and model."""
        try:
            logger.info(f"Loading model: {self.model_name}")
            logger.info(f"Using device: {self.device}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            
            logger.info("Model loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise RuntimeError(f"Failed to load model {self.model_name}: {str(e)}")
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split long text into chunks that fit within the model's token limit.
        
        Args:
            text (str): The input text to chunk
            
        Returns:
            List[str]: List of text chunks
        """
        if not text.strip():
            return []
        
        # Tokenize the full text to check length
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        
        if len(tokens) <= self.max_chunk_length:
            return [text]
        
        # Split text into sentences for better chunking
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Add period back except for the last sentence
            if not sentence.endswith('.'):
                sentence += '.'
            
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            test_tokens = self.tokenizer.encode(test_chunk, add_special_tokens=False)
            
            if len(test_tokens) <= self.max_chunk_length:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def summarize_chunk(self, text: str, max_length: int = 150, min_length: int = 30) -> str:
        """
        Summarize a single chunk of text.
        
        Args:
            text (str): The text chunk to summarize
            max_length (int): Maximum length of the summary
            min_length (int): Minimum length of the summary
            
        Returns:
            str: The summarized text
        """
        if not text.strip():
            return ""
        
        try:
            # Tokenize input text
            inputs = self.tokenizer.encode(
                text, 
                return_tensors="pt", 
                max_length=self.max_chunk_length, 
                truncation=True
            ).to(self.device)
            
            # Generate summary
            with torch.no_grad():
                summary_ids = self.model.generate(
                    inputs,
                    max_length=max_length,
                    min_length=min_length,
                    length_penalty=2.0,
                    num_beams=4,
                    early_stopping=True,
                    do_sample=False
                )
            
            # Decode the summary
            summary = self.tokenizer.decode(
                summary_ids[0], 
                skip_special_tokens=True
            )
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error summarizing chunk: {str(e)}")
            return f"Error summarizing this section: {str(e)}"
    
    def summarize(self, text: str, max_length: int = 150, min_length: int = 30) -> str:
        """
        Summarize the input text, handling long documents by chunking.
        
        Args:
            text (str): The input text to summarize
            max_length (int): Maximum length of each summary chunk
            min_length (int): Minimum length of each summary chunk
            
        Returns:
            str: The complete summarized text
        """
        if not text or not text.strip():
            return "No text provided for summarization."
        
        try:
            # Clean the input text
            text = text.strip()
            
            # Check if model is loaded
            if self.model is None or self.tokenizer is None:
                raise RuntimeError("Model not loaded properly")
            
            # Split text into chunks if necessary
            chunks = self.chunk_text(text)
            logger.info(f"Text split into {len(chunks)} chunks")
            
            # Summarize each chunk
            summaries = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Summarizing chunk {i+1}/{len(chunks)}")
                chunk_summary = self.summarize_chunk(chunk, max_length, min_length)
                if chunk_summary:
                    summaries.append(chunk_summary)
            
            # Combine summaries
            if not summaries:
                return "Unable to generate summary."
            
            # If we have multiple summaries, join them
            final_summary = " ".join(summaries)
            
            # If the combined summary is still very long, summarize it again
            if len(summaries) > 1:
                combined_tokens = self.tokenizer.encode(final_summary, add_special_tokens=False)
                if len(combined_tokens) > self.max_chunk_length:
                    logger.info("Final summary too long, creating final condensed summary")
                    final_summary = self.summarize_chunk(final_summary, max_length * 2, min_length)
            
            return final_summary
            
        except Exception as e:
            logger.error(f"Error in summarization: {str(e)}")
            return f"Error during summarization: {str(e)}"
    
    def get_model_info(self) -> dict:
        """
        Get information about the loaded model.
        
        Returns:
            dict: Model information
        """
        return {
            "model_name": self.model_name,
            "device": str(self.device),
            "max_chunk_length": self.max_chunk_length,
            "model_loaded": self.model is not None and self.tokenizer is not None
        }
