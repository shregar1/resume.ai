"""Orchestrator Agent for coordinating the multi-agent workflow."""

import uuid
import asyncio
from typing import Dict, Any, List
from datetime import datetime

from dtos.enitities.workflow.status import WorkflowStatus

from services.agents.base_agent import BaseAgent
from services.agents.parser_agent import ParserAgent
from services.agents.jd_analyzer_agent import JDAnalyzerAgent
from services.agents.matching_agent import MatchingAgent
from services.agents.scoring_agent import ScoringAgent
from services.agents.ranking_agent import RankingAgent

class OrchestratorAgent(BaseAgent):
    """Orchestrator agent that coordinates the entire ranking workflow."""
    
    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
    ):
        """Initialize the Orchestrator Agent."""
        super().__init__("orchestrator_agent")
        
        # Initialize specialized agents
        self.parser_agent = ParserAgent(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
        )
        self.jd_analyzer_agent = JDAnalyzerAgent(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
        )
        self.matching_agent = MatchingAgent(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
        )
        self.scoring_agent = ScoringAgent(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
        )
        self.ranking_agent = RankingAgent(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_id=user_id,
        )
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate the complete ranking workflow.
        
        Args:
            data: Dictionary containing:
                - job_description: Job description text
                - job_title: Job title
                - company: Company name
                - cv_files: List of CV file paths with types
                
        Returns:
            Dictionary containing complete ranking results
        """
        job_id = str(uuid.uuid4())
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"🚀 STARTING RANKING JOB: {job_id}")
        self.logger.info(f"{'='*80}\n")
        
        try:
            num_cvs = len(data.get('cv_files', []))
            self.logger.info(f"📊 Total CVs to process: {num_cvs}\n")
            
            # Phase 1: Analyze Job Description
            self.logger.info(f"{'='*80}")
            self.logger.info("📋 PHASE 1: Analyzing Job Description with LLM")
            self.logger.info(f"{'='*80}")
            jd_result = await self.jd_analyzer_agent.process({
                "job_description": data.get("job_description"),
                "job_title": data.get("job_title", ""),
                "company": data.get("company", "")
            })
            self.logger.info("✅ Job description analyzed successfully\n")
            
            if not jd_result.get("success"):
                self.logger.error(f"Job {job_id}: Failed to analyze job description")
                raise Exception("Failed to analyze job description")
            
            jd_data = jd_result["jd_data"]
            jd_embeddings = jd_result.get("embeddings", {})
            self.logger.info(f"Job {job_id}: JD analysis complete - JD ID: {jd_data.get('jd_id')}")
            
            # Phase 2: Parse CVs in parallel
            cv_files = data.get("cv_files", [])
            self.logger.info(f"{'='*80}")
            self.logger.info(f"📄 PHASE 2: Parsing {len(cv_files)} CVs with LLM (Parallel Processing)")
            self.logger.info(f"{'='*80}")
            
            parse_tasks = [
                self._parse_cv(cv_file, job_id, i)
                for i, cv_file in enumerate(cv_files)
            ]
            
            parsed_cvs = await asyncio.gather(*parse_tasks, return_exceptions=True)
            
            # Filter out failed parses
            successful_cvs = [
                cv for cv in parsed_cvs
                if not isinstance(cv, Exception) and cv.get("success")
            ]
            
            failed_count = len(parsed_cvs) - len(successful_cvs)
            if failed_count > 0:
                self.logger.warning(f"⚠️  {failed_count} CVs failed to parse")
            self.logger.info(f"✅ Successfully parsed {len(successful_cvs)}/{len(cv_files)} CVs\n")
            
            # Phase 3: Match and Score each CV
            self.logger.info(f"{'='*80}")
            self.logger.info(f"🔍 PHASE 3: Matching and Scoring {len(successful_cvs)} Candidates")
            self.logger.info(f"{'='*80}")
            
            score_tasks = [
                self._match_and_score_cv(cv["cv_data"], jd_data, jd_embeddings, job_id)
                for cv in successful_cvs
            ]
            
            candidate_scores = await asyncio.gather(*score_tasks, return_exceptions=True)
            
            # Filter successful scores
            successful_scores = [
                score for score in candidate_scores
                if not isinstance(score, Exception) and score is not None
            ]
            
            self.logger.info(f"✅ Completed matching and scoring for {len(successful_scores)} candidates\n")
            
            # Phase 4: Rank candidates
            self.logger.info(f"{'='*80}")
            self.logger.info(f"🏆 PHASE 4: Ranking {len(successful_scores)} Candidates")
            self.logger.info(f"{'='*80}")
            ranking_result = await self.ranking_agent.process({
                "candidate_scores": successful_scores,
                "jd_data": jd_data
            })
            
            if not ranking_result.get("success"):
                raise Exception("Failed to rank candidates")
            
            self.logger.info("✅ Ranking completed successfully\n")
            self.logger.info(f"{'='*80}")
            self.logger.info(f"🎉 JOB COMPLETED: {job_id}")
            self.logger.info(f"{'='*80}")
            self.logger.info(f"📊 Total Candidates Ranked: {ranking_result.get('total_candidates', 0)}")
            self.logger.info(f"📈 Tier Distribution: {ranking_result.get('tiers', {})}")
            self.logger.info(f"{'='*80}\n")
            
            # Compile final results
            return {
                "success": True,
                "job_id": job_id,
                "jd_data": jd_data,
                "total_cvs_submitted": len(cv_files),
                "total_cvs_parsed": len(successful_cvs),
                "total_candidates_ranked": ranking_result.get("total_candidates", 0),
                "ranked_candidates": ranking_result["ranked_candidates"],
                "tier_distribution": ranking_result.get("tiers", {}),
                "completed_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            return await self.handle_error(e, {"job_id": job_id})
    
    async def _parse_cv(
        self,
        cv_file: Dict[str, str],
        job_id: str,
        index: int
    ) -> Dict[str, Any]:
        """Parse a single CV.
        
        Args:
            cv_file: CV file information
            job_id: Job ID
            index: CV index
            
        Returns:
            Parsed CV data
        """
        try:
            self.logger.info(f"  📄 Parsing CV {index + 1} - {cv_file.get('file_path', 'unknown')}")
            result = await self.parser_agent.process(cv_file)
            
            if result.get("success"):
                self.logger.info(f"  ✅ CV {index + 1} parsed successfully")
            else:
                self.logger.warning(f"  ❌ CV {index + 1} failed to parse")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Job {job_id}: Error parsing CV {index + 1}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _match_and_score_cv(
        self,
        cv_data: Dict[str, Any],
        jd_data: Dict[str, Any],
        jd_embeddings: Dict[str, List[float]],
        job_id: str
    ) -> Dict[str, Any]:
        """Match and score a single CV.
        
        Args:
            cv_data: Parsed CV data
            jd_data: Job description data
            jd_embeddings: JD embeddings
            job_id: Job ID
            
        Returns:
            Candidate score
        """
        try:
            # Matching phase
            match_result = await self.matching_agent.process({
                "cv_data": cv_data,
                "jd_data": jd_data,
                "jd_embeddings": jd_embeddings
            })
            
            if not match_result.get("success"):
                self.logger.warning(f"Job {job_id}: Matching failed for CV {cv_data.get('cv_id')}")
                return None
            
            # Scoring phase
            score_result = await self.scoring_agent.process({
                "cv_data": cv_data,
                "jd_data": jd_data,
                "matches": match_result["matches"]
            })
            
            if not score_result.get("success"):
                self.logger.warning(f"Job {job_id}: Scoring failed for CV {cv_data.get('cv_id')}")
                return None
            
            # Compile candidate score
            candidate_score = {
                "candidate_id": str(uuid.uuid4()),
                "cv_id": cv_data.get("cv_id"),
                "jd_id": jd_data.get("jd_id"),
                "candidate_name": cv_data.get("candidate", {}).get("name", "Unknown"),
                "scores": score_result["scores"],
                "matches": {
                    "matched_skills": match_result["matches"]["skill_matches"].get("matched_must_have", []),
                    "missing_skills": match_result["matches"]["skill_matches"].get("missing_must_have", []),
                    "extra_skills": match_result["matches"]["skill_matches"].get("extra_skills", [])
                },
                "strengths": score_result.get("strengths", []),
                "weaknesses": score_result.get("weaknesses", [])
            }
            
            return candidate_score
        
        except Exception as e:
            self.logger.error(f"Job {job_id}: Error in match/score for CV {cv_data.get('cv_id')}: {e}")
            return None
    
    async def get_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a ranking job.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job status
        """
        # This would typically query a database or cache
        # For now, return a placeholder
        return {
            "job_id": job_id,
            "status": WorkflowStatus.COMPLETED.value,
            "message": "Job status tracking not yet implemented"
        }

