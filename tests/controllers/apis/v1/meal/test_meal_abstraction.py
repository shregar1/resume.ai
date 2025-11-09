from unittest.mock import Mock
import pytest

from datetime import datetime

from tests.controllers.apis.v1.test_v1_abstraction import TestIV1APIsController


@pytest.mark.asyncio
class TestIV1MealAPIsController(TestIV1APIsController):

    @pytest.fixture
    def meal_name(self):
        return "test meal"

    @pytest.fixture
    def servings(self):
        return 1

    @pytest.fixture
    def get_instructions_true(self):
        return True

    @pytest.fixture
    def get_instructions_false(self):
        return False

    @pytest.fixture
    def from_date(self):
        return datetime.strptime("2021-01-01", "%Y-%m-%d").date()

    @pytest.fixture
    def to_date(self):
        return datetime.strptime("2021-01-01", "%Y-%m-%d").date()

    @pytest.fixture
    def food_category(self):
        return "test food category"

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
