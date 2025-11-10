"""
Pytest configuration and fixtures for the test suite.
"""
import pytest
import asyncio
from typing import Dict, Any, List
from unittest.mock import Mock, MagicMock, AsyncMock
from datetime import datetime
import uuid


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.bind = Mock(return_value=logger)
    return logger


@pytest.fixture
def sample_cv_data() -> Dict[str, Any]:
    """Sample CV data for testing."""
    return {
        "cv_id": str(uuid.uuid4()),
        "candidate": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-0123",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/johndoe"
        },
        "summary": "Experienced software engineer with 5+ years in backend development",
        "experience": [
            {
                "company": "Tech Corp",
                "role": "Senior Software Engineer",
                "start_date": "2020-01",
                "end_date": "2024-01",
                "description": "Led backend development team",
                "key_achievements": [
                    "Reduced API latency by 40%",
                    "Implemented microservices architecture"
                ],
                "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                "duration_months": 48
            },
            {
                "company": "StartupXYZ",
                "role": "Software Engineer",
                "start_date": "2018-06",
                "end_date": "2020-01",
                "description": "Full-stack development",
                "key_achievements": ["Built RESTful APIs"],
                "technologies": ["Python", "Django", "React"],
                "duration_months": 19
            }
        ],
        "education": [
            {
                "institution": "Stanford University",
                "degree": "BS",
                "field": "Computer Science",
                "graduation_year": 2018
            }
        ],
        "skills": {
            "technical": ["Python", "FastAPI", "Django", "PostgreSQL", "Docker", "Kubernetes"],
            "soft": ["Leadership", "Communication", "Problem Solving"],
            "tools": ["Git", "Jenkins", "AWS"],
            "languages": ["English", "Spanish"]
        },
        "certifications": [
            {
                "name": "AWS Certified Developer",
                "issuer": "Amazon",
                "date": "2023-01"
            }
        ],
        "projects": [
            {
                "name": "E-commerce Platform",
                "description": "Built scalable e-commerce backend",
                "technologies": ["Python", "FastAPI", "PostgreSQL"]
            }
        ],
        "total_experience_years": 5.6,
        "metadata": {
            "file_path": "/path/to/resume.pdf",
            "file_type": "pdf",
            "parser_version": "1.0"
        }
    }


@pytest.fixture
def sample_jd_data() -> Dict[str, Any]:
    """Sample job description data for testing."""
    return {
        "jd_id": str(uuid.uuid4()),
        "job_title": "Senior Backend Engineer",
        "company": "TechCo",
        "department": "Engineering",
        "seniority_level": "senior",
        "requirements": {
            "must_have_skills": [
                {"skill": "Python", "weight": 0.9},
                {"skill": "FastAPI", "weight": 0.8},
                {"skill": "PostgreSQL", "weight": 0.7},
                {"skill": "Docker", "weight": 0.6}
            ],
            "nice_to_have_skills": [
                {"skill": "Kubernetes", "weight": 0.5},
                {"skill": "AWS", "weight": 0.4}
            ],
            "min_experience_years": 5,
            "education_level": "Bachelor's degree",
            "industry_experience": ["Technology"],
            "certifications": ["AWS Certified"]
        },
        "responsibilities": [
            "Design and implement scalable APIs",
            "Lead backend development team",
            "Optimize database performance"
        ],
        "scoring_weights": {
            "skills": 0.4,
            "experience": 0.3,
            "education": 0.15,
            "career_trajectory": 0.1,
            "other": 0.05
        },
        "full_description": "We are looking for a Senior Backend Engineer..."
    }


@pytest.fixture
def sample_match_results() -> Dict[str, Any]:
    """Sample matching results for testing."""
    return {
        "skill_matches": {
            "matched_skills": [
                {"skill": "Python", "weight": 0.9, "match_type": "exact"},
                {"skill": "FastAPI", "weight": 0.8, "match_type": "exact"},
                {"skill": "PostgreSQL", "weight": 0.7, "match_type": "exact"},
                {"skill": "Docker", "weight": 0.6, "match_type": "exact"}
            ],
            "missing_skills": [],
            "additional_skills": ["Django", "React"],
            "match_percentage": 90.0
        },
        "semantic_score": 0.85,
        "experience_match": {
            "years_required": 5,
            "years_candidate": 5.6,
            "meets_requirement": True,
            "score": 95.0
        },
        "education_match": {
            "required_level": "Bachelor's degree",
            "candidate_level": "BS Computer Science",
            "meets_requirement": True,
            "score": 100.0
        }
    }


@pytest.fixture
def sample_scores() -> Dict[str, Any]:
    """Sample scoring results for testing."""
    return {
        "total": 87.5,
        "skills_match": 90.0,
        "experience_relevance": 88.0,
        "education_fit": 85.0,
        "career_trajectory": 82.0,
        "confidence": 0.9
    }


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing."""
    client = AsyncMock()
    client.generate = AsyncMock(return_value='{"test": "response"}')
    client.generate_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3]])
    return client


@pytest.fixture
def mock_user_repository():
    """Mock user repository for testing."""
    repo = Mock()
    repo.retrieve_record_by_email = Mock(return_value=None)
    repo.retrieve_record_by_id = Mock(return_value=None)
    repo.create_record = Mock()
    repo.update_record = Mock()
    return repo


@pytest.fixture
def sample_pdf_content() -> str:
    """Sample PDF text content for testing."""
    return """
    John Doe
    john.doe@example.com | +1-555-0123 | San Francisco, CA
    
    SUMMARY
    Experienced software engineer with 5+ years in backend development
    
    EXPERIENCE
    Senior Software Engineer at Tech Corp (2020-2024)
    - Led backend development team
    - Reduced API latency by 40%
    
    EDUCATION
    Stanford University - BS Computer Science (2018)
    
    SKILLS
    Python, FastAPI, Django, PostgreSQL, Docker, Kubernetes
    """


@pytest.fixture
def sample_job_description() -> str:
    """Sample job description text for testing."""
    return """
    Senior Backend Engineer
    TechCo - Engineering Department
    
    We are looking for a Senior Backend Engineer with 5+ years of experience.
    
    Requirements:
    - Strong proficiency in Python and FastAPI
    - Experience with PostgreSQL and Docker
    - Bachelor's degree in Computer Science or related field
    
    Responsibilities:
    - Design and implement scalable APIs
    - Lead backend development team
    - Optimize database performance
    """


@pytest.fixture
def mock_db_session():
    """Mock database session for testing."""
    session = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.query = Mock()
    session.rollback = Mock()
    session.close = Mock()
    return session


@pytest.fixture
def sample_file_paths() -> List[Dict[str, str]]:
    """Sample CV file paths for testing."""
    return [
        {"file_path": "/path/to/resume1.pdf", "file_type": "pdf"},
        {"file_path": "/path/to/resume2.pdf", "file_type": "pdf"},
        {"file_path": "/path/to/resume3.docx", "file_type": "docx"}
    ]


@pytest.fixture
def sample_urn() -> str:
    """Generate a sample URN for testing."""
    return str(uuid.uuid4())


@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user data for testing."""
    return {
        "id": 1,
        "urn": str(uuid.uuid4()),
        "email": "test@example.com",
        "password": "hashed_password",
        "is_logged_in": False,
        "is_deleted": False,
        "created_on": datetime.now()
    }

