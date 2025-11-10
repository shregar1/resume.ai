"""Utility functions for the application."""

import re
import logging
from typing import List, Optional
from datetime import datetime
from dateutil import parser as date_parser


logger = logging.getLogger(__name__)


def extract_email(text: str) -> Optional[str]:
    """Extract email address from text.
    
    Args:
        text: Input text
        
    Returns:
        Email address or None
    """
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text.
    
    Args:
        text: Input text
        
    Returns:
        Phone number or None
    """
    # Simple pattern for common phone formats
    pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text.
    
    Args:
        text: Input text
        
    Returns:
        List of URLs
    """
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(pattern, text)


def parse_date(date_str: str) -> Optional[str]:
    """Parse date string to ISO format.
    
    Args:
        date_str: Date string
        
    Returns:
        ISO formatted date or None
    """
    try:
        dt = date_parser.parse(date_str, fuzzy=True)
        return dt.isoformat()
    except Exception as e:
        logger.warning(f"Could not parse date: {date_str} - {e}")
        return None


def calculate_duration_months(start_date: str, end_date: Optional[str] = None) -> int:
    """Calculate duration in months between two dates.
    
    Args:
        start_date: Start date string
        end_date: End date string (None for present)
        
    Returns:
        Duration in months
    """
    try:
        start = date_parser.parse(start_date, fuzzy=True)
        end = datetime.now() if end_date is None or end_date.lower() in ["present", "current", "now"] else date_parser.parse(end_date, fuzzy=True)
        
        months = (end.year - start.year) * 12 + (end.month - start.month)
        return max(0, months)
    except Exception as e:
        logger.warning(f"Could not calculate duration: {e}")
        return 0


def normalize_skill(skill: str) -> str:
    """Normalize skill name.
    
    Args:
        skill: Skill name
        
    Returns:
        Normalized skill name
    """
    # Remove special characters and extra spaces
    skill = re.sub(r'[^\w\s.#+]', '', skill)
    skill = ' '.join(skill.split())
    return skill.strip().lower()


def extract_years_of_experience(text: str) -> float:
    """Extract years of experience from text.
    
    Args:
        text: Input text
        
    Returns:
        Years of experience
    """
    patterns = [
        r'(\d+\.?\d*)\+?\s*(?:years?|yrs?)',
        r'(\d+\.?\d*)\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        if matches:
            try:
                return float(matches[0])
            except ValueError:
                continue
    
    return 0.0


def clean_text(text: str) -> str:
    """Clean and normalize text.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,;:()\-]', '', text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks.
    
    Args:
        text: Input text
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    return chunks if chunks else [text]

