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
        self.logger.info(f"Starting CV processing for file: {data.get('file_path')}")
        try:
            file_path = data.get("file_path")
            file_type = data.get("file_type", "").lower()
            
            if not file_path:
                self.logger.error("file_path is required but not provided")
                raise ValueError("file_path is required")
            
            self.logger.debug(f"Processing file type: {file_type}")
            # Extract text from file
            text = await self._extract_text(file_path, file_type)
            self.logger.info(f"Successfully extracted {len(text)} characters from file")
            
            # Parse text using LLM
            cv_data = await self._parse_with_llm(text)
            self.logger.info("Successfully parsed CV data with LLM")
            
            # Add metadata
            cv_data["metadata"] = {
                "file_path": file_path,
                "file_type": file_type,
                "parser_version": "1.0"
            }
            
            self.logger.info(f"CV processing completed successfully. CV ID: {cv_data.get('cv_id')}")
            return {
                "success": True,
                "cv_data": cv_data
            }
        
        except Exception as e:
            self.logger.error(f"Failed to process CV: {str(e)}", exc_info=True)
            return await self.handle_error(e, data)
    
    async def _extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from CV file.
        
        Args:
            file_path: Path to file
            file_type: Type of file
            
        Returns:
            Extracted text
        """
        self.logger.debug(f"Extracting text from {file_type} file: {file_path}")
        try:
            if file_type == "pdf" or file_path.endswith(".pdf"):
                self.logger.debug("Using PDF extraction")
                return self._extract_from_pdf(file_path)
            else:
                self.logger.error(f"Unsupported file type: {file_type}")
                raise ValueError(f"Unsupported file type: {file_type}")
        
        except Exception as e:
            self.logger.error(f"Error extracting text from {file_path}: {e}", exc_info=True)
            raise
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        self.logger.debug(f"Opening PDF file: {file_path}")
        text = ""
        with pdfplumber.open(file_path) as pdf:
            self.logger.debug(f"PDF has {len(pdf.pages)} pages")
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    self.logger.debug(f"Extracted {len(page_text)} chars from page {page_num}")
        self.logger.info(f"Completed PDF extraction: {len(text)} total characters")
        return clean_text(text)

    async def _parse_with_llm(self, text: str) -> Dict[str, Any]:
        """Parse CV text using LLM.
        
        Args:
            text: CV text
            
        Returns:
            Structured CV data
        """
        self.logger.info(f"Starting LLM parsing for text of length {len(text)}")
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
            self.logger.debug("Sending request to LLM for CV parsing")
            response = await self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1
            )
            self.logger.debug(f"Received LLM response of length {len(response)}")
            
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
            self.logger.info("Successfully parsed LLM response as JSON")
            
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
            self.logger.info(f"Calculated total experience: {cv_dict['total_experience_years']} years")
            
            return cv_dict
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse LLM response as JSON: {e}", exc_info=True)
            self.logger.warning("Falling back to basic extraction")
            # Fallback to basic extraction
            return await self._fallback_parsing(text)
        except Exception as e:
            self.logger.error(f"Error in LLM parsing: {e}", exc_info=True)
            self.logger.warning("Falling back to basic extraction")
            return await self._fallback_parsing(text)
    
    async def _fallback_parsing(self, text: str) -> Dict[str, Any]:
        """Fallback parsing using regex when LLM fails.
        
        Args:
            text: CV text
            
        Returns:
            Basic structured data
        """
        self.logger.warning("Using fallback parsing - minimal data extraction")
        return {
            "cv_id": str(uuid.uuid4()),
            "candidate": {
                "name": "",
                "email": "",
                "phone": "",
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

