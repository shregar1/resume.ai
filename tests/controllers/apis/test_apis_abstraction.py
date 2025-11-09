import pytest

from http import HTTPStatus
from starlette.requests import Request
from unittest.mock import Mock, AsyncMock

from tests.controllers.test_controller_abstraction import TestIController

from utilities.dictionary import DictionaryUtility


@pytest.mark.asyncio
class TestIAPIsController(TestIController):

    @pytest.fixture
    def mock_request(self, urn, user_urn, user_id):
        """Create a mock FastAPI request with state."""
        request = Mock(spec=Request)
        request.state.urn = urn
        request.state.user_urn = user_urn
        request.state.user_id = user_id
        mock_headers = Mock()
        mock_headers.mutablecopy = Mock(
            return_value={"Content-Type": "application/json"}
        )
        request.headers = mock_headers
        request.method = "POST"
        request.url.path = "/api/v1/meal/add"
        return request

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def mock_dictionary_utility_factory(self, mock_dictionary_utility):
        """Create a mock dictionary utility factory."""
        factory = Mock()
        factory.return_value = mock_dictionary_utility
        return factory

    @pytest.fixture
    def mock_dictionary_utility(
        self,
        urn,
        user_urn,
        user_id,
        api_name
    ):
        """Create a mock dictionary utility."""
        utility = DictionaryUtility(
            urn=urn,
            user_urn=user_urn,
            user_id=user_id,
            api_name=api_name,
        )
        utility.convert_dict_keys_to_camel_case = Mock(
            side_effect=lambda x: x
        )
        return utility

    async def controller_post_bad_input_error(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        repository_factory,
        service_factory,
        error,
        mock_dictionary_utility_factory,
        controller,
    ):
        """Handling of BadInputError."""

        service_factory.return_value.run = AsyncMock(
            side_effect=error
        )

        response = await controller.post(
            mock_request,
            valid_add_meal_request_dto,
            mock_session,
            Mock(),
            repository_factory,
            service_factory,
            mock_dictionary_utility_factory,
        )

        assert response.status_code == error.httpStatusCode
        response_content = response.body.decode()
        assert "Invalid meal data" in response_content
        assert "error_bad_input" in response_content

    async def controller_get_bad_input_error(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        repository_factory,
        service_factory,
        error,
        mock_dictionary_utility_factory,
        controller,
    ):
        """Handling of BadInputError."""

        service_factory.return_value.run = AsyncMock(
            side_effect=error
        )

        response = await controller.get(
            mock_request,
            valid_add_meal_request_dto,
            mock_session,
            Mock(),
            repository_factory,
            service_factory,
            mock_dictionary_utility_factory,
        )

        assert response.status_code == error.httpStatusCode
        response_content = response.body.decode()
        assert "Invalid meal data" in response_content
        assert "error_bad_input" in response_content

    async def controller_post_not_found_error(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        repository_factory,
        service_factory,
        error,
        mock_dictionary_utility_factory,
        controller,
    ):
        """Handling of NotFoundError."""

        service_factory.return_value.run = AsyncMock(
            side_effect=error
        )

        response = await controller.post(
            mock_request,
            valid_add_meal_request_dto,
            mock_session,
            Mock(),
            repository_factory,
            service_factory,
            mock_dictionary_utility_factory,
        )

        assert response.status_code == error.httpStatusCode
        response_content = response.body.decode()
        assert "Meal not found" in response_content
        assert "error_not_found" in response_content

    async def controller_get_not_found_error(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        repository_factory,
        service_factory,
        error,
        mock_dictionary_utility_factory,
        controller,
    ):
        """Handling of NotFoundError."""

        service_factory.return_value.run = AsyncMock(
            side_effect=error
        )

        response = await controller.get(
            mock_request,
            valid_add_meal_request_dto,
            mock_session,
            Mock(),
            repository_factory,
            service_factory,
            mock_dictionary_utility_factory,
        )

        assert response.status_code == error.httpStatusCode
        response_content = response.body.decode()
        assert "Meal not found" in response_content
        assert "error_not_found" in response_content

    async def controller_post_unexpected_response_error(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        repository_factory,
        service_factory,
        error,
        mock_dictionary_utility_factory,
        controller,
    ):
        """Handling of UnexpectedResponseError."""

        service_factory.return_value.run = AsyncMock(
            side_effect=error
        )

        response = await controller.post(
            mock_request,
            valid_add_meal_request_dto,
            mock_session,
            Mock(),
            repository_factory,
            service_factory,
            mock_dictionary_utility_factory,
        )

        print("******************************************")
        print(response, error)
        print("******************************************")

        assert response.status_code == error.httpStatusCode
        response_content = response.body.decode()
        assert "External API error" in response_content
        assert "error_external_api" in response_content

    async def controller_get_unexpected_response_error(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        repository_factory,
        service_factory,
        error,
        mock_dictionary_utility_factory,
        controller,
    ):
        """Handling of UnexpectedResponseError."""

        service_factory.return_value.run = AsyncMock(
            side_effect=error
        )

        response = await controller.get(
            mock_request,
            valid_add_meal_request_dto,
            mock_session,
            Mock(),
            repository_factory,
            service_factory,
            mock_dictionary_utility_factory,
        )

        assert response.status_code == error.httpStatusCode
        response_content = response.body.decode()
        assert "External API error" in response_content
        assert "error_external_api" in response_content

    async def controller_post_generic_exception(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        repository_factory,
        service_factory,
        error,
        mock_dictionary_utility_factory,
        controller,
    ):
        """Handling of generic exceptions."""

        service_factory.return_value.run = AsyncMock(
            side_effect=error
        )

        response = await controller.post(
            mock_request,
            valid_add_meal_request_dto,
            mock_session,
            Mock(),
            repository_factory,
            service_factory,
            mock_dictionary_utility_factory,
        )

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        response_content = response.body.decode()
        assert "Failed to add meal" in response_content
        assert "error_internal_server_error" in response_content

    async def controller_get_generic_exception(
        self,
        valid_add_meal_request_dto,
        mock_request,
        mock_session,
        repository_factory,
        service_factory,
        error,
        mock_dictionary_utility_factory,
        controller,
    ):
        """Handling of generic exceptions."""

        service_factory.return_value.run = AsyncMock(
            side_effect=error
        )

        response = await controller.get(
            mock_request,
            valid_add_meal_request_dto,
            mock_session,
            Mock(),
            repository_factory,
            service_factory,
            mock_dictionary_utility_factory,
        )

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        response_content = response.body.decode()
        assert "Failed to fetch meal" in response_content
        assert "error_internal_server_error" in response_content
