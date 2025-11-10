"""
Tests for the Matching Agent.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from services.agents.matching_agent import MatchingAgent


@pytest.mark.agents
@pytest.mark.unit
class TestMatchingAgent:
    """Test cases for MatchingAgent."""
    
    @pytest.fixture
    def matching_agent(self, mock_logger, mock_llm_client):
        """Create a MatchingAgent instance for testing."""
        agent = MatchingAgent(
            urn="test-urn",
            user_urn="user-urn",
            api_name="test-api",
            user_id="user-123"
        )
        agent._logger = mock_logger
        agent._llm_client = mock_llm_client
        return agent
    
    @pytest.mark.asyncio
    async def test_process_success(
        self, matching_agent, sample_cv_data, sample_jd_data
    ):
        """Test successful CV-JD matching."""
        data = {
            "cv_data": sample_cv_data,
            "jd_data": sample_jd_data,
            "jd_embeddings": {"full_description": [0.1, 0.2]}
        }
        
        matching_agent._match_skills = AsyncMock(
            return_value={"match_percentage": 85.0, "matched_skills": []}
        )
        matching_agent._semantic_match = AsyncMock(return_value=0.82)
        matching_agent._match_experience = Mock(
            return_value={"meets_requirement": True, "score": 90.0}
        )
        matching_agent._match_education = Mock(
            return_value={"meets_requirement": True, "score": 100.0}
        )
        
        result = await matching_agent.process(data)
        
        assert result["success"] is True
        assert "matches" in result
        assert "skill_matches" in result["matches"]
        assert "semantic_score" in result["matches"]
        matching_agent._logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_process_missing_cv_data(self, matching_agent, sample_jd_data):
        """Test matching fails when cv_data is missing."""
        data = {"jd_data": sample_jd_data}
        
        result = await matching_agent.process(data)
        
        assert result["success"] is False
        assert "error" in result
        matching_agent._logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_match_skills(self, matching_agent, sample_cv_data, sample_jd_data):
        """Test skill matching logic."""
        matching_agent._match_single_skill = AsyncMock(
            return_value={"match_type": "exact", "confidence": 1.0}
        )
        
        result = await matching_agent._match_skills(sample_cv_data, sample_jd_data)
        
        assert "matched_skills" in result
        assert "missing_skills" in result
        assert "match_percentage" in result
        assert isinstance(result["match_percentage"], float)
    
    @pytest.mark.asyncio
    async def test_semantic_match(
        self, matching_agent, sample_cv_data, sample_jd_data
    ):
        """Test semantic matching."""
        jd_embeddings = {"full_description": [0.5, 0.5, 0.5]}
        matching_agent.llm_client.generate_embeddings = AsyncMock(
            return_value=[[0.6, 0.6, 0.6]]
        )
        
        with pytest.patch('numpy.dot', return_value=0.85):
            with pytest.patch('numpy.linalg.norm', return_value=1.0):
                result = await matching_agent._semantic_match(
                    sample_cv_data, sample_jd_data, jd_embeddings
                )
        
        assert isinstance(result, float)
        assert 0 <= result <= 1
    
    def test_match_experience(self, matching_agent, sample_cv_data, sample_jd_data):
        """Test experience matching."""
        result = matching_agent._match_experience(sample_cv_data, sample_jd_data)
        
        assert "years_required" in result
        assert "years_candidate" in result
        assert "meets_requirement" in result
        assert isinstance(result["meets_requirement"], bool)
    
    def test_match_education(self, matching_agent, sample_cv_data, sample_jd_data):
        """Test education matching."""
        result = matching_agent._match_education(sample_cv_data, sample_jd_data)
        
        assert "required_level" in result
        assert "meets_requirement" in result
        assert isinstance(result["score"], float)


@pytest.mark.agents
@pytest.mark.unit
class TestRankingAgent:
    """Test cases for RankingAgent."""
    
    @pytest.fixture
    def ranking_agent(self, mock_logger, mock_llm_client):
        """Create a RankingAgent instance for testing."""
        from services.agents.ranking_agent import RankingAgent
        
        agent = RankingAgent(
            urn="test-urn",
            user_urn="user-urn",
            api_name="test-api",
            user_id="user-123"
        )
        agent._logger = mock_logger
        agent._llm_client = mock_llm_client
        return agent
    
    @pytest.mark.asyncio
    async def test_process_success(self, ranking_agent, sample_jd_data):
        """Test successful candidate ranking."""
        candidate_scores = [
            {
                "cv_id": "cv1",
                "scores": {"total": 90.0},
                "cv_data": {"candidate": {"name": "John"}},
                "matches": {}
            },
            {
                "cv_id": "cv2",
                "scores": {"total": 85.0},
                "cv_data": {"candidate": {"name": "Jane"}},
                "matches": {}
            }
        ]
        
        data = {
            "candidate_scores": candidate_scores,
            "jd_data": sample_jd_data
        }
        
        ranking_agent._apply_filters = Mock(return_value=candidate_scores)
        ranking_agent._assign_ranks_and_tiers = Mock(
            return_value=candidate_scores
        )
        ranking_agent._generate_explanation = Mock(return_value="Good fit")
        ranking_agent._calculate_tier_distribution = Mock(
            return_value={"excellent": 1, "good": 1}
        )
        
        result = await ranking_agent.process(data)
        
        assert result["success"] is True
        assert "ranked_candidates" in result
        assert result["total_candidates"] == 2
        ranking_agent._logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_process_empty_candidates(self, ranking_agent, sample_jd_data):
        """Test ranking with no candidates."""
        data = {"candidate_scores": [], "jd_data": sample_jd_data}
        
        result = await ranking_agent.process(data)
        
        assert result["success"] is True
        assert result["ranked_candidates"] == []
        ranking_agent._logger.warning.assert_called()


@pytest.mark.agents
@pytest.mark.unit
@pytest.mark.slow
class TestOrchestratorAgent:
    """Test cases for OrchestratorAgent."""
    
    @pytest.fixture
    def orchestrator_agent(self, mock_logger):
        """Create an OrchestratorAgent instance for testing."""
        from services.agents.orchestrator_agent import OrchestratorAgent
        
        agent = OrchestratorAgent(
            urn="test-urn",
            user_urn="user-urn",
            api_name="test-api",
            user_id="user-123"
        )
        agent._logger = mock_logger
        return agent
    
    @pytest.mark.asyncio
    async def test_process_full_workflow(
        self, orchestrator_agent, sample_jd_data, sample_cv_data, sample_file_paths
    ):
        """Test full orchestration workflow."""
        data = {
            "job_description": "Job description text",
            "job_title": "Senior Engineer",
            "company": "TechCo",
            "cv_files": sample_file_paths
        }
        
        # Mock all agent methods
        orchestrator_agent.jd_analyzer_agent.process = AsyncMock(
            return_value={
                "success": True,
                "jd_data": sample_jd_data,
                "embeddings": {}
            }
        )
        
        orchestrator_agent._parse_cv = AsyncMock(
            return_value={"success": True, "cv_data": sample_cv_data}
        )
        
        orchestrator_agent._match_and_score_cv = AsyncMock(
            return_value={
                "cv_data": sample_cv_data,
                "scores": {"total": 85.0},
                "matches": {}
            }
        )
        
        orchestrator_agent.ranking_agent.process = AsyncMock(
            return_value={
                "success": True,
                "ranked_candidates": [],
                "total_candidates": 3
            }
        )
        
        result = await orchestrator_agent.process(data)
        
        assert result["success"] is True
        assert "job_id" in result
        assert "ranked_candidates" in result
        orchestrator_agent._logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_process_jd_analysis_failure(self, orchestrator_agent):
        """Test workflow fails gracefully when JD analysis fails."""
        data = {
            "job_description": "Job description text",
            "cv_files": []
        }
        
        orchestrator_agent.jd_analyzer_agent.process = AsyncMock(
            return_value={"success": False}
        )
        
        result = await orchestrator_agent.process(data)
        
        assert result["success"] is False
        orchestrator_agent._logger.error.assert_called()

