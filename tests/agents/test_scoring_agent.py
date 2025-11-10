"""
Tests for the Scoring Agent.
"""
import pytest
from unittest.mock import Mock
from services.agents.scoring_agent import ScoringAgent


@pytest.mark.agents
@pytest.mark.unit
class TestScoringAgent:
    """Test cases for ScoringAgent."""
    
    @pytest.fixture
    def scoring_agent(self, mock_logger):
        """Create a ScoringAgent instance for testing."""
        agent = ScoringAgent(
            urn="test-urn",
            user_urn="user-urn",
            api_name="test-api",
            user_id="user-123"
        )
        agent._logger = mock_logger
        return agent
    
    @pytest.mark.asyncio
    async def test_process_success(
        self, scoring_agent, sample_cv_data, sample_jd_data, sample_match_results
    ):
        """Test successful scoring calculation."""
        data = {
            "cv_data": sample_cv_data,
            "jd_data": sample_jd_data,
            "matches": sample_match_results
        }
        
        result = await scoring_agent.process(data)
        
        assert result["success"] is True
        assert "scores" in result
        assert "strengths" in result
        assert "weaknesses" in result
        assert 0 <= result["scores"]["total"] <= 100
        scoring_agent._logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_process_missing_cv_data(self, scoring_agent, sample_jd_data):
        """Test scoring fails when cv_data is missing."""
        data = {"jd_data": sample_jd_data}
        
        result = await scoring_agent.process(data)
        
        assert result["success"] is False
        assert "error" in result
        scoring_agent._logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_process_missing_jd_data(self, scoring_agent, sample_cv_data):
        """Test scoring fails when jd_data is missing."""
        data = {"cv_data": sample_cv_data}
        
        result = await scoring_agent.process(data)
        
        assert result["success"] is False
        assert "error" in result
    
    def test_calculate_skills_score(self, scoring_agent, sample_match_results):
        """Test skills score calculation."""
        score = scoring_agent._calculate_skills_score(sample_match_results)
        
        assert isinstance(score, float)
        assert 0 <= score <= 100
        assert score == 90.0  # Based on sample match percentage
    
    def test_calculate_skills_score_no_matches(self, scoring_agent):
        """Test skills score calculation with no matches."""
        matches = {"skill_matches": {"match_percentage": 0}}
        
        score = scoring_agent._calculate_skills_score(matches)
        
        assert score == 0.0
    
    def test_calculate_experience_score(
        self, scoring_agent, sample_match_results, sample_cv_data, sample_jd_data
    ):
        """Test experience score calculation."""
        score = scoring_agent._calculate_experience_score(
            sample_match_results, sample_cv_data, sample_jd_data
        )
        
        assert isinstance(score, float)
        assert 0 <= score <= 100
    
    def test_calculate_education_score(self, scoring_agent, sample_match_results):
        """Test education score calculation."""
        score = scoring_agent._calculate_education_score(sample_match_results)
        
        assert isinstance(score, float)
        assert 0 <= score <= 100
        assert score == 100.0  # Based on sample data
    
    def test_calculate_career_trajectory_score(self, scoring_agent, sample_cv_data):
        """Test career trajectory score calculation."""
        score = scoring_agent._calculate_career_trajectory_score(sample_cv_data)
        
        assert isinstance(score, float)
        assert 0 <= score <= 100
    
    def test_calculate_confidence(self, scoring_agent, sample_match_results, sample_cv_data):
        """Test confidence calculation."""
        confidence = scoring_agent._calculate_confidence(sample_match_results, sample_cv_data)
        
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1
    
    def test_identify_strengths_weaknesses(
        self, scoring_agent, sample_cv_data, sample_jd_data, sample_match_results, sample_scores
    ):
        """Test identification of strengths and weaknesses."""
        strengths, weaknesses = scoring_agent._identify_strengths_weaknesses(
            sample_cv_data, sample_jd_data, sample_match_results, sample_scores
        )
        
        assert isinstance(strengths, list)
        assert isinstance(weaknesses, list)
        assert len(strengths) > 0

