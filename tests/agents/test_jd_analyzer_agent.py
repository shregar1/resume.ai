"""
Tests for the JD Analyzer Agent.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from services.agents.jd_analyzer_agent import JDAnalyzerAgent


@pytest.mark.agents
@pytest.mark.unit
class TestJDAnalyzerAgent:
    """Test cases for JDAnalyzerAgent."""
    
    @pytest.fixture
    def jd_analyzer_agent(self, mock_logger, mock_llm_client):
        """Create a JDAnalyzerAgent instance for testing."""
        agent = JDAnalyzerAgent(
            urn="test-urn",
            user_urn="user-urn",
            api_name="test-api",
            user_id="user-123"
        )
        agent._logger = mock_logger
        agent._llm_client = mock_llm_client
        return agent
    
    @pytest.mark.asyncio
    async def test_process_success(self, jd_analyzer_agent, sample_jd_data):
        """Test successful JD analysis."""
        data = {
            "job_description": "Job description text",
            "job_title": "Senior Backend Engineer",
            "company": "TechCo"
        }
        
        jd_analyzer_agent._analyze_with_llm = AsyncMock(return_value=sample_jd_data)
        jd_analyzer_agent._generate_embeddings = AsyncMock(
            return_value={"full_description": [0.1, 0.2], "skills": [0.3, 0.4]}
        )
        
        result = await jd_analyzer_agent.process(data)
        
        assert result["success"] is True
        assert "jd_data" in result
        assert "embeddings" in result
        assert result["jd_data"]["job_title"] == "Senior Backend Engineer"
        jd_analyzer_agent._logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_process_missing_job_description(self, jd_analyzer_agent):
        """Test processing fails when job_description is missing."""
        data = {"job_title": "Engineer"}
        
        result = await jd_analyzer_agent.process(data)
        
        assert result["success"] is False
        assert "error" in result
        jd_analyzer_agent._logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_analyze_with_llm_success(self, jd_analyzer_agent, sample_jd_data):
        """Test successful LLM analysis."""
        import json
        llm_response = json.dumps(sample_jd_data)
        
        jd_analyzer_agent.llm_client.generate = AsyncMock(return_value=llm_response)
        
        result = await jd_analyzer_agent._analyze_with_llm(
            "JD text", "Senior Engineer", "TechCo"
        )
        
        assert result["job_title"] == "Senior Backend Engineer"
        assert result["company"] == "TechCo"
        assert "jd_id" in result
        assert "full_description" in result
    
    @pytest.mark.asyncio
    async def test_analyze_with_llm_fallback(self, jd_analyzer_agent):
        """Test LLM analysis falls back on error."""
        jd_analyzer_agent.llm_client.generate = AsyncMock(side_effect=Exception("LLM error"))
        
        result = await jd_analyzer_agent._analyze_with_llm(
            "JD text", "Engineer", "Company"
        )
        
        assert result["job_title"] == "Engineer"
        assert result["company"] == "Company"
        assert result["seniority_level"] == "mid"
        jd_analyzer_agent._logger.warning.assert_called()
    
    @pytest.mark.asyncio
    async def test_analyze_with_llm_removes_markdown(self, jd_analyzer_agent, sample_jd_data):
        """Test that markdown is stripped from LLM response."""
        import json
        llm_response = f"```json\n{json.dumps(sample_jd_data)}\n```"
        
        jd_analyzer_agent.llm_client.generate = AsyncMock(return_value=llm_response)
        
        result = await jd_analyzer_agent._analyze_with_llm("JD text", "Title", "Company")
        
        assert "jd_id" in result
        assert result["job_title"] == "Senior Backend Engineer"
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_success(self, jd_analyzer_agent, sample_jd_data):
        """Test successful embeddings generation."""
        embeddings_list = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        jd_analyzer_agent.llm_client.generate_embeddings = AsyncMock(
            return_value=embeddings_list
        )
        
        result = await jd_analyzer_agent._generate_embeddings(sample_jd_data)
        
        assert "full_description" in result
        assert "skills" in result
        assert "responsibilities" in result
        assert result["full_description"] == [0.1, 0.2]
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_error(self, jd_analyzer_agent, sample_jd_data):
        """Test embeddings generation handles errors."""
        jd_analyzer_agent.llm_client.generate_embeddings = AsyncMock(
            side_effect=Exception("Embedding error")
        )
        
        result = await jd_analyzer_agent._generate_embeddings(sample_jd_data)
        
        assert result["full_description"] == []
        assert result["skills"] == []
        jd_analyzer_agent._logger.error.assert_called()

