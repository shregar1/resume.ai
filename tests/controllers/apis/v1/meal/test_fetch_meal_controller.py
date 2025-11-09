import pytest

from http import HTTPStatus
from unittest.mock import Mock, AsyncMock, ANY

from constants.api_status import APIStatus

from controllers.apis.v1.meal.fetch import FetchMealController

from dtos.requests.apis.v1.meal.fetch import FetchMealRequestDTO
from dtos.responses.base import BaseResponseDTO

from errors.bad_input_error import BadInputError
from errors.not_found_error import NotFoundError
from errors.unexpected_response_error import UnexpectedResponseError

from tests.controllers.apis.v1.meal.test_meal_abstraction import (
    TestIV1MealAPIsController,
)


@pytest.mark.asyncio
class TestFetchMealAPIController(TestIV1MealAPIsController):

    @pytest.fixture
    def valid_fetch_meal_request_dto(
        self,
        reference_number,
        meal_name,
        servings,
        get_instructions_true,
    ):
        return FetchMealRequestDTO(
            meal_name=meal_name,
            servings=servings,
            get_instructions=get_instructions_true,
            reference_number=reference_number,
        )

    @pytest.fixture
    def mock_fetch_meal_service(self):
        """Create a mock fetch meal service."""
        service = Mock()
        service.run = AsyncMock()
        return service

    @pytest.fixture
    def mock_meal_log_repository_factory(self, mock_meal_log_repository):
        """Create a mock meal log repository factory."""
        factory = Mock()
        factory.return_value = mock_meal_log_repository
        return factory

    @pytest.fixture
    def mock_meal_log_repository(self):
        """Create a mock meal log repository."""
        return Mock()

    @pytest.fixture
    def mock_fetch_meal_service_factory(self, mock_fetch_meal_service):
        """Create a mock fetch meal service factory."""
        factory = Mock()
        factory.return_value = mock_fetch_meal_service
        return factory

    @pytest.fixture
    def successful_response_dto(self, urn):
        """Create a successful response DTO."""
        return BaseResponseDTO(
            transactionUrn=urn,
            status=APIStatus.SUCCESS,
            responseMessage="Meal fetched successfully",
            responseKey="success_fetch_meal",
            data={"meal_id": 123, "meal_name": "test_meal"}
        )

    async def test_fetch_meal_api_controller_success(
        self,
        valid_fetch_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
    ):
        """Test successful meal addition."""

        controller = FetchMealController()
        mock_service = AsyncMock()
        mock_service.run = AsyncMock(return_value=successful_response_dto)
        mock_fetch_meal_service_factory.return_value = mock_service

        response = await controller.get(
            request=mock_request,
            request_payload=valid_fetch_meal_request_dto,
            session=mock_session,
            cache=Mock(),
            meal_log_repository=mock_meal_log_repository_factory,
            fetch_meal_service_factory=mock_fetch_meal_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
        )

        assert response.status_code == HTTPStatus.OK
        assert mock_service.run.called
        assert mock_service.run.call_args[1]["request_dto"] == (
            valid_fetch_meal_request_dto
        )

    @pytest.mark.parametrize("invalid_servings", [-1, 0, 1001])
    async def test_fetch_meal_api_controller_invalid_servings(
        self,
        reference_number,
        meal_name,
        invalid_servings,
        get_instructions_true,
    ):
        """Test controller with invalid servings values."""
        with pytest.raises(Exception):
            FetchMealRequestDTO(
                meal_name=meal_name,
                servings=invalid_servings,
                get_instructions=get_instructions_true,
                reference_number=reference_number,
            )

    @pytest.mark.parametrize("invalid_meal_name", ["", None, "a" * 1001])
    async def test_fetch_meal_api_controller_invalid_meal_name(
        self,
        reference_number,
        invalid_meal_name,
        servings,
        get_instructions_true,
    ):
        """Test controller with invalid meal names."""
        with pytest.raises(Exception):
            FetchMealRequestDTO(
                meal_name=invalid_meal_name,
                servings=servings,
                get_instructions=get_instructions_true,
                reference_number=reference_number,
            )

    async def test_fetch_meal_api_controller_bad_input_error(
        self,
        valid_fetch_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_service_factory,
        mock_dictionary_utility_factory,
    ):
        """Test handling of BadInputError."""

        controller = FetchMealController()
        bad_input_error = BadInputError(
            responseMessage="Invalid meal data",
            responseKey="error_bad_input",
            httpStatusCode=HTTPStatus.BAD_REQUEST
        )
        await self.controller_get_bad_input_error(
            valid_fetch_meal_request_dto,
            mock_request,
            mock_session,
            mock_meal_log_repository_factory,
            mock_fetch_meal_service_factory,
            bad_input_error,
            mock_dictionary_utility_factory,
            controller,
        )

    async def test_fetch_meal_api_controller_not_found_error(
        self,
        valid_fetch_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_service_factory,
        mock_dictionary_utility_factory,
    ):
        """Test handling of NotFoundError."""

        controller = FetchMealController()
        not_found_error = NotFoundError(
            responseMessage="Meal not found",
            responseKey="error_not_found",
            httpStatusCode=HTTPStatus.NOT_FOUND
        )
        await self.controller_get_not_found_error(
            valid_fetch_meal_request_dto,
            mock_request,
            mock_session,
            mock_meal_log_repository_factory,
            mock_fetch_meal_service_factory,
            not_found_error,
            mock_dictionary_utility_factory,
            controller,
        )

    async def test_fetch_meal_api_controller_unexpected_response_error(
        self,
        valid_fetch_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_service_factory,
        mock_dictionary_utility_factory,
    ):
        """Test handling of UnexpectedResponseError."""
        # Arrange
        controller = FetchMealController()
        unexpected_error = UnexpectedResponseError(
            responseMessage="External API error",
            responseKey="error_external_api",
            httpStatusCode=HTTPStatus.BAD_GATEWAY
        )
        await self.controller_get_unexpected_response_error(
            valid_fetch_meal_request_dto,
            mock_request,
            mock_session,
            mock_meal_log_repository_factory,
            mock_fetch_meal_service_factory,
            unexpected_error,
            mock_dictionary_utility_factory,
            controller,
        )

    async def test_fetch_meal_api_controller_generic_exception(
        self,
        valid_fetch_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_service_factory,
        mock_dictionary_utility_factory,
    ):
        """Test handling of generic exceptions."""
        controller = FetchMealController()
        generic_error = Exception("Unexpected error")

        await self.controller_get_generic_exception(
            valid_fetch_meal_request_dto,
            mock_request,
            mock_session,
            mock_meal_log_repository_factory,
            mock_fetch_meal_service_factory,
            generic_error,
            mock_dictionary_utility_factory,
            controller,
        )

    async def test_fetch_meal_api_controller_missing_user_id(
        self,
        valid_fetch_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
    ):
        """
        Test controller behavior when user_id is missing from request state.
        """

        controller = FetchMealController()
        delattr(mock_request.state, 'user_id')
        mock_fetch_meal_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        response = await controller.get(
            request=mock_request,
            request_payload=valid_fetch_meal_request_dto,
            session=mock_session,
            meal_log_repository=mock_meal_log_repository_factory,
            fetch_meal_service_factory=mock_fetch_meal_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
        )

        assert response.status_code == HTTPStatus.OK
        service_call_args = mock_fetch_meal_service_factory.call_args[1]
        assert service_call_args["user_id"] is None

    async def test_fetch_meal_api_controller_missing_user_urn(
        self,
        valid_fetch_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
    ):
        """
        Test controller behavior when user_urn is missing from request state.
        """

        controller = FetchMealController()
        delattr(mock_request.state, 'user_urn')
        mock_fetch_meal_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        response = await controller.get(
            request=mock_request,
            request_payload=valid_fetch_meal_request_dto,
            session=mock_session,
            meal_log_repository=mock_meal_log_repository_factory,
            fetch_meal_service_factory=mock_fetch_meal_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
        )

        assert response.status_code == HTTPStatus.OK
        service_call_args = mock_fetch_meal_service_factory.call_args[1]
        assert service_call_args["user_urn"] is None

    async def test_fetch_meal_api_controller_dictionary_utility_called(
        self,
        valid_fetch_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
    ):

        controller = FetchMealController()
        mock_fetch_meal_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )
        await controller.get(
            request=mock_request,
            request_payload=valid_fetch_meal_request_dto,
            session=mock_session,
            cache=Mock(),
            meal_log_repository=mock_meal_log_repository_factory,
            fetch_meal_service_factory=mock_fetch_meal_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
        )
        utility = mock_dictionary_utility_factory.return_value
        utility.convert_dict_keys_to_camel_case.assert_called_once()
        call_args = utility.convert_dict_keys_to_camel_case.call_args[0][0]
        assert call_args["transactionUrn"] == (
            successful_response_dto.transactionUrn
        )
        assert call_args["status"] == successful_response_dto.status

    async def test_service_factory_called_with_correct_params(
        self,
        valid_fetch_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
        urn,
        user_urn,
        user_id,
    ):
        """Test that service factory is called with correct parameters."""

        controller = FetchMealController()
        mock_fetch_meal_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        await controller.get(
            request=mock_request,
            request_payload=valid_fetch_meal_request_dto,
            session=mock_session,
            cache=Mock(),
            meal_log_repository=mock_meal_log_repository_factory,
            fetch_meal_service_factory=mock_fetch_meal_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
        )

        mock_fetch_meal_service_factory.assert_called_once_with(
            urn=urn,
            user_urn=user_urn,
            api_name="SEARCH_MEAL",
            user_id=user_id,
            meal_log_repository=mock_meal_log_repository_factory.return_value,
            cache=ANY,
        )

    async def test_repository_factory_called_with_correct_params(
        self,
        valid_fetch_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_fetch_meal_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
        urn,
        user_urn,
        user_id,
    ):
        """Test that repository factory is called with correct parameters."""
        controller = FetchMealController()
        mock_fetch_meal_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        await controller.get(
            request=mock_request,
            request_payload=valid_fetch_meal_request_dto,
            session=mock_session,
            cache=Mock(),
            meal_log_repository=mock_meal_log_repository_factory,
            fetch_meal_service_factory=mock_fetch_meal_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
        )

        mock_meal_log_repository_factory.assert_called_once_with(
            urn=urn,
            user_urn=user_urn,
            api_name="SEARCH_MEAL",
            user_id=user_id,
            session=mock_session,
        )
