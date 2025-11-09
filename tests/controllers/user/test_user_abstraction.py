import pytest
from unittest.mock import Mock

from tests.controllers.test_controller_abstraction import TestIController


@pytest.mark.asyncio
class TestIUserController(TestIController):

    @pytest.fixture
    def mock_request(self, urn, user_urn, user_id):
        """Create a mock request object."""
        request = Mock()
        request.state = Mock()
        request.state.urn = urn
        request.state.user_id = user_id
        request.state.user_urn = user_urn
        request.headers = Mock()
        request.headers.mutablecopy = Mock(return_value={})
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
    def mock_dictionary_utility(self):
        """Create a mock dictionary utility."""
        utility = Mock()
        utility.convert_dict_keys_to_camel_case = Mock(side_effect=lambda x: x)
        return utility
