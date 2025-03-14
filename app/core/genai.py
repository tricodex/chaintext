# mypy: ignore-errors
from typing import List, Optional, Dict, Any
from loguru import logger
import json
import hashlib

# Import Google Generative AI with proper error handling
try:
    from google import genai
    from google.genai import types  # Correct import path for March 2025
    GENAI_AVAILABLE = True
except ImportError:
    logger.error("Google Generative AI library not installed. Run: pip install google-genai")
    GENAI_AVAILABLE = False

from app.core.config import settings

# Configuration for Gemini models
MODEL_INFO = {
    "gemini-2.0-flash": {
        "description": "High throughput model with 1M token context window",
        "context_window": 1_000_000,
        "status": "experimental"
    },
    "text-embedding-004": {
        "description": "Embedding model for vector search",
        "context_window": 3072,
        "status": "stable"
    }
}

class GenAIClient:
    """Client for Google's Generative AI (Gemini) models"""
    
    def __init__(self):
        """Initialize the Gemini client with API key"""
        # Set up the API key
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not set. Gemini functionality will not work.")
            self.available = False
        elif not GENAI_AVAILABLE:
            logger.warning("Google Generative AI library not available. Gemini functionality will not work.")
            self.available = False
        else:
            # Initialize client
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                self.available = True
                logger.info("Initialized Gemini AI client successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini AI client: {e}")
                self.available = False
    
    async def generate_content(self, prompt: str, system_instruction: Optional[str] = None, model: str = "gemini-2.0-flash") -> Dict[str, Any]:
        """Generate content using Gemini models
        
        Following the official syntax:
        client.models.generate_content(model="gemini-2.0-flash", contents="prompt")
        
        Args:
            prompt: The input prompt or message
            system_instruction: Optional system instruction for context
            model: The Gemini model to use (default: gemini-2.0-flash for high throughput)
            
        Returns:
            Dictionary with generated text and success status
        """
        if not self.available:
            logger.warning("Gemini client not available. Returning error.")
            return {
                "text": "Gemini API not available. Please check your API key and installation.",
                "success": False
            }
            
        try:
            # Log model information
            model_context_window = MODEL_INFO.get(model, {}).get("context_window", 1_000_000)
            logger.debug(f"Using model {model} with {model_context_window} token context window")
            
            # Handle system instruction if provided
            if system_instruction:
                # This is the only valid syntax for system instructions as per official Gemini documentation
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
                response = self.client.models.generate_content(
                    model=model,
                    config=config,
                    contents=[prompt]  # Contents must be a list as per docs
                )
            else:
                # Basic content generation without system instruction
                response = self.client.models.generate_content(
                    model=model,
                    contents=[prompt]  # Contents must be a list as per docs
                )
            
            # Return the text response
            return {
                "text": response.text,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {e}")
            return {
                "text": f"Error: {str(e)}",
                "success": False
            }
    
    async def generate_structured_content(self, prompt: str, schema: Dict, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        """Generate structured content using Gemini with a schema in the prompt
        
        For Gemini, we supply a schema as text in the prompt as per the documentation
        """
        if not self.available:
            logger.warning("Gemini client not available. Returning error.")
            return {
                "data": None,
                "text": "Gemini API not available. Please check your API key and installation.",
                "success": False
            }
            
        try:
            # Add schema to the prompt as text
            schema_str = json.dumps(schema, indent=2)
            schema_prompt = f"""{prompt}\n\nUse this JSON schema:\n{schema_str}\nReturn a valid JSON that follows this schema."""
            
            # Generate content
            result = await self.generate_content(schema_prompt, system_instruction)
            
            if result["success"]:
                # Try to parse the response as JSON
                try:
                    # Extract JSON from the text if needed
                    text = result["text"]
                    
                    # Look for JSON block (in case there's extra text)
                    if "```json" in text:
                        json_text = text.split("```json")[1].split("```")[0].strip()
                        logger.debug("Found JSON code block with explicit json tag")
                    elif "```" in text:
                        json_text = text.split("```")[1].strip()
                        logger.debug("Found JSON in code block")
                    else:
                        # Try to extract JSON by looking for surrounding braces
                        start_idx = text.find('{')
                        end_idx = text.rfind('}') + 1
                        
                        if start_idx >= 0 and end_idx > start_idx:
                            json_text = text[start_idx:end_idx]
                            logger.debug("Extracted JSON using brace detection")
                        else:
                            json_text = text
                            logger.debug("Using raw text as JSON")
                    
                    parsed_json = json.loads(json_text)
                    return {
                        "data": parsed_json,
                        "text": result["text"],
                        "success": True
                    }
                except json.JSONDecodeError as je:
                    logger.error(f"Failed to parse JSON response: {je}")
                    return {
                        "data": None,
                        "text": result["text"],
                        "error": "Failed to parse JSON response",
                        "success": False
                    }
            else:
                return {
                    "data": None,
                    "text": result["text"],
                    "success": False
                }
        except Exception as e:
            logger.error(f"Error generating structured content: {e}")
            return {
                "data": None,
                "text": f"Error: {str(e)}",
                "success": False
            }
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text using Gemini embeddings
        
        Uses the syntax from the documentation:
        client.models.embed_content(model="text-embedding-004", contents="text")
        
        Args:
            text: The text to embed
            
        Returns:
            A list of embedding values as floats
        """
        if not self.available:
            logger.warning("Gemini client not available. Returning zero vector.")
            return [0.0] * 768
            
        try:
            logger.debug(f"Generating embeddings for text")
            
            # Use the syntax from the documentation
            result = self.client.models.embed_content(
                model="text-embedding-004",
                contents=text
            )
            
            # Process embedding result based on response format
            # Check if embeddings are in expected format
            if hasattr(result, "embeddings") and isinstance(result.embeddings, list):
                # Check if the embeddings list has values
                if len(result.embeddings) > 0:
                    embedding_obj = result.embeddings[0]
                    # Check if the embedding object has a values attribute
                    if hasattr(embedding_obj, "values"):
                        return embedding_obj.values
            
            # Alternative approach if the structure is different
            if hasattr(result, "embedding"):
                return result.embedding
                
            # Log issue and return zero vector if we can't extract embeddings
            logger.warning("Could not extract embeddings from response, returning zero vector")
            return [0.0] * 768
                
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            # Return a zero vector as fallback
            return [0.0] * 768

# Create a singleton instance
gemini_client = GenAIClient()