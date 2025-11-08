import datetime
import pytest

from unittest.mock import Mock

from dtos.requests.user.logout import UserLogoutRequestDTO

from models.user import User

from repositories.user import UserRepository

from services.user.logout import UserLogoutService

from tests.services.user.test_user_abstraction import TestIUserService


@pytest.mark.asyncio
class TestUserLogoutService(TestIUserService):
    @pytest.fixture(autouse=True)
    def setup(
        self,
        urn,
        user_urn,
        api_name,
        mock_jwt_utility,
        user_repository,
    ):
        self.user_repository: UserRepository = user_repository
        self.logout_service = UserLogoutService(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_repository=self.user_repository,
            jwt_utility=mock_jwt_utility,
        )

    @pytest.fixture
    def valid_logout_data(
        self,
        reference_number,
    ):
        return UserLogoutRequestDTO(
            reference_number=reference_number
        )

    @pytest.fixture
    def mock_logged_in_user(self, urn, email, hashed_password):
        return User(
            id=1,
            urn=urn,
            email=email,
            password=hashed_password,
            is_logged_in=True,
            created_on=datetime.datetime.now(),
            updated_on=datetime.datetime.now(),
        )

    @pytest.fixture
    def mock_logged_out_user(self, urn, email, hashed_password):
        return User(
            id=1,
            urn=urn,
            email=email,
            password=hashed_password,
            is_logged_in=True,
            created_on=datetime.datetime.now(),
            updated_on=datetime.datetime.now(),
        )

    async def test_successful_logout(
        self,
        mock_logged_in_user,
        mock_logged_out_user,
    ):
        ls = self.logout_service
        ls.user_repository.retrieve_record_by_id_is_logged_in = Mock(
            return_value=mock_logged_in_user
        )
        ls.user_repository.update_record = Mock(
            return_value=mock_logged_out_user
        )

        result = await ls.run()

        assert result.status == "SUCCESS"
        assert result.data["status"] == mock_logged_out_user.is_logged_in
