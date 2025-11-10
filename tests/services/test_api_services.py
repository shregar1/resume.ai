"""
Tests for API services.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch


@pytest.mark.services
@pytest.mark.unit
class TestRankingJobService:
    """Test cases for Ranking Job service."""
    
    @pytest.fixture
    def ranking_service(self, mock_logger):
        """Create a ranking job service instance for testing."""
        from services.apis.v1.ranking_job.create import CreateRankingJobService
        
        service = CreateRankingJobService(
            urn="test-urn",
            user_urn="user-urn",
            api_name="create_ranking_job"
        )
        service._logger = mock_logger
        return service
    
    @pytest.mark.asyncio
    async def test_create_ranking_job_success(
        self, ranking_service, sample_job_description, sample_file_paths
    ):
        """Test successful ranking job creation."""
        request_dto = Mock()
        request_dto.job_description = sample_job_description
        request_dto.job_title = "Senior Engineer"
        request_dto.company = "TechCo"
        
        # Mock orchestrator
        with patch('services.apis.v1.ranking_job.create.OrchestratorAgent') as mock_orch:
            mock_orch_instance = AsyncMock()
            mock_orch_instance.process = AsyncMock(
                return_value={
                    "success": True,
                    "job_id": "job-123",
                    "ranked_candidates": []
                }
            )
            mock_orch.return_value = mock_orch_instance
            
            result = await ranking_service.run(request_dto)
        
        assert result is not None
        ranking_service._logger.info.assert_called()


@pytest.mark.services  
@pytest.mark.integration
class TestServiceIntegration:
    """Integration tests for services working together."""
    
    @pytest.mark.asyncio
    async def test_full_ranking_pipeline(
        self, sample_job_description, sample_file_paths
    ):
        """Test complete ranking pipeline integration."""
        # This would test the full flow from job creation to ranking
        # Requires mock data and orchestrator setup
        pass

