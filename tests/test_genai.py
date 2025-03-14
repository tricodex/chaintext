"""Tests for Gemini AI integration"""
import pytest
from unittest.mock import patch, MagicMock
import json

from app.core.genai import GenAIClient

@pytest.fixture
def mock_gemini_client():
    """Create a mock Gemini client for testing"""
    with patch('app.core.genai.genai.Client') as mock_client:
        # Create mock response for generate_content
        mock_response = MagicMock()
        mock_response.text = "This is a mock response"
        
        # Mock the models.generate_content method
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        
        # Mock the models object with the model
        mock_client_instance = MagicMock()
        mock_client_instance.models = MagicMock()
        mock_client_instance.models.generate_content.return_value = mock_response
        
        # Mock embedding
        mock_client_instance.models.embed_content.return_value = MagicMock(embedding=[0.1] * 768)
        
        # Return the mocked client
        mock_client.return_value = mock_client_instance
        yield GenAIClient()

@pytest.mark.asyncio
async def test_generate_content(mock_gemini_client):
    """Test generate_content method"""
    # Call the method
    result = await mock_gemini_client.generate_content("Test prompt")
    
    # Check the result
    assert result["success"] is True
    assert result["text"] == "This is a mock response"
    
    # Check that the model was called with correct parameters
    mock_gemini_client.client.models.generate_content.assert_called_once_with(
        model="gemini-2.0-flash",
        contents="Test prompt",
        config=None
    )

@pytest.mark.asyncio
async def test_generate_content_with_system_instruction(mock_gemini_client):
    """Test generate_content method with system instruction"""
    # Call the method with system instruction
    result = await mock_gemini_client.generate_content(
        "Test prompt", 
        system_instruction="Act as a helpful assistant"
    )
    
    # Check the result
    assert result["success"] is True
    
    # The system instruction should be passed to the model
    assert mock_gemini_client.client.models.generate_content.call_args[1]['config'] is not None

@pytest.mark.asyncio
async def test_generate_structured_content(mock_gemini_client):
    """Test generate_structured_content method"""
    # Mock the generate_content method to return a JSON response
    with patch.object(
        mock_gemini_client, 
        'generate_content', 
        return_value={"text": '{"answer": "Test answer", "confidence": 0.9}', "success": True}
    ):
        # Call the method
        schema = {"answer": "string", "confidence": "number"}
        result = await mock_gemini_client.generate_structured_content(
            "Test prompt", 
            schema
        )
        
        # Check the result
        assert result["success"] is True
        assert result["data"] == {"answer": "Test answer", "confidence": 0.9}

@pytest.mark.asyncio
async def test_embed_text(mock_gemini_client):
    """Test embed_text method"""
    # Call the method
    result = await mock_gemini_client.embed_text("Test text")
    
    # Check the result
    assert len(result) == 768
    assert result[0] == 0.1
    
    # Check that the model was called
    mock_gemini_client.client.models.embed_content.assert_called_once()
