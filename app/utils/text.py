"""Text processing utilities for ChainContext"""
import re
from typing import List, Optional


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and normalizing
    
    Args:
        text: The text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
        
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
    
    return text.strip()


def split_text(text: str, max_chunk_size: int = 1024, overlap: int = 200) -> List[str]:
    """
    Split text into chunks with overlap
    
    Args:
        text: The text to split
        max_chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
        
    if len(text) <= max_chunk_size:
        return [text]
    
    # Clean the text first
    text = clean_text(text)
    
    # Split the text into paragraphs
    paragraphs = [p for p in text.split('\n') if p.strip()]
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed the max size, 
        # finish the current chunk and start a new one
        if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Start new chunk with overlap from the end of the previous chunk
            current_chunk = current_chunk[-overlap:] if len(current_chunk) > overlap else ""
        
        # Add the paragraph to the current chunk
        if current_chunk:
            current_chunk += "\n\n" + paragraph
        else:
            current_chunk = paragraph
    
    # Add the final chunk if it's not empty
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text using simple frequency analysis
    Note: This is a simplified implementation for the hackathon
    
    Args:
        text: The text to extract keywords from
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        List of keywords
    """
    if not text:
        return []
        
    # Clean the text
    text = clean_text(text).lower()
    
    # Remove common stop words (simplified list)
    stop_words = {
        'the', 'and', 'is', 'of', 'to', 'in', 'that', 'it', 
        'with', 'for', 'as', 'be', 'on', 'not', 'this', 'by',
        'are', 'from', 'or', 'an', 'at', 'a', 'but', 'if', 'so'
    }
    
    # Split into words and remove stop words
    words = [word for word in re.findall(r'\b\w+\b', text) if word not in stop_words and len(word) > 2]
    
    # Count word frequencies
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, count in sorted_words[:max_keywords]]


def highlight_text(text: str, keywords: List[str], highlight_start: str = "<mark>", highlight_end: str = "</mark>") -> str:
    """
    Highlight keywords in text
    
    Args:
        text: The text to highlight keywords in
        keywords: List of keywords to highlight
        highlight_start: String to prepend to highlighted text
        highlight_end: String to append to highlighted text
        
    Returns:
        Text with keywords highlighted
    """
    if not text or not keywords:
        return text
        
    result = text
    pattern = r'\b({})\b'
    
    for keyword in keywords:
        regex = re.compile(pattern.format(re.escape(keyword)), re.IGNORECASE)
        result = regex.sub(f"{highlight_start}\\1{highlight_end}", result)
    
    return result


def summarize_text(text: str, max_length: int = 200) -> str:
    """
    Create a simple summary of text by truncating
    Note: In a real implementation, we would use an AI model for summarization
    
    Args:
        text: The text to summarize
        max_length: Maximum length of the summary
        
    Returns:
        Summarized text
    """
    if not text:
        return ""
        
    # Clean the text
    text = clean_text(text)
    
    if len(text) <= max_length:
        return text
    
    # Simple truncation with ellipsis
    return text[:max_length].rsplit(' ', 1)[0] + "..."
