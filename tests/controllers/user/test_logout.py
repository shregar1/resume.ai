import pytest

from http import HTTPStatus
from unittest.mock import Mock, AsyncMock

from constants.api_status import APIStatus

from dtos.requests.user.logout import UserLogoutRequestDTO
from dtos.responses.base import BaseResponseDTO

from errors.bad_input_error import BadInputError
from errors.not_found_error import NotFoundError
from errors.unexpected_response_error import UnexpectedResponseError

from controllers.user.logout import UserLogoutController

from tests.controllers.user.test_user_abstraction import TestIUserController


@pytest.mark.asyncio
class TestUserLogoutAPIController(TestIUserController):

    @pytest.fixture
    def valid_user_logout_request_dto(
        self,
        reference_number,
    ):
        return UserLogoutRequestDTO(
            reference_number=reference_number,
        )

    @pytest.fixture
    def mock_user_logout_service(self):
        """Create a mock user logout service."""
        service = Mock()
        service.run = AsyncMock()
        return service

    @pytest.fixture
    def mock_user_logout_service_factory(self, mock_user_logout_service):
        """Create a mock user logout service factory."""
        factory = Mock()
        factory.return_value = mock_user_logout_service
        return factory

    @pytest.fixture
    def mock_user_repository_factory(self, mock_user_repository):
        """Create a mock user repository factory."""
        factory = Mock()
        factory.return_value = mock_user_repository
        return factory

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository."""
        return Mock()

    @pytest.fixture
    def mock_jwt_utility_factory(self, mock_jwt_utility):
        """Create a mock JWT utility factory."""
        factory = Mock()
        factory.return_value = mock_jwt_utility
        return factory

    @pytest.fixture
    def mock_jwt_utility(self):
        """Create a mock JWT utility."""
        return Mock()

    @pytest.fixture
    def successful_response_dto(self, urn):
        """Create a successful response DTO."""
        return BaseResponseDTO(
            transactionUrn=urn,
            status=APIStatus.SUCCESS,
            responseMessage="User logged out successfully",
            responseKey="success_user_logout",
            data={"user_id": 123, "logout_time": "2024-01-01T12:00:00Z"}
        )

    async def test_user_logout_api_controller_success(
        self,
        valid_user_logout_request_dto,
        mock_request,
        mock_session,
        mock_user_repository_factory,
        mock_user_logout_service_factory,
        mock_dictionary_utility_factory,
        mock_jwt_utility_factory,
        successful_response_dto,
    ):
        """Test successful user logout."""

        controller = UserLogoutController()
        mock_service = AsyncMock()
        mock_service.run = AsyncMock(return_value=successful_response_dto)
        mock_user_logout_service_factory.return_value = mock_service

        response = await controller.post(
            request=mock_request,
            request_payload=valid_user_logout_request_dto,
            session=mock_session,
            user_repository=mock_user_repository_factory,
            user_logout_service_factory=mock_user_logout_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
            jwt_utility=mock_jwt_utility_factory,
        )

        assert response.status_code == HTTPStatus.OK
        assert mock_service.run.called
        assert mock_service.run.call_args == ()

    async def test_user_logout_api_controller_bad_input_error(
        self,
        valid_user_logout_request_dto,
        mock_request,
        mock_session,
        mock_user_repository_factory,
        mock_user_logout_service_factory,
        mock_dictionary_utility_factory,
        mock_jwt_utility_factory,
    ):
        """Test handling of BadInputError."""

        controller = UserLogoutController()
        bad_input_error = BadInputError(
            responseMessage="Invalid logout request",
            responseKey="error_bad_input",
            httpStatusCode=HTTPStatus.BAD_REQUEST
        )
        mock_user_logout_service_factory.return_value.run = AsyncMock(
            side_effect=bad_input_error
        )

        response = await controller.post(
            request=mock_request,
            request_payload=valid_user_logout_request_dto,
            session=mock_session,
            user_repository=mock_user_repository_factory,
            user_logout_service_factory=mock_user_logout_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
            jwt_utility=mock_jwt_utility_factory,
        )

        assert response.status_code == bad_input_error.httpStatusCode
        response_content = response.body.decode()
        assert "Invalid logout request" in response_content
        assert "error_bad_input" in response_content

    async def test_user_logout_api_controller_not_found_error(
        self,
        valid_user_logout_request_dto,
        mock_request,
        mock_session,
        mock_user_repository_factory,
        mock_user_logout_service_factory,
        mock_dictionary_utility_factory,
        mock_jwt_utility_factory,
    ):
        """Test handling of NotFoundError."""

        controller = UserLogoutController()
        not_found_error = NotFoundError(
            responseMessage="User session not found",
            responseKey="error_not_found",
            httpStatusCode=HTTPStatus.NOT_FOUND
        )
        mock_user_logout_service_factory.return_value.run = AsyncMock(
            side_effect=not_found_error
        )

        response = await controller.post(
            request=mock_request,
            request_payload=valid_user_logout_request_dto,
            session=mock_session,
            user_repository=mock_user_repository_factory,
            user_logout_service_factory=mock_user_logout_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
            jwt_utility=mock_jwt_utility_factory,
        )

        assert response.status_code == not_found_error.httpStatusCode
        response_content = response.body.decode()
        assert "User session not found" in response_content
        assert "error_not_found" in response_content

    async def test_user_logout_api_controller_unexpected_response_error(
        self,
        valid_user_logout_request_dto,
        mock_request,
        mock_session,
        mock_user_repository_factory,
        mock_user_logout_service_factory,
        mock_dictionary_utility_factory,
        mock_jwt_utility_factory,
    ):
        """Test handling of UnexpectedResponseError."""
        # Arrange
        controller = UserLogoutController()
        unexpected_error = UnexpectedResponseError(
            responseMessage="External API error",
            responseKey="error_external_api",
            httpStatusCode=HTTPStatus.BAD_GATEWAY
        )
        mock_user_logout_service_factory.return_value.run = AsyncMock(
            side_effect=unexpected_error
        )

        response = await controller.post(
            request=mock_request,
            request_payload=valid_user_logout_request_dto,
            session=mock_session,
            user_repository=mock_user_repository_factory,
            user_logout_service_factory=mock_user_logout_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
            jwt_utility=mock_jwt_utility_factory,
        )

        assert response.status_code == unexpected_error.httpStatusCode
        response_content = response.body.decode()
        assert "External API error" in response_content
        assert "error_external_api" in response_content

    async def test_user_logout_api_controller_generic_exception(
        self,
        valid_user_logout_request_dto,
        mock_request,
        mock_session,
        mock_user_repository_factory,
        mock_user_logout_service_factory,
        mock_dictionary_utility_factory,
        mock_jwt_utility_factory,
    ):
        """Test handling of generic exceptions."""
        # Arrange
        controller = UserLogoutController()
        generic_error = Exception("Unexpected error")

        mock_user_logout_service_factory.return_value.run = AsyncMock(
            side_effect=generic_error
        )

        response = await controller.post(
            request=mock_request,
            request_payload=valid_user_logout_request_dto,
            session=mock_session,
            user_repository=mock_user_repository_factory,
            user_logout_service_factory=mock_user_logout_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
            jwt_utility=mock_jwt_utility_factory,
        )

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        response_content = response.body.decode()
        assert "Failed to logout user" in response_content
        assert "error_internal_server_error" in response_content

    async def test_user_logout_api_controller_dictionary_utility_called(
        self,
        valid_user_logout_request_dto,
        mock_request,
        mock_session,
        mock_user_repository_factory,
        mock_user_logout_service_factory,
        mock_dictionary_utility_factory,
        mock_jwt_utility_factory,
        successful_response_dto,
    ):
        """Test that dictionary utility is called to convert response keys."""
        controller = UserLogoutController()
        mock_user_logout_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        await controller.post(
            request=mock_request,
            request_payload=valid_user_logout_request_dto,
            session=mock_session,
            user_repository=mock_user_repository_factory,
            user_logout_service_factory=mock_user_logout_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
            jwt_utility=mock_jwt_utility_factory,
        )
        utility = mock_dictionary_utility_factory.return_value
        callable = utility.convert_dict_keys_to_camel_case
        callable.assert_called_once()
        call_args = (mock_dictionary_utility_factory.return_value
                     .convert_dict_keys_to_camel_case.call_args[0][0])
        assert call_args["transactionUrn"] == (
            successful_response_dto.transactionUrn
        )
        assert call_args["status"] == successful_response_dto.status

    async def test_service_factory_called_with_correct_params(
        self,
        valid_user_logout_request_dto,
        mock_request,
        mock_session,
        mock_user_repository_factory,
        mock_user_logout_service_factory,
        mock_dictionary_utility_factory,
        mock_jwt_utility_factory,
        successful_response_dto,
        urn,
    ):
        """Test that service factory is called with correct parameters."""

        controller = UserLogoutController()
        mock_user_logout_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        await controller.post(
            request=mock_request,
            request_payload=valid_user_logout_request_dto,
            session=mock_session,
            user_repository=mock_user_repository_factory,
            user_logout_service_factory=mock_user_logout_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
            jwt_utility=mock_jwt_utility_factory,
        )

        mock_user_logout_service_factory.assert_called_once_with(
            urn=urn,
            user_urn=mock_request.state.user_urn,
            api_name="LOGOUT",
            user_id=mock_request.state.user_id,
            jwt_utility=mock_jwt_utility_factory.return_value,
            user_repository=mock_user_repository_factory.return_value,
        )

    async def test_repository_factory_called_with_correct_params(
        self,
        valid_user_logout_request_dto,
        mock_request,
        mock_session,
        mock_user_repository_factory,
        mock_user_logout_service_factory,
        mock_dictionary_utility_factory,
        mock_jwt_utility_factory,
        successful_response_dto,
        urn,
    ):
        """Test that repository factory is called with correct parameters."""
        controller = UserLogoutController()
        mock_user_logout_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        await controller.post(
            request=mock_request,
            request_payload=valid_user_logout_request_dto,
            session=mock_session,
            user_repository=mock_user_repository_factory,
            user_logout_service_factory=mock_user_logout_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
            jwt_utility=mock_jwt_utility_factory,
        )

        mock_user_repository_factory.assert_called_once_with(
            urn=urn,
            user_urn=mock_request.state.user_urn,
            api_name="LOGOUT",
            user_id=mock_request.state.user_id,
            session=mock_session,
        )
