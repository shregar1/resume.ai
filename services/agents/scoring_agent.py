"""Scoring Engine Agent for calculating candidate scores."""

from typing import Dict, Any, List

from services.agents.base_agent import BaseAgent


class ScoringAgent(BaseAgent):
    """Agent responsible for scoring candidates."""
    
    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ):
        """Initialize the Scoring Agent."""
        super().__init__(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
        )
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate scores for a candidate.
        
        Args:
            data: Dictionary containing:
                - cv_data: Parsed CV data
                - jd_data: Job description data
                - matches: Matching results
                
        Returns:
            Dictionary containing calculated scores
        """
        self.logger.info(f"Starting scoring for candidate: {data.get('cv_data', {}).get('cv_id', 'Unknown')}")
        try:
            cv_data = data.get("cv_data")
            jd_data = data.get("jd_data")
            matches = data.get("matches", {})
            
            if not cv_data or not jd_data:
                self.logger.error("cv_data and jd_data are required but not provided")
                raise ValueError("cv_data and jd_data are required")
            
            # Get scoring weights
            weights = jd_data.get("scoring_weights", {})
            self.logger.debug(f"Using scoring weights: {weights}")
            
            # Calculate individual scores
            self.logger.debug("Calculating skills score")
            skills_score = self._calculate_skills_score(matches)
            self.logger.debug(f"Skills score: {skills_score}")
            
            self.logger.debug("Calculating experience score")
            experience_score = self._calculate_experience_score(matches, cv_data, jd_data)
            self.logger.debug(f"Experience score: {experience_score}")
            
            self.logger.debug("Calculating education score")
            education_score = self._calculate_education_score(matches)
            self.logger.debug(f"Education score: {education_score}")
            
            self.logger.debug("Calculating career trajectory score")
            career_score = self._calculate_career_trajectory_score(cv_data)
            self.logger.debug(f"Career trajectory score: {career_score}")
            
            # Calculate total weighted score
            total_score = (
                weights.get("skills", 0.4) * skills_score +
                weights.get("experience", 0.3) * experience_score +
                weights.get("education", 0.15) * education_score +
                weights.get("career_trajectory", 0.1) * career_score
            )
            self.logger.info(f"Calculated total weighted score: {total_score}")
            
            # Calculate confidence
            confidence = self._calculate_confidence(matches, cv_data)
            self.logger.debug(f"Calculated confidence: {confidence}")
            
            # Create scores object
            scores = {
                "total": round(total_score, 2),
                "skills_match": round(skills_score, 2),
                "experience_relevance": round(experience_score, 2),
                "education_fit": round(education_score, 2),
                "career_trajectory": round(career_score, 2),
                "confidence": round(confidence, 2)
            }
            
            # Generate strengths and weaknesses
            self.logger.debug("Identifying strengths and weaknesses")
            strengths, weaknesses = self._identify_strengths_weaknesses(
                cv_data, jd_data, matches, scores
            )
            self.logger.info(f"Found {len(strengths)} strengths and {len(weaknesses)} weaknesses")
            
            return {
                "success": True,
                "scores": scores,
                "strengths": strengths,
                "weaknesses": weaknesses
            }
        
        except Exception as e:
            self.logger.error(f"Failed to calculate scores: {str(e)}", exc_info=True)
            return await self.handle_error(e, data)
    
    def _calculate_skills_score(self, matches: Dict[str, Any]) -> float:
        """Calculate skills match score.
        
        Args:
            matches: Matching results
            
        Returns:
            Skills score (0-100)
        """
        skill_matches = matches.get("skill_matches", {})
        
        # Base score on must-have skills match percentage
        base_score = skill_matches.get("match_percentage", 0)
        
        # Bonus for nice-to-have skills
        nice_to_have = len(skill_matches.get("matched_nice_to_have", []))
        bonus = min(20, nice_to_have * 4)  # Up to 20 bonus points
        
        # Incorporate semantic score
        semantic_score = matches.get("semantic_score", 50)
        
        # Weighted combination
        final_score = (base_score * 0.6) + (semantic_score * 0.3) + bonus
        
        return min(100, max(0, final_score))
    
    def _calculate_experience_score(
        self,
        matches: Dict[str, Any],
        cv_data: Dict[str, Any],
        jd_data: Dict[str, Any]
    ) -> float:
        """Calculate experience relevance score.
        
        Args:
            matches: Matching results
            cv_data: CV data
            jd_data: Job description data
            
        Returns:
            Experience score (0-100)
        """
        exp_match = matches.get("experience_match", {})
        
        cv_years = exp_match.get("cv_years", 0)
        required_years = exp_match.get("required_years", 0)
        
        if required_years == 0:
            return 100
        
        if cv_years >= required_years:
            # Meet or exceed requirement
            if cv_years <= required_years * 1.5:
                # Good match
                return 100
            elif cv_years <= required_years * 2:
                # Slightly overqualified
                return 90
            else:
                # Significantly overqualified (may be issue)
                return 75
        else:
            # Below requirement
            ratio = cv_years / required_years
            return ratio * 70  # Max 70 if below requirement
    
    def _calculate_education_score(self, matches: Dict[str, Any]) -> float:
        """Calculate education fit score.
        
        Args:
            matches: Matching results
            
        Returns:
            Education score (0-100)
        """
        edu_match = matches.get("education_match", {})
        
        if not edu_match.get("has_education"):
            return 50  # No education info
        
        if edu_match.get("meets_requirement"):
            return 100
        
        # Has education but doesn't meet requirement
        return 70
    
    def _calculate_career_trajectory_score(self, cv_data: Dict[str, Any]) -> float:
        """Calculate career trajectory score.
        
        Args:
            cv_data: CV data
            
        Returns:
            Career trajectory score (0-100)
        """
        experiences = cv_data.get("experience", [])
        
        if len(experiences) < 2:
            return 75  # Not enough data
        
        score = 50  # Base score
        
        # Check for progression in roles
        roles = [exp.get("role", "").lower() for exp in experiences[:5]]
        
        # Simple heuristics for career progression
        senior_keywords = ["senior", "lead", "principal", "architect", "director", "manager", "head"]
        mid_keywords = ["engineer", "developer", "analyst", "consultant"]
        
        role_levels = []
        for role in roles:
            if any(kw in role for kw in senior_keywords):
                role_levels.append(3)
            elif any(kw in role for kw in mid_keywords):
                role_levels.append(2)
            else:
                role_levels.append(1)
        
        # Check if generally progressing
        if len(role_levels) >= 2:
            if role_levels[0] >= role_levels[-1]:
                # Progression or stable at senior level
                score = 85
            else:
                # Regression
                score = 60
        
        # Bonus for company diversity
        companies = set([exp.get("company", "") for exp in experiences[:5]])
        if 2 <= len(companies) <= 4:
            score += 10  # Good company diversity
        elif len(companies) > 4:
            score -= 5  # Job hopping
        
        return min(100, max(0, score))
    
    def _calculate_confidence(
        self,
        matches: Dict[str, Any],
        cv_data: Dict[str, Any]
    ) -> float:
        """Calculate confidence in the scoring.
        
        Args:
            matches: Matching results
            cv_data: CV data
            
        Returns:
            Confidence score (0-1)
        """
        confidence = 0.5  # Base confidence
        
        # Higher confidence if we have more data
        if cv_data.get("experience") and len(cv_data["experience"]) >= 2:
            confidence += 0.15
        
        if cv_data.get("education"):
            confidence += 0.1
        
        if cv_data.get("skills", {}).get("technical"):
            confidence += 0.15
        
        # Higher confidence if strong match on must-have skills
        skill_matches = matches.get("skill_matches", {})
        if skill_matches.get("match_percentage", 0) > 80:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _identify_strengths_weaknesses(
        self,
        cv_data: Dict[str, Any],
        jd_data: Dict[str, Any],
        matches: Dict[str, Any],
        scores: Dict[str, float]
    ) -> tuple[List[str], List[str]]:
        """Identify candidate strengths and weaknesses.
        
        Args:
            cv_data: CV data
            jd_data: Job description data
            matches: Matching results
            scores: Calculated scores
            
        Returns:
            Tuple of (strengths, weaknesses)
        """
        strengths = []
        weaknesses = []
        
        # Analyze skills
        skill_matches = matches.get("skill_matches", {})
        matched_must_have = skill_matches.get("matched_must_have", [])
        missing_must_have = skill_matches.get("missing_must_have", [])
        matched_nice_to_have = skill_matches.get("matched_nice_to_have", [])
        
        if len(matched_must_have) >= 3:
            top_skills = [s["skill"] for s in matched_must_have[:3]]
            strengths.append(f"Strong match on required skills: {', '.join(top_skills)}")
        
        if matched_nice_to_have:
            strengths.append(f"Has {len(matched_nice_to_have)} additional desired skills")
        
        if missing_must_have:
            weaknesses.append(f"Missing required skills: {', '.join(missing_must_have[:3])}")
        
        # Analyze experience
        exp_match = matches.get("experience_match", {})
        cv_years = exp_match.get("cv_years", 0)
        required_years = exp_match.get("required_years", 0)
        
        if cv_years > required_years * 1.2:
            strengths.append(f"{cv_years} years of experience (exceeds requirement)")
        elif cv_years < required_years:
            weaknesses.append(f"Only {cv_years} years experience (requires {required_years})")
        
        # Analyze education
        edu_match = matches.get("education_match", {})
        if edu_match.get("meets_requirement"):
            if edu_match.get("highest_degree"):
                strengths.append(f"Has {edu_match['highest_degree']} degree")
        else:
            weaknesses.append("Education level below requirement")
        
        # Career trajectory
        if scores.get("career_trajectory", 0) >= 85:
            strengths.append("Strong career progression")
        elif scores.get("career_trajectory", 0) < 60:
            weaknesses.append("Limited career progression")
        
        return strengths[:5], weaknesses[:5]  # Limit to top 5 each

