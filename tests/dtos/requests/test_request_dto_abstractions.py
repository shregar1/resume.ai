import pytest
import uuid

from tests.dtos.test_dtos_abstraction import TestIDTO


@pytest.mark.asyncio
class TestIRequestDTO(TestIDTO):

    @pytest.fixture
    def reference_number(self):
        return str(uuid.uuid4())

    @pytest.fixture
    def parameter_none_error_factory(self):
        def _make_parameter_none_error(field_name, data_type, message_type):
            return [
                {
                    "type": data_type,
                    "loc": (field_name,),
                    "msg": f"Input should be a valid {message_type}",
                    "input": None,
                    "url": f"https://errors.pydantic.dev/2.11/v/{data_type}",
                }
            ]
        return _make_parameter_none_error
