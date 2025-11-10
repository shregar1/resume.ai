"""Ranking Agent for creating final ranked candidate list."""

from typing import Dict, Any, List

from services.agents.base_agent import BaseAgent

from dtos.enitities.candidate.tier import CandidateTier

from start_utils import llm, embedding_llm

from utilities.llm_client import LLMClientUtility



class RankingAgent(BaseAgent):
    """Agent responsible for ranking candidates."""
    
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
        """Rank all candidates.
        
        Args:
            data: Dictionary containing:
                - candidate_scores: List of candidate score objects
                - jd_data: Job description data
                
        Returns:
            Dictionary containing ranked list
        """
        self.logger.info(f"Starting candidate ranking for {len(data.get('candidate_scores', []))} candidates")
        try:
            candidate_scores = data.get("candidate_scores", [])
            jd_data = data.get("jd_data", {})
            
            if not candidate_scores:
                self.logger.warning("No candidates to rank")
                return {
                    "success": True,
                    "ranked_candidates": []
                }
            
            # Apply filters
            self.logger.debug("Applying filters to candidates")
            filtered_candidates = self._apply_filters(candidate_scores, jd_data)
            self.logger.info(f"After filtering: {len(filtered_candidates)} candidates remain")
            
            # Sort by total score
            sorted_candidates = sorted(
                filtered_candidates,
                key=lambda x: x["scores"]["total"],
                reverse=True
            )
            self.logger.debug("Candidates sorted by total score")
            
            # Assign ranks and tiers
            self.logger.debug("Assigning ranks and tiers")
            ranked_candidates = self._assign_ranks_and_tiers(sorted_candidates)
            
            # Generate explanations
            self.logger.debug("Generating ranking explanations")
            for candidate in ranked_candidates:
                candidate["explanation"] = self._generate_explanation(candidate)
            
            tier_distribution = self._calculate_tier_distribution(ranked_candidates)
            self.logger.info(f"Ranking complete. Tier distribution: {tier_distribution}")
            
            return {
                "success": True,
                "ranked_candidates": ranked_candidates,
                "total_candidates": len(ranked_candidates),
                "tiers": tier_distribution
            }
        
        except Exception as e:
            self.logger.error(f"Failed to rank candidates: {str(e)}", exc_info=True)
            return await self.handle_error(e, data)
    
    def _apply_filters(
        self,
        candidates: List[Dict[str, Any]],
        jd_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply filtering rules to candidates.
        
        Args:
            candidates: List of candidate scores
            jd_data: Job description data
            
        Returns:
            Filtered candidate list
        """
        filtered = []
        
        for candidate in candidates:
            # Minimum score threshold
            if candidate["scores"]["total"] < 30:
                self.logger.info(f"Filtered out {candidate.get('candidate_name', 'Unknown')} - score too low")
                continue
            
            # Must have minimum required skills match
            skill_score = candidate["scores"]["skills_match"]
            if skill_score < 40:
                self.logger.info(f"Filtered out {candidate.get('candidate_name', 'Unknown')} - insufficient skills")
                continue
            
            # Check for critical missing requirements
            missing_skills = candidate.get("matches", {}).get("missing_skills", [])
            requirements = jd_data.get("requirements", {})
            critical_skills = [
                s["skill"] for s in requirements.get("must_have_skills", [])
                if s.get("weight", 0) >= 0.9
            ]
            
            has_critical_gaps = any(
                skill.lower() in [m.lower() for m in missing_skills]
                for skill in critical_skills
            )
            
            if has_critical_gaps and len(critical_skills) > 0:
                self.logger.info(f"Filtered out {candidate.get('candidate_name', 'Unknown')} - missing critical skills")
                continue
            
            filtered.append(candidate)
        
        return filtered
    
    def _assign_ranks_and_tiers(
        self,
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Assign ranks and tiers to candidates.
        
        Args:
            candidates: Sorted list of candidates
            
        Returns:
            Candidates with ranks and tiers
        """
        
        for i, candidate in enumerate(candidates):
            # Assign rank
            candidate["rank"] = i + 1
            
            # Assign tier based on score and position
            score = candidate["scores"]["total"]
            
            if score >= 85:
                candidate["tier"] = CandidateTier.A.value
            elif score >= 70:
                candidate["tier"] = CandidateTier.B.value
            elif score >= 55:
                candidate["tier"] = CandidateTier.C.value
            else:
                candidate["tier"] = CandidateTier.D.value
        
        return candidates
    
    def _generate_explanation(self, candidate: Dict[str, Any]) -> str:
        """Generate explanation for candidate ranking.
        
        Args:
            candidate: Candidate data
            
        Returns:
            Explanation text
        """
        parts = []
        
        scores = candidate.get("scores", {})
        total = scores.get("total", 0)
        
        # Overall assessment
        if total >= 85:
            parts.append("Excellent match for this position.")
        elif total >= 70:
            parts.append("Strong candidate with good potential.")
        elif total >= 55:
            parts.append("Decent fit with some gaps.")
        else:
            parts.append("Marginal fit for the role.")
        
        # Key strengths
        strengths = candidate.get("strengths", [])
        if strengths:
            parts.append(f"Strengths: {'; '.join(strengths[:3])}.")
        
        # Key weaknesses
        weaknesses = candidate.get("weaknesses", [])
        if weaknesses:
            parts.append(f"Areas of concern: {'; '.join(weaknesses[:2])}.")
        
        # Specific scores
        if scores.get("skills_match", 0) >= 85:
            parts.append("Excellent skills match.")
        elif scores.get("skills_match", 0) < 60:
            parts.append("Skills match is below expectations.")
        
        return " ".join(parts)
    
    def _calculate_tier_distribution(
        self,
        candidates: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate distribution of candidates across tiers.
        
        Args:
            candidates: List of candidates
            
        Returns:
            Tier distribution dictionary
        """
        distribution = {"A": 0, "B": 0, "C": 0, "D": 0}
        
        for candidate in candidates:
            tier = candidate.get("tier", "C")
            distribution[tier] = distribution.get(tier, 0) + 1
        
        return distribution

