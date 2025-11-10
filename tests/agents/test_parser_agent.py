"""
Tests for the Parser Agent.
"""
import pytest
from unittest.mock import Mock, patch, mock_open, AsyncMock
from services.agents.parser_agent import ParserAgent


@pytest.mark.agents
@pytest.mark.unit
class TestParserAgent:
    """Test cases for ParserAgent."""
    
    @pytest.fixture
    def parser_agent(self, mock_logger):
        """Create a ParserAgent instance for testing."""
        with patch('services.agents.parser_agent.llm', None):
            with patch('services.agents.parser_agent.embedding_llm', None):
                agent = ParserAgent(
                    urn="test-urn",
                    user_urn="user-urn",
                    api_name="test-api",
                    user_id="user-123"
                )
                agent._logger = mock_logger
                return agent
    
    @pytest.mark.asyncio
    async def test_process_success(self, parser_agent, sample_cv_data):
        """Test successful CV processing."""
        data = {
            "file_path": "/path/to/resume.pdf",
            "file_type": "pdf"
        }
        
        # Mock the internal methods
        parser_agent._extract_text = AsyncMock(return_value="CV text content")
        parser_agent._parse_with_llm = AsyncMock(return_value=sample_cv_data)
        
        result = await parser_agent.process(data)
        
        assert result["success"] is True
        assert "cv_data" in result
        assert result["cv_data"]["metadata"]["file_path"] == "/path/to/resume.pdf"
        parser_agent._logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_process_missing_file_path(self, parser_agent):
        """Test processing fails when file_path is missing."""
        data = {"file_type": "pdf"}
        
        result = await parser_agent.process(data)
        
        assert result["success"] is False
        assert "error" in result
        parser_agent._logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_extract_text_pdf(self, parser_agent):
        """Test text extraction from PDF."""
        from unittest.mock import MagicMock
        
        mock_pdf = MagicMock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "PDF content"
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        
        with patch('pdfplumber.open', return_value=mock_pdf):
            with patch('services.agents.parser_agent.clean_text', return_value="Cleaned PDF content"):
                result = await parser_agent._extract_text("/path/to/file.pdf", "pdf")
        
        assert result == "Cleaned PDF content"
        parser_agent._logger.debug.assert_called()
    
    @pytest.mark.asyncio
    async def test_extract_text_docx(self, parser_agent):
        """Test text extraction from DOCX."""
        mock_doc = Mock()
        mock_para = Mock()
        mock_para.text = "DOCX content"
        mock_doc.paragraphs = [mock_para]
        
        with patch('services.agents.parser_agent.Document', return_value=mock_doc):
            with patch('services.agents.parser_agent.clean_text', return_value="Cleaned DOCX content"):
                result = await parser_agent._extract_text("/path/to/file.docx", "docx")
        
        assert result == "Cleaned DOCX content"
    
    @pytest.mark.asyncio
    async def test_extract_text_txt(self, parser_agent, sample_pdf_content):
        """Test text extraction from TXT."""
        with patch('builtins.open', mock_open(read_data=sample_pdf_content)):
            with patch('services.agents.parser_agent.clean_text', return_value=sample_pdf_content):
                result = await parser_agent._extract_text("/path/to/file.txt", "txt")
        
        assert sample_pdf_content in result
    
    @pytest.mark.asyncio
    async def test_extract_text_unsupported_type(self, parser_agent):
        """Test extraction fails for unsupported file types."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            await parser_agent._extract_text("/path/to/file.xyz", "xyz")
    
    @pytest.mark.asyncio
    async def test_parse_with_llm_success(self, parser_agent, sample_cv_data):
        """Test successful LLM parsing."""
        import json
        llm_response = json.dumps(sample_cv_data)
        
        parser_agent.llm_client = Mock()
        parser_agent.llm_client.generate = AsyncMock(return_value=llm_response)
        parser_agent._calculate_duration_months = Mock(return_value=48)
        
        result = await parser_agent._parse_with_llm("CV text")
        
        assert "cv_id" in result
        assert result["candidate"]["name"] == "John Doe"
        assert "total_experience_years" in result
    
    @pytest.mark.asyncio
    async def test_parse_with_llm_json_decode_error(self, parser_agent):
        """Test LLM parsing falls back on JSON decode error."""
        parser_agent.llm_client = Mock()
        parser_agent.llm_client.generate = AsyncMock(return_value="Invalid JSON")
        parser_agent._fallback_parsing = AsyncMock(return_value={"cv_id": "test"})
        
        result = await parser_agent._parse_with_llm("CV text")
        
        assert result["cv_id"] == "test"
        parser_agent._logger.warning.assert_called()
    
    @pytest.mark.asyncio
    async def test_parse_with_llm_removes_markdown(self, parser_agent, sample_cv_data):
        """Test that markdown code blocks are removed from LLM response."""
        import json
        llm_response = f"```json\n{json.dumps(sample_cv_data)}\n```"
        
        parser_agent.llm_client = Mock()
        parser_agent.llm_client.generate = AsyncMock(return_value=llm_response)
        parser_agent._calculate_duration_months = Mock(return_value=48)
        
        result = await parser_agent._parse_with_llm("CV text")
        
        assert "cv_id" in result
        assert result["candidate"]["name"] == "John Doe"
    
    @pytest.mark.asyncio
    async def test_fallback_parsing(self, parser_agent):
        """Test fallback parsing returns basic structure."""
        parser_agent._extract_email = Mock(return_value="test@example.com")
        parser_agent._extract_phone = Mock(return_value="+1-555-0123")
        
        result = await parser_agent._fallback_parsing("Some CV text")
        
        assert "cv_id" in result
        assert result["candidate"]["email"] == "test@example.com"
        assert result["total_experience_years"] == 0.0
        parser_agent._logger.warning.assert_called()

