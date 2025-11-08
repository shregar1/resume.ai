import pytest

from tests.services.test_service_abstraction import TestIService


@pytest.mark.asyncio
class TestIAPIsService(TestIService):
    pass
