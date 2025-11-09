import pytest

from tests.dtos.test_dtos_abstraction import TestIDTO


@pytest.mark.asyncio
class TestIResponsesDTO(TestIDTO):

    @pytest.fixture
    def transaction_urn(self):
        return "test_transaction_urn"

    @pytest.fixture
    def status(self):
        return "test_status"

    @pytest.fixture
    def response_message(self):
        return "test_response_message"

    @pytest.fixture
    def response_key(self):
        return "test_response_key"

    @pytest.fixture
    def errors(self):
        return dict()

    @pytest.fixture
    def data(self):
        return list()
