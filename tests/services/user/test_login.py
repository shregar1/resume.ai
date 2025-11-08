import datetime
import pytest
import uuid

from unittest.mock import Mock

from errors.not_found_error import NotFoundError
from models.user import User
from repositories.user import UserRepository
from services.user.login import UserLoginService
from errors.bad_input_error import BadInputError
from dtos.requests.user.login import UserLoginRequestDTO

from tests.services.user.test_user_abstraction import TestIUserService


@pytest.mark.asyncio
class TestUserLoginService(TestIUserService):
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
        self.login_service: UserLoginService = UserLoginService(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_repository=self.user_repository,
            jwt_utility=mock_jwt_utility,
        )

    @pytest.fixture
    def valid_login_data(
        self,
        reference_number,
        email,
        password,
    ):
        return UserLoginRequestDTO(
            reference_number=reference_number,
            email=email,
            password=password,
        )

    @pytest.fixture
    def invalid_login_data(
        self,
        reference_number,
        email,
    ):
        return UserLoginRequestDTO(
            reference_number=reference_number,
            email=email,
            password="incorrect_password",
        )

    @pytest.fixture
    def mock_user(self, urn, email, hashed_password):
        return User(
            id=1,
            urn=urn,
            email=email,
            password=hashed_password,
            is_logged_in=True,
            created_on=datetime.datetime.now(),
            updated_on=datetime.datetime.now(),
        )

    async def test_successful_login(
        self,
        valid_login_data,
        mock_user,
        jwt_token,
    ):
        self.login_service.user_repository.retrieve_record_by_email = Mock(
            return_value=mock_user
        )
        self.login_service.user_repository.update_record = Mock(
            return_value=mock_user
        )
        self.login_service.jwt_utility.create_access_token = Mock(
            return_value=jwt_token
        )

        result = await self.login_service.run(valid_login_data)

        assert result.status == "SUCCESS"
        assert result.data["status"] == mock_user.is_logged_in
        assert result.data["token"] == jwt_token
        assert result.data["user_urn"] == mock_user.urn

    async def test_user_not_found(self):

        ls = self.login_service
        login_data = UserLoginRequestDTO(
            reference_number=str(uuid.uuid4()),
            email="nonexistent@test.com",
            password="AnyPassword123!",
        )

        ls.user_repository.retrieve_record_by_email = (
            Mock(return_value=None)
        )

        with pytest.raises(NotFoundError) as exc_info:
            await self.login_service.run(login_data)

        assert exc_info.value.responseKey == "error_authorisation_failed"
        assert exc_info.value.responseMessage == (
            "User not Found. Incorrect email."
        )

    async def test_incorrect_password(self, mock_user: User):

        ls = self.login_service
        login_data = UserLoginRequestDTO(
            reference_number=str(uuid.uuid4()),
            email="test@test.com",
            password="WrongPassword123!",
        )
        ls.user_repository.retrieve_record_by_email = (
            Mock(return_value=mock_user)
        )

        with pytest.raises(BadInputError) as exc_info:
            await self.login_service.run(login_data)

        assert exc_info.value.responseKey == "error_authorisation_failed"
        assert exc_info.value.responseMessage == "Incorrect password."

    async def test_login_updates_user_status(
        self,
        valid_login_data: UserLoginRequestDTO,
        mock_user: User,
        jwt_token: str,
    ):
        self.login_service.user_repository.retrieve_record_by_email = (
            Mock(return_value=mock_user)
        )
        self.login_service.user_repository.update_record = Mock(
            return_value=mock_user
        )
        self.login_service.jwt_utility.create_access_token = Mock(
            return_value=jwt_token
        )

        result = await self.login_service.run(valid_login_data)

        self.login_service.user_repository.update_record.assert_called_once()
        assert result.data["status"] == mock_user.is_logged_in
        assert result.data["token"] == jwt_token
        assert result.data["user_urn"] == mock_user.urn

    async def test_jwt_token_payload(
        self,
        valid_login_data: UserLoginRequestDTO,
        mock_user: User,
        jwt_token: str,
    ):
        ls = self.login_service
        ls.user_repository.retrieve_record_by_email = (
            Mock(return_value=mock_user)
        )
        ls.user_repository.update_record = Mock(
            return_value=mock_user
        )
        ls.jwt_utility.create_access_token = (
            Mock(return_value=jwt_token)
        )

        await ls.run(valid_login_data)

        expected_payload = {
            "user_id": mock_user.id,
            "user_urn": mock_user.urn,
            "user_email": mock_user.email,
            "last_login": str(mock_user.updated_on),
        }
        ls.jwt_utility.create_access_token.assert_called_once_with(
            data=expected_payload
        )
