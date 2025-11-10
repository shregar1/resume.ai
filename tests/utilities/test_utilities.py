"""
Tests for utility functions.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from utilities.llm_client import LLMClientUtility
from utilities.helpers import clean_text, normalize_skill


@pytest.mark.utilities
@pytest.mark.unit
class TestLLMClientUtility:
    """Test cases for LLM client utility."""
    
    @pytest.fixture
    def llm_client(self, mock_logger):
        """Create LLM client for testing."""
        client = LLMClientUtility(
            urn="test-urn",
            user_urn="user-urn",
            api_name="test-api",
            user_id="user-123",
            conversational_llm_model=Mock(),
            embedding_llm_model=Mock()
        )
        client._logger = mock_logger
        client.google_client = AsyncMock()
        return client
    
    @pytest.mark.asyncio
    async def test_generate_text_success(self, llm_client):
        """Test successful text generation."""
        llm_client.google_client.generate = AsyncMock(
            return_value="Generated response text"
        )
        
        result = await llm_client.generate(
            prompt="Test prompt",
            system_prompt="System instructions",
            temperature=0.7
        )
        
        assert result == "Generated response text"
        assert llm_client.google_client.generate.called
        llm_client._logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_generate_text_with_system_prompt(self, llm_client):
        """Test text generation combines system and user prompts."""
        llm_client.google_client.generate = AsyncMock(
            return_value="Response"
        )
        
        await llm_client.generate(
            prompt="User prompt",
            system_prompt="System prompt"
        )
        
        # Check that prompts were combined
        call_args = llm_client.google_client.generate.call_args
        combined_prompt = call_args.kwargs.get('prompt') or call_args[1].get('prompt')
        assert "System prompt" in combined_prompt
        assert "User prompt" in combined_prompt
    
    @pytest.mark.asyncio
    async def test_generate_text_error(self, llm_client):
        """Test text generation handles errors."""
        llm_client.google_client.generate = AsyncMock(
            side_effect=Exception("LLM Error")
        )
        
        with pytest.raises(Exception, match="LLM Error"):
            await llm_client.generate(prompt="Test")
        
        llm_client._logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_success(self, llm_client):
        """Test successful embeddings generation."""
        embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        llm_client.google_client.generate_embeddings = AsyncMock(
            return_value=embeddings
        )
        
        result = await llm_client.generate_embeddings(
            texts=["Text 1", "Text 2"]
        )
        
        assert result == embeddings
        assert len(result) == 2
        llm_client._logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_error(self, llm_client):
        """Test embeddings generation handles errors."""
        llm_client.google_client.generate_embeddings = AsyncMock(
            side_effect=Exception("Embedding Error")
        )
        
        with pytest.raises(Exception, match="Embedding Error"):
            await llm_client.generate_embeddings(texts=["Text"])
        
        llm_client._logger.error.assert_called()


@pytest.mark.utilities
@pytest.mark.unit
class TestHelperFunctions:
    """Test cases for helper functions."""
    
    def test_clean_text_removes_extra_whitespace(self):
        """Test clean_text removes extra whitespace."""
        text = "Hello    World  \n\n  Test"
        result = clean_text(text)
        
        assert "    " not in result
        assert result.count("\n") < text.count("\n")
    
    def test_clean_text_empty_string(self):
        """Test clean_text handles empty strings."""
        result = clean_text("")
        assert result == ""
    
    def test_normalize_skill_lowercase(self):
        """Test normalize_skill converts to lowercase."""
        result = normalize_skill("PYTHON")
        assert result == "python"
    
    def test_normalize_skill_removes_special_chars(self):
        """Test normalize_skill removes special characters."""
        result = normalize_skill("Python-3.9")
        assert "-" not in result or result == "python39"


@pytest.mark.utilities
@pytest.mark.unit
class TestJWTUtility:
    """Test cases for JWT utility."""
    
    @pytest.fixture
    def jwt_utility(self):
        """Create JWT utility for testing."""
        from utilities.jwt import JWTUtility
        
        return JWTUtility(urn="test-urn")
    
    def test_create_access_token(self, jwt_utility):
        """Test access token creation."""
        from unittest.mock import patch
        
        data = {"user_id": 123, "email": "test@example.com"}
        
        with patch('start_utils.SECRET_KEY', 'test-secret'):
            with patch('start_utils.ALGORITHM', 'HS256'):
                token = jwt_utility.create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_token_valid(self, jwt_utility):
        """Test decoding valid token."""
        from unittest.mock import patch
        
        data = {"user_id": 123}
        
        with patch('start_utils.SECRET_KEY', 'test-secret'):
            with patch('start_utils.ALGORITHM', 'HS256'):
                token = jwt_utility.create_access_token(data)
                decoded = jwt_utility.decode_token(token)
        
        assert decoded["user_id"] == 123
    
    def test_decode_token_invalid(self, jwt_utility):
        """Test decoding invalid token raises error."""
        from unittest.mock import patch
        
        with patch('start_utils.SECRET_KEY', 'test-secret'):
            with patch('start_utils.ALGORITHM', 'HS256'):
                with pytest.raises(Exception):
                    jwt_utility.decode_token("invalid.token.here")


@pytest.mark.utilities
@pytest.mark.unit  
class TestDictionaryUtility:
    """Test cases for dictionary utility."""
    
    @pytest.fixture
    def dict_utility(self):
        """Create dictionary utility for testing."""
        from utilities.dictionary import DictionaryUtility
        
        return DictionaryUtility(urn="test-urn")
    
    def test_convert_keys_to_camel_case(self, dict_utility):
        """Test conversion of dictionary keys to camelCase."""
        input_dict = {
            "first_name": "John",
            "last_name": "Doe",
            "email_address": "john@example.com"
        }
        
        result = dict_utility.convert_dict_keys_to_camel_case(input_dict)
        
        assert "firstName" in result
        assert "lastName" in result
        assert "emailAddress" in result
        assert "first_name" not in result
    
    def test_convert_keys_nested(self, dict_utility):
        """Test conversion handles nested dictionaries."""
        input_dict = {
            "user_info": {
                "first_name": "John",
                "contact_details": {
                    "phone_number": "555-0123"
                }
            }
        }
        
        result = dict_utility.convert_dict_keys_to_camel_case(input_dict)
        
        assert "userInfo" in result
        assert "firstName" in result["userInfo"]
        assert "contactDetails" in result["userInfo"]
        assert "phoneNumber" in result["userInfo"]["contactDetails"]

