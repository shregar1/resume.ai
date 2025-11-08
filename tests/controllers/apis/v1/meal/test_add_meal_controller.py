import pytest

from http import HTTPStatus
from unittest.mock import Mock, AsyncMock, ANY

from constants.api_status import APIStatus

from dtos.requests.apis.v1.meal.add import AddMealRequestDTO
from dtos.responses.base import BaseResponseDTO

from errors.bad_input_error import BadInputError
from errors.not_found_error import NotFoundError
from errors.unexpected_response_error import UnexpectedResponseError

from controllers.apis.v1.meal.add import AddMealController

from tests.controllers.apis.v1.meal.test_meal_abstraction import (
    TestIV1MealAPIsController
)


@pytest.mark.asyncio
class TestAddMealAPIController(TestIV1MealAPIsController):

    @pytest.fixture
    def valid_add_meal_request_dto(
        self,
        reference_number,
        meal_name,
        servings,
        get_instructions_true,
    ):
        return AddMealRequestDTO(
            meal_name=meal_name,
            servings=servings,
            get_instructions=get_instructions_true,
            reference_number=reference_number,
        )

    @pytest.fixture
    def mock_add_meal_service(self):
        """Create a mock add meal service."""
        service = Mock()
        service.run = AsyncMock()
        return service

    @pytest.fixture
    def mock_add_meal_service_factory(self, mock_add_meal_service):
        """Create a mock add meal service factory."""
        factory = Mock()
        factory.return_value = mock_add_meal_service
        return factory

    @pytest.fixture
    def successful_response_dto(self, urn):
        """Create a successful response DTO."""
        return BaseResponseDTO(
            transactionUrn=urn,
            status=APIStatus.SUCCESS,
            responseMessage="Meal added successfully",
            responseKey="success_meal_added",
            data={"meal_id": 123, "meal_name": "test_meal"}
        )

    async def test_add_meal_api_controller_success(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_add_meal_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
    ):
        """Test successful meal addition."""

        controller = AddMealController()
        mock_service = AsyncMock()
        mock_service.run = AsyncMock(return_value=successful_response_dto)
        mock_add_meal_service_factory.return_value = mock_service

        response = await controller.post(
            request=mock_request,
            request_payload=valid_add_meal_request_dto,
            session=mock_session,
            meal_log_repository=mock_meal_log_repository_factory,
            add_meal_service_factory=mock_add_meal_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
        )

        assert response.status_code == HTTPStatus.OK
        assert mock_service.run.called
        assert mock_service.run.call_args[1]["request_dto"] == (
            valid_add_meal_request_dto
        )

    @pytest.mark.parametrize("invalid_servings", [-1, 0, 1001])
    async def test_add_meal_api_controller_invalid_servings(
        self,
        reference_number,
        meal_name,
        invalid_servings,
        get_instructions_true,
    ):
        """Test controller with invalid servings values."""
        with pytest.raises(Exception):
            AddMealRequestDTO(
                meal_name=meal_name,
                servings=invalid_servings,
                get_instructions=get_instructions_true,
                reference_number=reference_number,
            )

    @pytest.mark.parametrize("invalid_meal_name", ["", None, "a" * 1001])
    async def test_add_meal_api_controller_invalid_meal_name(
        self,
        invalid_meal_name,
        servings,
        get_instructions_true,
    ):
        """Test controller with invalid meal names."""
        with pytest.raises(Exception):
            AddMealRequestDTO(
                meal_name=invalid_meal_name,
                servings=servings,
                get_instructions=get_instructions_true,
                reference_number="123e4567-e89b-12d3-a456-426614174000",
            )

    async def test_add_meal_api_controller_bad_input_error(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_add_meal_service_factory,
        mock_dictionary_utility_factory,
    ):
        """Test handling of BadInputError."""

        controller = AddMealController()
        bad_input_error = BadInputError(
            responseMessage="Invalid meal data",
            responseKey="error_bad_input",
            httpStatusCode=HTTPStatus.BAD_REQUEST
        )
        mock_add_meal_service_factory.return_value.run = AsyncMock(
            side_effect=bad_input_error
        )

        response = await controller.post(
            request=mock_request,
            request_payload=valid_add_meal_request_dto,
            session=mock_session,
            meal_log_repository=mock_meal_log_repository_factory,
            add_meal_service_factory=mock_add_meal_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
        )

        assert response.status_code == bad_input_error.httpStatusCode
        response_content = response.body.decode()
        assert "Invalid meal data" in response_content
        assert "error_bad_input" in response_content

    async def test_add_meal_api_controller_not_found_error(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_add_meal_service_factory,
        mock_dictionary_utility_factory,
    ):
        """Test handling of NotFoundError."""

        controller = AddMealController()
        not_found_error = NotFoundError(
            responseMessage="Meal not found",
            responseKey="error_not_found",
            httpStatusCode=HTTPStatus.NOT_FOUND
        )
        mock_add_meal_service_factory.return_value.run = AsyncMock(
            side_effect=not_found_error
        )

        response = await controller.post(
            request=mock_request,
            request_payload=valid_add_meal_request_dto,
            session=mock_session,
            meal_log_repository=mock_meal_log_repository_factory,
            add_meal_service_factory=mock_add_meal_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
        )

        assert response.status_code == not_found_error.httpStatusCode
        response_content = response.body.decode()
        assert "Meal not found" in response_content
        assert "error_not_found" in response_content

    async def test_add_meal_api_controller_unexpected_response_error(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_add_meal_service_factory,
        mock_dictionary_utility_factory,
    ):

        controller = AddMealController()

        unexpected_response_error = UnexpectedResponseError(
            responseMessage="External API error",
            responseKey="error_external_api",
            httpStatusCode=HTTPStatus.BAD_GATEWAY,
        )
        mock_add_meal_service_factory.return_value.run = AsyncMock(
            side_effect=unexpected_response_error
        )
        await self.controller_post_unexpected_response_error(
            valid_add_meal_request_dto,
            mock_request,
            mock_session,
            mock_meal_log_repository_factory,
            mock_add_meal_service_factory,
            unexpected_response_error,
            mock_dictionary_utility_factory,
            controller,
        )

    async def test_add_meal_api_controller_generic_exception(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_add_meal_service_factory,
        mock_dictionary_utility_factory,
    ):
        # Ensure the dictionary utility mock is set up
        mock_dictionary_utility_factory.convert_dict_keys_to_camel_case = (
            Mock(return_value={})
        )
        controller = AddMealController()
        generic_error = Exception("Unexpected error")
        mock_add_meal_service_factory.return_value.run = AsyncMock(
            side_effect=generic_error
        )
        await self.controller_post_generic_exception(
            valid_add_meal_request_dto,
            mock_request,
            mock_session,
            mock_meal_log_repository_factory,
            mock_add_meal_service_factory,
            generic_error,
            mock_dictionary_utility_factory,
            controller,
        )

    async def test_add_meal_api_controller_missing_user_id(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_add_meal_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
    ):
        """
        Test controller behavior when user_id is missing from request state.
        """

        controller = AddMealController()
        delattr(mock_request.state, 'user_id')
        mock_add_meal_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        response = await controller.post(
            request=mock_request,
            request_payload=valid_add_meal_request_dto,
            session=mock_session,
            meal_log_repository=mock_meal_log_repository_factory,
            add_meal_service_factory=mock_add_meal_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
        )

        assert response.status_code == HTTPStatus.OK
        service_call_args = mock_add_meal_service_factory.call_args[1]
        assert service_call_args["user_id"] is None

    async def test_add_meal_api_controller_missing_user_urn(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_add_meal_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
    ):
        """
        Test controller behavior when user_urn is missing from request state.
        """

        controller = AddMealController()
        delattr(mock_request.state, 'user_urn')
        mock_add_meal_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        response = await controller.post(
            request=mock_request,
            request_payload=valid_add_meal_request_dto,
            session=mock_session,
            meal_log_repository=mock_meal_log_repository_factory,
            add_meal_service_factory=mock_add_meal_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
        )

        assert response.status_code == HTTPStatus.OK
        service_call_args = mock_add_meal_service_factory.call_args[1]
        assert service_call_args["user_urn"] is None

    async def test_add_meal_api_controller_dictionary_utility_called(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_add_meal_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
    ):
        """Test that dictionary utility is called to convert response keys."""
        controller = AddMealController()
        mock_add_meal_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        await controller.post(
            request=mock_request,
            request_payload=valid_add_meal_request_dto,
            session=mock_session,
            meal_log_repository=mock_meal_log_repository_factory,
            add_meal_service_factory=mock_add_meal_service_factory,
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
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_add_meal_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
        urn,
        user_urn,
        user_id,
    ):
        """Test that service factory is called with correct parameters."""

        controller = AddMealController()
        mock_add_meal_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        await controller.post(
            request=mock_request,
            request_payload=valid_add_meal_request_dto,
            session=mock_session,
            meal_log_repository=mock_meal_log_repository_factory,
            add_meal_service_factory=mock_add_meal_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
        )

        mock_add_meal_service_factory.assert_called_once_with(
            urn=urn,
            user_urn=user_urn,
            api_name="ADD_MEAL",
            user_id=user_id,
            meal_log_repository=mock_meal_log_repository_factory.return_value,
            cache=ANY,
        )

    async def test_repository_factory_called_with_correct_params(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        mock_meal_log_repository_factory,
        mock_add_meal_service_factory,
        mock_dictionary_utility_factory,
        successful_response_dto,
        urn,
        user_urn,
        user_id,
    ):
        """Test that repository factory is called with correct parameters."""
        controller = AddMealController()
        mock_add_meal_service_factory.return_value.run = AsyncMock(
            return_value=successful_response_dto
        )

        await controller.post(
            request=mock_request,
            request_payload=valid_add_meal_request_dto,
            session=mock_session,
            meal_log_repository=mock_meal_log_repository_factory,
            add_meal_service_factory=mock_add_meal_service_factory,
            dictionary_utility=mock_dictionary_utility_factory,
        )

        mock_meal_log_repository_factory.assert_called_once_with(
            urn=urn,
            user_urn=user_urn,
            api_name="ADD_MEAL",
            user_id=user_id,
            session=mock_session,
        )
