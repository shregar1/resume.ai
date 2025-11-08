import bcrypt
import pytest
import uuid

from unittest.mock import Mock

from repositories.user import UserRepository

from tests.services.test_service_abstraction import TestIService


@pytest.mark.asyncio
class TestIUserService(TestIService):

    @pytest.fixture
    def mock_jwt_utility(self, urn, user_id, jwt_token):
        mock_jwt = Mock()
        mock_jwt.create_access_token = Mock(return_value=jwt_token)
        mock_jwt.decode_token = Mock(
            return_value={
                "user_id": user_id,
                "user_urn": str(uuid.uuid4()),
            }
        )
        return mock_jwt

    @pytest.fixture
    def email(self):
        """
        Email for the user.
        """
        return "test@test.com"

    @pytest.fixture
    def password(self):
        """
        Password for the user.
        """
        return "CorrectPassword123!"

    @pytest.fixture
    def hashed_password(self, password):
        """
        Hashed password for the user.
        """
        return bcrypt.hashpw(
            password.encode("utf8"),
            bcrypt.gensalt(),
        ).decode("utf8")

    @pytest.fixture
    def jwt_token(self):
        """
        JWT token for the user.
        """
        return "mock-jwt-token"

    @pytest.fixture
    def user_repository(
        self,
        urn,
        user_urn,
        api_name,
        user_id,
        db_session,
    ):
        """
        User repository for the user.
        """
        return UserRepository(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            session=db_session,
            user_id=user_id,
        )
