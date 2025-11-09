import pytest

from http import HTTPStatus
from unittest.mock import Mock, AsyncMock, ANY

from constants.api_status import APIStatus

from controllers.apis.v1.meal.history import FetchMealHistoryController

from dtos.requests.apis.v1.meal.history import FetchMealHistoryRequestDTO
from dtos.responses.base import BaseResponseDTO

from errors.bad_input_error import BadInputError
from errors.not_found_error import NotFoundError
from errors.unexpected_response_error import UnexpectedResponseError

from tests.controllers.apis.v1.meal.test_meal_abstraction import (
    TestIV1MealAPIsController,
)


@pytest.mark.asyncio
class TestFetchMealHistoryAPIController(TestIV1MealAPIsController):

    @pytest.fixture
    def valid_fetch_meal_history_request_dto(
        self,
        reference_number,
    ):
        return FetchMealHistoryRequestDTO(
            reference_number=reference_number,
        )

    @pytest.fixture
    def mock_fetch_meal_history_service(self):
        """Create a mock fetch meal service."""
        service = Mock()
        service.run = AsyncMock()
        return service

    @pytest.fixture
    def mock_fetch_meal_history_service_factory(
        self,
        mock_fetch_meal_history_service
    ):
        """Create a mock fetch meal service factory."""
        factory = Mock()
        factory.return_value = mock_fetch_meal_history_service
        return factory

    @pytest.fixture
    def successful_response_dto(self, urn):
        """Create a successful response DTO."""
        return BaseResponseDTO(
            transactionUrn=urn,
            status=APIStatus.SUCCESS,
            responseMessage="Meal history fetched successfully",
            responseKey="success_fetch_meal_history",
            data={"meal_id": 123, "meal_name": "test_meal"}
        )

    async def test_fetch_meal_history_api_controller_success(
        self,
        valid_fetch_meal_history_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_history_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
    ):
        """Test successful meal history fetch."""

        controller = FetchMealHistoryController()
        mock_service = AsyncMock()
        mock_service.run = AsyncMock(return_value=successful_response_dto)
        mock_fetch_meal_history_service_factory.return_value = mock_service

        response = await controller.get(
            request=mock_request,
            reference_number=(
                valid_fetch_meal_history_request_dto.reference_number
            ),
            from_date=valid_fetch_meal_history_request_dto.from_date,
            to_date=valid_fetch_meal_history_request_dto.to_date,
            session=mock_session,
            cache=Mock(),
            meal_log_repository=mock_meal_log_repository_factory,
            fetch_meal_history_service_factory=(
                mock_fetch_meal_history_service_factory
            ),
            dictionary_utility=mock_dictionary_utility_factory,
        )

        assert response.status_code == HTTPStatus.OK
        assert mock_service.run.called
        assert mock_service.run.call_args[1]["request_dto"] == (
            valid_fetch_meal_history_request_dto
        )

    async def test_fetch_meal_history_api_controller_bad_input_error(
        self,
        valid_fetch_meal_history_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_history_service_factory,
        mock_dictionary_utility_factory,
    ):
        """Test handling of BadInputError."""

        controller = FetchMealHistoryController()
        bad_input_error = BadInputError(
            responseMessage="Invalid meal data",
            responseKey="error_bad_input",
            httpStatusCode=HTTPStatus.BAD_REQUEST
        )

        mock_fetch_meal_history_service_factory.return_value.run = AsyncMock(
            side_effect=bad_input_error
        )

        response = await controller.get(
            request=mock_request,
            reference_number=(
                valid_fetch_meal_history_request_dto.reference_number
            ),
            from_date=valid_fetch_meal_history_request_dto.from_date,
            to_date=valid_fetch_meal_history_request_dto.to_date,
            session=mock_session,
            cache=Mock(),
            meal_log_repository=mock_meal_log_repository_factory,
            fetch_meal_history_service_factory=(
                mock_fetch_meal_history_service_factory
            ),
            dictionary_utility=mock_dictionary_utility_factory,
        )

        assert response.status_code == bad_input_error.httpStatusCode
        response_content = response.body.decode()
        assert "Invalid meal data" in response_content
        assert "error_bad_input" in response_content

    async def test_fetch_meal_history_api_controller_not_found_error(
        self,
        valid_fetch_meal_history_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_history_service_factory,
        mock_dictionary_utility_factory,
    ):
        """Test handling of NotFoundError."""

        controller = FetchMealHistoryController()
        not_found_error = NotFoundError(
            responseMessage="Meal not found",
            responseKey="error_not_found",
            httpStatusCode=HTTPStatus.NOT_FOUND
        )

        mock_fetch_meal_history_service_factory.return_value.run = AsyncMock(
            side_effect=not_found_error
        )

        response = await controller.get(
            request=mock_request,
            reference_number=(
                valid_fetch_meal_history_request_dto.reference_number
            ),
            from_date=valid_fetch_meal_history_request_dto.from_date,
            to_date=valid_fetch_meal_history_request_dto.to_date,
            session=mock_session,
            meal_log_repository=mock_meal_log_repository_factory,
            fetch_meal_history_service_factory=(
                mock_fetch_meal_history_service_factory
            ),
            dictionary_utility=mock_dictionary_utility_factory,
        )

        assert response.status_code == not_found_error.httpStatusCode
        response_content = response.body.decode()
        assert "Meal not found" in response_content
        assert "error_not_found" in response_content

    async def test_fetch_meal_history_api_controller_unexpected_response_error(
        self,
        valid_fetch_meal_history_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_history_service_factory,
        mock_dictionary_utility_factory,
    ):
        """Test handling of UnexpectedResponseError."""
        # Arrange
        controller = FetchMealHistoryController()
        unexpected_error = UnexpectedResponseError(
            responseMessage="External API error",
            responseKey="error_external_api",
            httpStatusCode=HTTPStatus.BAD_GATEWAY
        )

        mock_fetch_meal_history_service_factory.return_value.run = AsyncMock(
            side_effect=unexpected_error
        )

        response = await controller.get(
            request=mock_request,
            reference_number=(
                valid_fetch_meal_history_request_dto.reference_number
            ),
            from_date=valid_fetch_meal_history_request_dto.from_date,
            to_date=valid_fetch_meal_history_request_dto.to_date,
            session=mock_session,
            meal_log_repository=mock_meal_log_repository_factory,
            fetch_meal_history_service_factory=(
                mock_fetch_meal_history_service_factory
            ),
            dictionary_utility=mock_dictionary_utility_factory,
        )

        assert response.status_code == unexpected_error.httpStatusCode
        response_content = response.body.decode()
        assert "External API error" in response_content
        assert "error_external_api" in response_content

    async def test_fetch_meal_history_api_controller_generic_exception(
        self,
        valid_fetch_meal_history_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_history_service_factory,
        mock_dictionary_utility_factory,
    ):
        """Test handling of generic exceptions."""
        controller = FetchMealHistoryController()
        generic_error = Exception("Unexpected error")

        mock_fetch_meal_history_service_factory.return_value.run = AsyncMock(
            side_effect=generic_error
        )

        response = await controller.get(
            request=mock_request,
            reference_number=(
                valid_fetch_meal_history_request_dto.reference_number
            ),
            from_date=valid_fetch_meal_history_request_dto.from_date,
            to_date=valid_fetch_meal_history_request_dto.to_date,
            session=mock_session,
            meal_log_repository=mock_meal_log_repository_factory,
            fetch_meal_history_service_factory=(
                mock_fetch_meal_history_service_factory
            ),
            dictionary_utility=mock_dictionary_utility_factory,
        )

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        response_content = response.body.decode()
        assert "Failed to fetch meal" in response_content
        assert "error_internal_server_error" in response_content

    async def test_fetch_meal_history_api_controller_missing_user_id(
        self,
        valid_fetch_meal_history_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_history_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
    ):
        """
        Test controller behavior when user_id is missing from request state.
        """

        controller = FetchMealHistoryController()
        delattr(mock_request.state, 'user_id')
        mock_fetch_meal_history_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        response = await controller.get(
            request=mock_request,
            reference_number=(
                valid_fetch_meal_history_request_dto.reference_number
            ),
            from_date=valid_fetch_meal_history_request_dto.from_date,
            to_date=valid_fetch_meal_history_request_dto.to_date,
            session=mock_session,
            meal_log_repository=mock_meal_log_repository_factory,
            fetch_meal_history_service_factory=(
                mock_fetch_meal_history_service_factory
            ),
            dictionary_utility=mock_dictionary_utility_factory,
        )

        assert response.status_code == HTTPStatus.OK
        service_call_args = (
            mock_fetch_meal_history_service_factory.call_args[1]
        )
        assert service_call_args["user_id"] is None

    async def test_fetch_meal_history_api_controller_missing_user_urn(
        self,
        valid_fetch_meal_history_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_history_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
    ):
        """
        Test controller behavior when user_urn is missing from request state.
        """

        controller = FetchMealHistoryController()
        delattr(mock_request.state, 'user_urn')
        mock_fetch_meal_history_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        response = await controller.get(
            request=mock_request,
            reference_number=(
                valid_fetch_meal_history_request_dto.reference_number
            ),
            from_date=valid_fetch_meal_history_request_dto.from_date,
            to_date=valid_fetch_meal_history_request_dto.to_date,
            session=mock_session,
            meal_log_repository=mock_meal_log_repository_factory,
            fetch_meal_history_service_factory=(
                mock_fetch_meal_history_service_factory
            ),
            dictionary_utility=mock_dictionary_utility_factory,
        )

        assert response.status_code == HTTPStatus.OK
        service_call_args = (
            mock_fetch_meal_history_service_factory.call_args[1]
        )
        assert service_call_args["user_urn"] is None

    async def test_fetch_meal_history_api_controller_dictionary_utility_called(
        self,
        valid_fetch_meal_history_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_history_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
    ):
        """Test that dictionary utility is called to convert response keys."""
        controller = FetchMealHistoryController()
        mock_fetch_meal_history_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        await controller.get(
            request=mock_request,
            reference_number=(
                valid_fetch_meal_history_request_dto.reference_number
            ),
            from_date=valid_fetch_meal_history_request_dto.from_date,
            to_date=valid_fetch_meal_history_request_dto.to_date,
            session=mock_session,
            meal_log_repository=mock_meal_log_repository_factory,
            fetch_meal_history_service_factory=(
                mock_fetch_meal_history_service_factory
            ),
            dictionary_utility=mock_dictionary_utility_factory,
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
        valid_fetch_meal_history_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_history_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
        urn,
        user_urn,
        user_id,
    ):
        """Test that service factory is called with correct parameters."""

        controller = FetchMealHistoryController()
        mock_fetch_meal_history_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        await controller.get(
            request=mock_request,
            reference_number=(
                valid_fetch_meal_history_request_dto.reference_number
            ),
            from_date=valid_fetch_meal_history_request_dto.from_date,
            to_date=valid_fetch_meal_history_request_dto.to_date,
            session=mock_session,
            cache=Mock(),
            meal_log_repository=mock_meal_log_repository_factory,
            fetch_meal_history_service_factory=(
                mock_fetch_meal_history_service_factory
            ),
            dictionary_utility=mock_dictionary_utility_factory,
        )

        mock_fetch_meal_history_service_factory.assert_called_once_with(
            urn=urn,
            user_urn=user_urn,
            api_name="MEAL_HISTORY",
            user_id=user_id,
            meal_log_repository=mock_meal_log_repository_factory.return_value,
            cache=ANY,
        )

    async def test_repository_factory_called_with_correct_params(
        self,
        valid_fetch_meal_history_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_history_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
        urn,
        user_urn,
        user_id,
    ):
        """Test that repository factory is called with correct parameters."""
        controller = FetchMealHistoryController()
        mock_fetch_meal_history_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        await controller.get(
            request=mock_request,
            reference_number=(
                valid_fetch_meal_history_request_dto.reference_number
            ),
            from_date=valid_fetch_meal_history_request_dto.from_date,
            to_date=valid_fetch_meal_history_request_dto.to_date,
            session=mock_session,
            cache=Mock(),
            meal_log_repository=mock_meal_log_repository_factory,
            fetch_meal_history_service_factory=(
                mock_fetch_meal_history_service_factory
            ),
            dictionary_utility=mock_dictionary_utility_factory,
        )

        mock_meal_log_repository_factory.assert_called_once_with(
            urn=urn,
            user_urn=user_urn,
            api_name="MEAL_HISTORY",
            user_id=user_id,
            session=mock_session,
        )
