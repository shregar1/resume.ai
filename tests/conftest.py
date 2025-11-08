import asyncio
import pytest
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def urn():
    """Test urn for login tests."""
    return "test-urn"


@pytest.fixture(scope="session")
def user_urn():
    """Test user urn for login tests."""
    return "test-user-urn"


@pytest.fixture(scope="session")
def api_name():
    """Test api name for login tests."""
    return "test-api"


@pytest.fixture(scope="session")
def user_id():
    """Test user id for login tests."""
    return 1


@pytest.fixture(scope="session")
def reference_number():
    """Test reference number for login tests."""
    return str(uuid.uuid4())


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_database_url():
    return "postgresql+psycopg2://calcount:calcount123@0.0.0.0:5432/calcount"


@pytest.fixture(scope="session")
def test_engine(test_database_url):
    """Create test database engine."""

    engine = create_engine(test_database_url)

    yield engine

    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    """Create a new database session for a test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
