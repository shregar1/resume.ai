"""Parser Agent for extracting structured data from CVs."""

import json
import uuid
from typing import Dict, Any
import pdfplumber
from docx import Document

from services.agents.base_agent import BaseAgent

from start_utils import llm, embedding_llm

from utilities.llm_client import LLMClientUtility
from utilities.helpers import clean_text


class ParserAgent(BaseAgent):
    """Agent responsible for parsing CVs and extracting structured data."""
    
    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ):
        """Initialize the Parser Agent."""
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
        )
        self.llm_client = LLMClientUtility(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            conversational_llm_model=llm,
            embedding_llm_model=embedding_llm,
        )
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a CV file and extract structured data.
        
        Args:
            data: Dictionary containing:
                - file_path: Path to CV file
                - file_type: Type of file (pdf, docx, txt)
                
        Returns:
            Dictionary containing parsed CV data
        """
        try:
            file_path = data.get("file_path")
            file_type = data.get("file_type", "").lower()
            
            if not file_path:
                raise ValueError("file_path is required")
            
            # Extract text from file
            text = await self._extract_text(file_path, file_type)
            
            # Parse text using LLM
            cv_data = await self._parse_with_llm(text)
            
            # Add metadata
            cv_data["metadata"] = {
                "file_path": file_path,
                "file_type": file_type,
                "parser_version": "1.0"
            }
            
            return {
                "success": True,
                "cv_data": cv_data
            }
        
        except Exception as e:
            return await self.handle_error(e, data)
    
    async def _extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from CV file.
        
        Args:
            file_path: Path to file
            file_type: Type of file
            
        Returns:
            Extracted text
        """
        try:
            if file_type == "pdf" or file_path.endswith(".pdf"):
                return self._extract_from_pdf(file_path)
            elif file_type == "docx" or file_path.endswith(".docx"):
                return self._extract_from_docx(file_path)
            elif file_type == "txt" or file_path.endswith(".txt"):
                return self._extract_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        
        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            raise
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return clean_text(text)
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file.
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Extracted text
        """
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return clean_text(text)
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file.
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            Extracted text
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return clean_text(text)
    
    async def _parse_with_llm(self, text: str) -> Dict[str, Any]:
        """Parse CV text using LLM.
        
        Args:
            text: CV text
            
        Returns:
            Structured CV data
        """
        system_prompt = """You are an expert CV parser. Extract structured information from the CV text.
Return a JSON object with the following structure:
{
  "candidate": {
    "name": "",
    "email": "",
    "phone": "",
    "location": "",
    "linkedin": ""
  },
  "summary": "",
  "experience": [
    {
      "company": "",
      "role": "",
      "start_date": "",
      "end_date": "",
      "description": "",
      "key_achievements": [],
      "technologies": []
    }
  ],
  "education": [
    {
      "institution": "",
      "degree": "",
      "field": "",
      "graduation_year": null
    }
  ],
  "skills": {
    "technical": [],
    "soft": [],
    "tools": [],
    "languages": []
  },
  "certifications": [
    {
      "name": "",
      "issuer": "",
      "date": ""
    }
  ],
  "projects": [
    {
      "name": "",
      "description": "",
      "technologies": []
    }
  ]
}

Be thorough and extract all relevant information. Use null for missing dates/numbers."""

        user_prompt = f"""Parse the following CV and extract structured information:

{text}

Return ONLY valid JSON, no additional text."""

        try:
            response = await self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1
            )
            
            # Parse JSON response
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            cv_dict = json.loads(response)
            
            # Calculate total experience
            total_months = 0
            for exp in cv_dict.get("experience", []):
                duration = self._calculate_duration_months(
                    exp.get("start_date", ""),
                    exp.get("end_date")
                )
                exp["duration_months"] = duration
                total_months += duration
            
            cv_dict["total_experience_years"] = round(total_months / 12, 1)
            cv_dict["cv_id"] = str(uuid.uuid4())
            
            return cv_dict
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse LLM response as JSON: {e}")
            # Fallback to basic extraction
            return await self._fallback_parsing(text)
        except Exception as e:
            self.logger.error(f"Error in LLM parsing: {e}")
            return await self._fallback_parsing(text)
    
    async def _fallback_parsing(self, text: str) -> Dict[str, Any]:
        """Fallback parsing using regex when LLM fails.
        
        Args:
            text: CV text
            
        Returns:
            Basic structured data
        """
        return {
            "cv_id": str(uuid.uuid4()),
            "candidate": {
                "name": "",
                "email": self._extract_email(text) or "",
                "phone": self._extract_phone(text) or "",
                "location": "",
                "linkedin": ""
            },
            "summary": text[:500],
            "experience": [],
            "education": [],
            "skills": {
                "technical": [],
                "soft": [],
                "tools": [],
                "languages": []
            },
            "certifications": [],
            "projects": [],
            "total_experience_years": 0.0
        }

