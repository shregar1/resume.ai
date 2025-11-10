"""
Tests for DTOs (Data Transfer Objects).
"""
import pytest
from pydantic import ValidationError


@pytest.mark.unit
class TestRequestDTOs:
    """Test cases for request DTOs."""
    
    def test_user_login_request_dto(self):
        """Test UserLoginRequestDTO validation - skipped as user modules removed."""
        pytest.skip("User login DTOs have been removed from the codebase")
    
    def test_user_login_request_dto_invalid_email(self):
        """Test UserLoginRequestDTO rejects invalid email - skipped as user modules removed."""
        pytest.skip("User login DTOs have been removed from the codebase")
    
    def test_user_registration_request_dto(self):
        """Test UserRegistrationRequestDTO validation - skipped as user modules removed."""
        pytest.skip("User registration DTOs have been removed from the codebase")


@pytest.mark.unit
class TestResponseDTOs:
    """Test cases for response DTOs."""
    
    def test_base_response_dto(self):
        """Test BaseResponseDTO structure."""
        from dtos.responses.base import BaseResponseDTO
        
        dto = BaseResponseDTO(
            transactionUrn="test-urn",
            status="success",
            responseMessage="Test message",
            responseKey="test_key",
            data={"result": "test"}
        )
        
        assert dto.transactionUrn == "test-urn"
        assert dto.status == "success"
        assert dto.data["result"] == "test"
    
    def test_base_response_dto_serialization(self):
        """Test BaseResponseDTO can be serialized."""
        from dtos.responses.base import BaseResponseDTO
        
        dto = BaseResponseDTO(
            transactionUrn="test-urn",
            status="success",
            responseMessage="Test",
            responseKey="test",
            data={}
        )
        
        dict_data = dto.model_dump()
        
        assert isinstance(dict_data, dict)
        assert "transactionUrn" in dict_data

