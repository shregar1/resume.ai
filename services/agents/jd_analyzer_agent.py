"""Job Description Analyzer Agent."""

import json
import uuid

from typing import Dict, Any, List

from services.agents.base_agent import BaseAgent

from start_utils import llm, embedding_llm

from utilities.llm_client import LLMClientUtility

class JDAnalyzerAgent(BaseAgent):
    """Agent responsible for analyzing job descriptions."""
    
    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ):
        """Initialize the JD Analyzer Agent."""
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id
        )
        self.llm_client = LLMClientUtility(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
            conversational_llm_model=llm,
            embedding_llm_model=embedding_llm,
        )
        self.logger.info("JDAnalyzerAgent initialized")
    
    @property
    def llm_client(self):
        return self._llm_client
    
    @llm_client.setter
    def llm_client(self, value):
        self._llm_client = value

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a job description and extract requirements.
        
        Args:
            data: Dictionary containing:
                - job_description: Job description text
                - job_title: Job title (optional)
                - company: Company name (optional)
                
        Returns:
            Dictionary containing analyzed JD data
        """
        self.logger.info(f"Starting JD analysis for job: {data.get('job_title', 'Unknown')}")
        try:
            jd_text = data.get("job_description")
            job_title = data.get("job_title", "")
            company = data.get("company", "")
            
            if not jd_text:
                self.logger.error("job_description is required but not provided")
                raise ValueError("job_description is required")
            
            self.logger.debug(f"Processing JD with {len(jd_text)} characters")
            # Analyze JD using LLM
            jd_data = await self._analyze_with_llm(jd_text, job_title, company)
            self.logger.info(f"Successfully analyzed JD. JD ID: {jd_data.get('jd_id')}")
            
            # Generate embeddings for semantic matching
            self.logger.debug("Generating embeddings for semantic matching")
            embeddings = await self._generate_embeddings(jd_data)
            self.logger.info("Successfully generated embeddings")
            
            return {
                "success": True,
                "jd_data": jd_data,
                "embeddings": embeddings
            }
        
        except Exception as e:
            self.logger.error(f"Failed to analyze JD: {str(e)}", exc_info=True)
            return await self.handle_error(e, data)
    
    async def _analyze_with_llm(
        self,
        jd_text: str,
        job_title: str,
        company: str
    ) -> Dict[str, Any]:
        """Analyze job description using LLM.
        
        Args:
            jd_text: Job description text
            job_title: Job title
            company: Company name
            
        Returns:
            Structured job description data
        """
        self.logger.info(f"Analyzing JD with LLM for {job_title} at {company}")
        system_prompt = """You are an expert recruiter analyzing job descriptions. Extract structured requirements.
Return a JSON object with the following structure:
{
  "job_title": "",
  "company": "",
  "department": "",
  "seniority_level": "junior|mid|senior|lead|executive",
  "requirements": {
    "must_have_skills": [
      {"skill": "Python", "weight": 0.9}
    ],
    "nice_to_have_skills": [
      {"skill": "Docker", "weight": 0.5}
    ],
    "min_experience_years": 5,
    "education_level": "Bachelor's degree",
    "industry_experience": ["Technology", "Finance"],
    "certifications": ["AWS Certified"]
  },
  "responsibilities": ["Build APIs", "Lead team"],
  "scoring_weights": {
    "skills": 0.4,
    "experience": 0.3,
    "education": 0.15,
    "career_trajectory": 0.1,
    "other": 0.05
  }
}

Assign weights to skills based on importance (0.0-1.0).
Adjust scoring_weights based on what matters most for this role."""

        user_prompt = f"""Analyze the following job description and extract structured requirements:

Job Title: {job_title}
Company: {company}

Job Description:
{jd_text}

Return ONLY valid JSON, no additional text."""

        try:
            self.logger.debug("Sending request to LLM for JD analysis")
            response = await self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1
            )
            self.logger.debug(f"Received LLM response of length {len(response)}")
            
            # Clean and parse JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            jd_dict = json.loads(response)
            jd_dict["jd_id"] = str(uuid.uuid4())
            jd_dict["full_description"] = jd_text
            self.logger.info(f"Successfully parsed JD data. Found {len(jd_dict.get('requirements', {}).get('must_have_skills', []))} must-have skills")
            
            return jd_dict
        
        except Exception as e:
            self.logger.error(f"Error analyzing JD with LLM: {e}", exc_info=True)
            self.logger.warning("Using fallback JD structure")
            # Fallback
            return {
                "jd_id": str(uuid.uuid4()),
                "job_title": job_title,
                "company": company,
                "department": "",
                "seniority_level": "mid",
                "requirements": {
                    "must_have_skills": [],
                    "nice_to_have_skills": [],
                    "min_experience_years": 0,
                    "education_level": "",
                    "industry_experience": [],
                    "certifications": []
                },
                "responsibilities": [],
                "scoring_weights": {
                    "skills": 0.4,
                    "experience": 0.3,
                    "education": 0.15,
                    "career_trajectory": 0.1,
                    "other": 0.05
                },
                "full_description": jd_text
            }
    
    async def _generate_embeddings(
        self,
        jd_data: Dict[str, Any]
    ) -> Dict[str, List[float]]:
        """Generate embeddings for semantic matching.
        
        Args:
            jd_data: Job description data
            
        Returns:
            Dictionary of embeddings
        """
        self.logger.debug("Generating embeddings for JD components")
        try:

            texts_to_embed = [
                jd_data.get("full_description", ""),
                " ".join([s["skill"] for s in jd_data.get("requirements", {}).get("must_have_skills", [])]),
                " ".join(jd_data.get("responsibilities", []))
            ]
            
            self.logger.debug(f"Generating embeddings for {len(texts_to_embed)} text components")
            embeddings_list = await self.llm_client.generate_embeddings(texts_to_embed)
            self.logger.info("Successfully generated all embeddings")
            
            return {
                "full_description": embeddings_list[0],
                "skills": embeddings_list[1],
                "responsibilities": embeddings_list[2]
            }
        
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {e}", exc_info=True)
            return {
                "full_description": [],
                "skills": [],
                "responsibilities": []
            }

