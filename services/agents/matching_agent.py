"""Matching Agent for semantic CV-JD matching."""

from typing import Dict, Any, List
import numpy as np

from services.agents.base_agent import BaseAgent
from utilities.llm_client import LLMClientUtility
from utilities.helpers import normalize_skill

from start_utils import CONVERSATIONAL_LLM_MODEL, EMBEDDING_LLM_MODEL


class MatchingAgent(BaseAgent):
    """Agent responsible for matching CVs with job requirements."""
    
    def __init__(self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ):
        """Initialize the Matching Agent."""
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
            conversational_llm_model=CONVERSATIONAL_LLM_MODEL,
            embedding_llm_model=EMBEDDING_LLM_MODEL,
        )
        self.logger.info("MatchingAgent initialized")

    @property
    def llm_client(self):
        return self._llm_client
    
    @llm_client.setter
    def llm_client(self, value):
        self._llm_client = value

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Match a CV against job requirements.
        
        Args:
            data: Dictionary containing:
                - cv_data: Parsed CV data
                - jd_data: Analyzed job description data
                - jd_embeddings: JD embeddings for semantic matching
                
        Returns:
            Dictionary containing match results
        """
        try:
            cv_data = data.get("cv_data")
            jd_data = data.get("jd_data")
            jd_embeddings = data.get("jd_embeddings", {})
            
            if not cv_data or not jd_data:
                raise ValueError("cv_data and jd_data are required")
            
            # Perform skill matching
            skill_matches = await self._match_skills(cv_data, jd_data)
            
            # Perform semantic matching
            semantic_score = await self._semantic_match(cv_data, jd_data, jd_embeddings)
            
            # Match experience
            experience_match = self._match_experience(cv_data, jd_data)
            
            # Match education
            education_match = self._match_education(cv_data, jd_data)
            
            return {
                "success": True,
                "matches": {
                    "skill_matches": skill_matches,
                    "semantic_score": semantic_score,
                    "experience_match": experience_match,
                    "education_match": education_match
                }
            }
        
        except Exception as e:
            return await self.handle_error(e, data)
    
    async def _match_skills(
        self,
        cv_data: Dict[str, Any],
        jd_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Match skills between CV and JD.
        
        Args:
            cv_data: CV data
            jd_data: Job description data
            
        Returns:
            Skill matching results
        """
        # Extract CV skills
        cv_skills = set()
        skills_section = cv_data.get("skills", {})
        for skill_category in ["technical", "tools", "soft", "languages"]:
            cv_skills.update([normalize_skill(s) for s in skills_section.get(skill_category, [])])
        
        # Also extract from experience
        for exp in cv_data.get("experience", []):
            cv_skills.update([normalize_skill(s) for s in exp.get("technologies", [])])
        
        # Extract JD required skills
        requirements = jd_data.get("requirements", {})
        must_have = requirements.get("must_have_skills", [])
        nice_to_have = requirements.get("nice_to_have_skills", [])
        
        matched_must_have = []
        missing_must_have = []
        matched_nice_to_have = []
        
        # Match must-have skills
        for skill_req in must_have:
            skill = normalize_skill(skill_req.get("skill", ""))
            weight = skill_req.get("weight", 1.0)
            
            if skill in cv_skills or await self._is_similar_skill(skill, cv_skills):
                matched_must_have.append({
                    "skill": skill_req.get("skill", ""),
                    "weight": weight,
                    "match_score": 100
                })
            else:
                missing_must_have.append(skill_req.get("skill", ""))
        
        # Match nice-to-have skills
        for skill_req in nice_to_have:
            skill = normalize_skill(skill_req.get("skill", ""))
            weight = skill_req.get("weight", 0.5)
            
            if skill in cv_skills or await self._is_similar_skill(skill, cv_skills):
                matched_nice_to_have.append({
                    "skill": skill_req.get("skill", ""),
                    "weight": weight,
                    "match_score": 80
                })
        
        # Find extra skills
        jd_skills = set([normalize_skill(s.get("skill", "")) for s in must_have + nice_to_have])
        extra_skills = list(cv_skills - jd_skills)[:10]  # Limit to top 10
        
        # Calculate match percentage
        total_must_have = len(must_have)
        matched_count = len(matched_must_have)
        match_percentage = (matched_count / total_must_have * 100) if total_must_have > 0 else 0
        
        return {
            "matched_must_have": matched_must_have,
            "missing_must_have": missing_must_have,
            "matched_nice_to_have": matched_nice_to_have,
            "extra_skills": extra_skills,
            "match_percentage": match_percentage
        }
    
    async def _is_similar_skill(self, target_skill: str, cv_skills: set) -> bool:
        """Check if target skill is similar to any CV skill.
        
        Args:
            target_skill: Skill to check
            cv_skills: Set of CV skills
            
        Returns:
            True if similar skill found
        """
        # Simple similarity check (could be enhanced with embeddings)
        target_parts = set(target_skill.split())
        for cv_skill in cv_skills:
            cv_parts = set(cv_skill.split())
            overlap = len(target_parts & cv_parts)
            if overlap > 0 and overlap / len(target_parts) > 0.5:
                return True
        return False
    
    async def _semantic_match(
        self,
        cv_data: Dict[str, Any],
        jd_data: Dict[str, Any],
        jd_embeddings: Dict[str, List[float]]
    ) -> float:
        """Perform semantic matching using embeddings.
        
        Args:
            cv_data: CV data
            jd_data: Job description data
            jd_embeddings: JD embeddings
            
        Returns:
            Semantic similarity score (0-100)
        """
        try:
            # Create CV summary for embedding
            cv_summary = self._create_cv_summary(cv_data)
            
            # Generate CV embedding
            cv_embedding = await self.llm_client.generate_embeddings([cv_summary])
            
            if not cv_embedding or not jd_embeddings.get("full_description"):
                return 50.0  # Default score
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(
                cv_embedding[0],
                jd_embeddings["full_description"]
            )
            
            # Convert to 0-100 scale
            return max(0, min(100, similarity * 100))
        
        except Exception as e:
            self.logger.error(f"Error in semantic matching: {e}")
            return 50.0
    
    def _create_cv_summary(self, cv_data: Dict[str, Any]) -> str:
        """Create a summary of CV for embedding.
        
        Args:
            cv_data: CV data
            
        Returns:
            CV summary text
        """
        parts = []
        
        # Add summary
        if cv_data.get("summary"):
            parts.append(cv_data["summary"])
        
        # Add skills
        skills_section = cv_data.get("skills", {})
        all_skills = []
        for category in ["technical", "tools"]:
            all_skills.extend(skills_section.get(category, []))
        if all_skills:
            parts.append(f"Skills: {', '.join(all_skills[:20])}")
        
        # Add recent experience
        experiences = cv_data.get("experience", [])[:2]
        for exp in experiences:
            parts.append(f"{exp.get('role')} at {exp.get('company')}: {exp.get('description', '')[:200]}")
        
        return " ".join(parts)[:2000]  # Limit length
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity (-1 to 1)
        """
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            self.logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def _match_experience(
        self,
        cv_data: Dict[str, Any],
        jd_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Match experience requirements.
        
        Args:
            cv_data: CV data
            jd_data: Job description data
            
        Returns:
            Experience match results
        """
        cv_years = cv_data.get("total_experience_years", 0)
        required_years = jd_data.get("requirements", {}).get("min_experience_years", 0)
        
        meets_requirement = cv_years >= required_years
        difference = cv_years - required_years
        
        return {
            "cv_years": cv_years,
            "required_years": required_years,
            "meets_requirement": meets_requirement,
            "difference_years": difference
        }
    
    def _match_education(
        self,
        cv_data: Dict[str, Any],
        jd_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Match education requirements.
        
        Args:
            cv_data: CV data
            jd_data: Job description data
            
        Returns:
            Education match results
        """
        education = cv_data.get("education", [])
        required_level = jd_data.get("requirements", {}).get("education_level", "").lower()
        
        has_education = len(education) > 0
        highest_degree = ""
        
        if education:
            # Simple logic to find highest degree
            degrees = [e.get("degree", "").lower() for e in education]
            if any("phd" in d or "doctorate" in d for d in degrees):
                highest_degree = "PhD"
            elif any("master" in d or "ms" in d or "mba" in d for d in degrees):
                highest_degree = "Master's"
            elif any("bachelor" in d or "bs" in d or "ba" in d for d in degrees):
                highest_degree = "Bachelor's"
            else:
                highest_degree = education[0].get("degree", "")
        
        meets_requirement = True  # Simple check
        if "master" in required_level and "bachelor" in highest_degree.lower():
            meets_requirement = False
        elif "phd" in required_level and "phd" not in highest_degree.lower():
            meets_requirement = False
        
        return {
            "has_education": has_education,
            "highest_degree": highest_degree,
            "required_level": required_level,
            "meets_requirement": meets_requirement
        }

