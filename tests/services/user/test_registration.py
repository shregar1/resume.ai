import datetime
import pytest

from unittest.mock import Mock

from constants.api_status import APIStatus
from dtos.requests.user.registration import UserRegistrationRequestDTO

from errors.bad_input_error import BadInputError
from models.user import User

from repositories.user import UserRepository

from services.user.registration import UserRegistrationService

from tests.services.user.test_user_abstraction import TestIUserService


@pytest.mark.asyncio
class TestUserRegistrationService(TestIUserService):
    @pytest.fixture(autouse=True)
    def setup(
        self,
        urn,
        user_urn,
        api_name,
        user_repository,
    ):
        self.user_repository: UserRepository = user_repository
        self.registration_service = UserRegistrationService(
            urn=urn,
            user_urn=user_urn,
            api_name=api_name,
            user_repository=self.user_repository,
        )

    @pytest.fixture
    def valid_registration_data(
        self,
        reference_number,
        email,
        password,
    ):
        return UserRegistrationRequestDTO(
            reference_number=reference_number,
            email=email,
            password=password,
        )

    @pytest.fixture
    def mock_registered_user(self, urn, email, hashed_password):
        return User(
            id=1,
            urn=urn,
            email=email,
            password=hashed_password,
            is_logged_in=False,
            created_on=datetime.datetime.now(),
            updated_on=datetime.datetime.now(),
        )

    @pytest.fixture
    def mock_existing_user(self, urn, email, hashed_password):
        return User(
            id=1,
            urn=urn,
            email=email,
            password=hashed_password,
            is_logged_in=False,
            created_on=datetime.datetime.now(),
            updated_on=datetime.datetime.now(),
        )

    async def test_successful_registration(
        self,
        valid_registration_data,
        mock_registered_user,
    ):
        service = self.registration_service
        service.user_repository.retrieve_record_by_email = Mock(
            return_value=None
        )
        service.user_repository.create_record = Mock(
            return_value=mock_registered_user
        )

        result = await service.run(valid_registration_data)

        assert result.status == APIStatus.SUCCESS
        assert result.data["user_email"] == mock_registered_user.email

    async def test_existing_user_registration(
        self,
        valid_registration_data,
        mock_existing_user,
    ):
        service = self.registration_service
        service.user_repository.retrieve_record_by_email = Mock(
            return_value=mock_existing_user
        )
        service.user_repository.create_record = Mock(
            return_value=None
        )

        with pytest.raises(BadInputError) as exc_info:
            await service.run(valid_registration_data)

        assert exc_info.value.responseKey == "error_email_already_registered"
        assert exc_info.value.responseMessage == "Email already registered."
