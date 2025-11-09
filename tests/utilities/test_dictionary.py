import pytest
from unittest.mock import Mock

from tests.utilities.test_utility_abstraction import TestIUtility

from utilities.dictionary import DictionaryUtility


class TestDictionaryUtility(TestIUtility):

    @pytest.fixture
    def dictionary_utility(self):
        """Create a DictionaryUtility instance for testing."""
        return DictionaryUtility(
            urn="test-urn",
            user_urn="test-user-urn",
            api_name="TEST_API",
            user_id="123",
        )

    @pytest.fixture
    def sample_dict(self):
        """Create a sample dictionary for testing."""
        return {
            "user_name": "john_doe",
            "email_address": "john@example.com",
            "phone_number": "123-456-7890",
            "nested_data": {
                "first_name": "John",
                "last_name": "Doe",
                "address_info": {
                    "street_name": "Main Street",
                    "city_name": "New York",
                },
            },
            "list_data": [
                {"item_name": "item1", "item_value": 100},
                {"item_name": "item2", "item_value": 200},
            ],
        }

    async def test_dictionary_utility_initialization(self, dictionary_utility):
        """Test DictionaryUtility initialization with correct properties."""
        assert dictionary_utility.urn == "test-urn"
        assert dictionary_utility.user_urn == "test-user-urn"
        assert dictionary_utility.api_name == "TEST_API"
        assert dictionary_utility.user_id == "123"

    async def test_dictionary_utility_property_setters(
        self,
        dictionary_utility,
    ):
        """Test DictionaryUtility property setters."""
        dictionary_utility.urn = "new-urn"
        dictionary_utility.user_urn = "new-user-urn"
        dictionary_utility.api_name = "NEW_API"
        dictionary_utility.user_id = "456"

        assert dictionary_utility.urn == "new-urn"
        assert dictionary_utility.user_urn == "new-user-urn"
        assert dictionary_utility.api_name == "NEW_API"
        assert dictionary_utility.user_id == "456"

    async def test_build_dictonary_with_key_success(self, dictionary_utility):
        """Test building dictionary with key from list of objects."""
        # Create mock objects
        obj1 = Mock()
        obj1.id = "user1"
        obj1.name = "John"

        obj2 = Mock()
        obj2.id = "user2"
        obj2.name = "Jane"

        records = [obj1, obj2]

        result = dictionary_utility.build_dictonary_with_key(records, "id")

        assert result["user1"] == obj1
        assert result["user2"] == obj2
        assert len(result) == 2

    async def test_build_dictonary_with_key_empty_list(
        self,
        dictionary_utility,
    ):
        """Test building dictionary with empty list."""
        result = dictionary_utility.build_dictonary_with_key([], "id")
        assert result == {}

    async def test_build_dictonary_with_key_missing_attribute(
        self,
        dictionary_utility
    ):
        """Test building dictionary with missing attribute."""
        class SimpleObject:
            def __init__(self, name):
                self.name = name

        obj1 = SimpleObject("John")

        records = [obj1]

        with pytest.raises(AttributeError):
            dictionary_utility.build_dictonary_with_key(records, "id")

    async def test_snake_to_camel_case_basic(self, dictionary_utility):
        """Test basic snake_case to camelCase conversion."""
        assert dictionary_utility.snake_to_camel_case("user_name") == (
            "userName"
        )
        assert dictionary_utility.snake_to_camel_case("email_address") == (
            "emailAddress"
        )
        assert dictionary_utility.snake_to_camel_case("phone_number") == (
            "phoneNumber"
        )

    async def test_snake_to_camel_case_single_word(self, dictionary_utility):
        """Test snake_case to camelCase with single word."""
        assert dictionary_utility.snake_to_camel_case("user") == "user"
        assert dictionary_utility.snake_to_camel_case("name") == "name"

    async def test_snake_to_camel_case_multiple_underscores(
        self,
        dictionary_utility,
    ):
        """Test snake_case to camelCase with multiple underscores."""
        assert (
            dictionary_utility.snake_to_camel_case("user_name_test")
            == "userNameTest"
        )
        assert (
            dictionary_utility.snake_to_camel_case("api_v1_user_data")
            == "apiV1UserData"
        )

    async def test_snake_to_camel_case_with_numbers(self, dictionary_utility):
        """Test snake_case to camelCase with numbers."""
        assert dictionary_utility.snake_to_camel_case("user_123") == "user123"
        assert dictionary_utility.snake_to_camel_case("api_v1") == "apiV1"

    async def test_convert_dict_keys_to_camel_case_basic(
        self,
        dictionary_utility,
    ):
        """Test basic dictionary key conversion to camelCase."""
        data = {"user_name": "john", "email_address": "john@example.com"}

        result = dictionary_utility.convert_dict_keys_to_camel_case(data)

        assert result["userName"] == "john"
        assert result["emailAddress"] == "john@example.com"
        assert "user_name" not in result
        assert "email_address" not in result

    async def test_convert_dict_keys_to_camel_case_nested(
        self, dictionary_utility, sample_dict
    ):
        """Test nested dictionary key conversion to camelCase."""
        result = dictionary_utility.convert_dict_keys_to_camel_case(
            sample_dict
        )

        assert "userName" in result
        assert "emailAddress" in result
        assert "phoneNumber" in result
        assert "nestedData" in result
        assert "listData" in result

        # Check nested dictionary
        nested = result["nestedData"]
        assert "firstName" in nested
        assert "lastName" in nested
        assert "addressInfo" in nested

        # Check deeply nested
        address = nested["addressInfo"]
        assert "streetName" in address
        assert "cityName" in address

        # Check list items
        list_data = result["listData"]
        assert len(list_data) == 2
        assert "itemName" in list_data[0]
        assert "itemValue" in list_data[0]

    async def test_convert_dict_keys_to_camel_case_with_lists(
        self,
        dictionary_utility,
    ):
        """Test dictionary key conversion with lists."""
        data = {
            "user_list": [
                {"user_name": "john", "email_address": "john@example.com"},
                {"user_name": "jane", "email_address": "jane@example.com"},
            ]
        }

        result = dictionary_utility.convert_dict_keys_to_camel_case(data)

        assert "userList" in result
        user_list = result["userList"]
        assert len(user_list) == 2

        assert "userName" in user_list[0]
        assert "emailAddress" in user_list[0]
        assert "userName" in user_list[1]
        assert "emailAddress" in user_list[1]

    async def test_convert_dict_keys_to_camel_case_non_dict(
        self,
        dictionary_utility,
    ):
        """Test conversion with non-dictionary data."""
        # String
        assert (
            dictionary_utility.convert_dict_keys_to_camel_case("hello")
            == "hello"
        )

        # Integer
        assert dictionary_utility.convert_dict_keys_to_camel_case(123) == 123

        # List of non-dicts
        data = ["hello", "world", 123]
        result = dictionary_utility.convert_dict_keys_to_camel_case(data)
        assert result == ["hello", "world", 123]

    async def test_camel_to_snake_case_basic(self, dictionary_utility):
        """Test basic camelCase to snake_case conversion."""
        assert (
            dictionary_utility.camel_to_snake_case("userName") == "user_name"
        )
        assert (
            dictionary_utility.camel_to_snake_case("emailAddress")
            == "email_address"
        )
        assert (
            dictionary_utility.camel_to_snake_case("phoneNumber")
            == "phone_number"
        )

    async def test_camel_to_snake_case_single_word(self, dictionary_utility):
        """Test camelCase to snake_case with single word."""
        assert dictionary_utility.camel_to_snake_case("user") == "user"
        assert dictionary_utility.camel_to_snake_case("name") == "name"

    async def test_camel_to_snake_case_with_numbers(self, dictionary_utility):
        """Test camelCase to snake_case with numbers."""
        assert dictionary_utility.camel_to_snake_case("user123") == "user123"
        assert dictionary_utility.camel_to_snake_case("apiV1") == "api_v1"

    async def test_camel_to_snake_case_complex(self, dictionary_utility):
        """Test camelCase to snake_case with complex cases."""
        assert (
            dictionary_utility.camel_to_snake_case("APIResponse")
            == "api_response"
        )
        assert dictionary_utility.camel_to_snake_case("userID") == "user_id"
        assert (
            dictionary_utility.camel_to_snake_case("JSONData") == "json_data"
        )

    async def test_convert_dict_keys_to_snake_case_basic(
        self,
        dictionary_utility,
    ):
        """Test basic dictionary key conversion to snake_case."""
        data = {"userName": "john", "emailAddress": "john@example.com"}

        result = dictionary_utility.convert_dict_keys_to_snake_case(data)

        assert result["user_name"] == "john"
        assert result["email_address"] == "john@example.com"
        assert "userName" not in result
        assert "emailAddress" not in result

    async def test_convert_dict_keys_to_snake_case_nested(
        self,
        dictionary_utility,
    ):
        """Test nested dictionary key conversion to snake_case."""
        data = {
            "userName": "john",
            "nestedData": {
                "firstName": "John",
                "lastName": "Doe",
                "addressInfo": {"streetName": "Main Street"},
            },
            "listData": [{"itemName": "item1", "itemValue": 100}],
        }

        result = dictionary_utility.convert_dict_keys_to_snake_case(data)

        assert "user_name" in result
        assert "nested_data" in result
        assert "list_data" in result

        nested = result["nested_data"]
        assert "first_name" in nested
        assert "last_name" in nested
        assert "address_info" in nested

        address = nested["address_info"]
        assert "street_name" in address

        list_data = result["list_data"]
        assert "item_name" in list_data[0]
        assert "item_value" in list_data[0]

    async def test_convert_dict_keys_to_snake_case_non_dict(
        self,
        dictionary_utility,
    ):
        """Test snake_case conversion with non-dictionary data."""

        assert (
            dictionary_utility.convert_dict_keys_to_snake_case("hello")
            == "hello"
        )
        assert dictionary_utility.convert_dict_keys_to_snake_case(123) == 123
        data = ["hello", "world", 123]
        result = dictionary_utility.convert_dict_keys_to_snake_case(data)
        assert result == ["hello", "world", 123]

    async def test_mask_value_string(self, dictionary_utility):
        """Test masking string values."""
        assert dictionary_utility.mask_value("hello") == "XXXXX"
        assert dictionary_utility.mask_value("password123") == "XXXXXXXXXXX"
        assert dictionary_utility.mask_value("") == ""

    async def test_mask_value_numbers(self, dictionary_utility):
        """Test masking numeric values."""
        assert dictionary_utility.mask_value(123) == 0
        assert dictionary_utility.mask_value(3.14) == 0.0
        assert dictionary_utility.mask_value(0) == 0

    async def test_mask_value_other_types(self, dictionary_utility):
        """Test masking other data types."""
        assert dictionary_utility.mask_value(True) == 0
        assert dictionary_utility.mask_value(None) is None
        assert dictionary_utility.mask_value([1, 2, 3]) == [1, 2, 3]

    async def test_mask_dict_values_basic(self, dictionary_utility):
        """Test basic dictionary value masking."""
        data = {
            "password": "secret123",
            "email": "user@example.com",
            "age": 25,
            "score": 95.5,
        }

        result = dictionary_utility.mask_dict_values(data)

        assert result["password"] == "XXXXXXXXX"
        assert result["email"] == "XXXXXXXXXXXXXXXX"
        assert result["age"] == 0
        assert result["score"] == 0.0

    async def test_mask_dict_values_nested(self, dictionary_utility):
        """Test nested dictionary value masking."""
        data = {
            "user": {
                "password": "secret123",
                "email": "user@example.com",
                "profile": {"phone": "123-456-7890", "ssn": "123-45-6789"},
            },
            "sensitive_data": ["password1", "password2"],
        }

        result = dictionary_utility.mask_dict_values(data)

        user = result["user"]
        assert user["password"] == "XXXXXXXXX"
        assert user["email"] == "XXXXXXXXXXXXXXXX"

        profile = user["profile"]
        assert profile["phone"] == "XXXXXXXXXXXX"
        assert profile["ssn"] == "XXXXXXXXXXX"

        sensitive_data = result["sensitive_data"]
        assert sensitive_data == ["XXXXXXXXX", "XXXXXXXXX"]

    async def test_mask_dict_values_with_lists(self, dictionary_utility):
        """Test dictionary value masking with lists."""
        data = {
            "passwords": ["pass1", "pass2", "pass3"],
            "numbers": [123, 456, 789],
            "mixed": ["text", 123, 45.6],
        }

        result = dictionary_utility.mask_dict_values(data)

        assert result["passwords"] == ["XXXXX", "XXXXX", "XXXXX"]
        assert result["numbers"] == [0, 0, 0]
        assert result["mixed"] == ["XXXX", 0, 0.0]

    async def test_remove_keys_from_dict_basic(self, dictionary_utility):
        """Test basic key removal from dictionary."""
        data = {
            "name": "John",
            "email": "john@example.com",
            "password": "secret123",
            "age": 25,
        }

        keys_to_remove = ["password", "email"]
        result = dictionary_utility.remove_keys_from_dict(data, keys_to_remove)

        assert "name" in result
        assert "age" in result
        assert "password" not in result
        assert "email" not in result
        assert len(result) == 2

    async def test_remove_keys_from_dict_nested(self, dictionary_utility):
        """Test key removal from nested dictionary."""
        data = {
            "user": {
                "name": "John",
                "email": "john@example.com",
                "password": "secret123",
                "profile": {
                    "phone": "123-456-7890",
                    "ssn": "123-45-6789",
                    "address": "123 Main St",
                },
            },
            "settings": {"theme": "dark", "password": "old_password"},
        }

        keys_to_remove = ["password", "ssn"]
        result = dictionary_utility.remove_keys_from_dict(data, keys_to_remove)

        user = result["user"]
        assert "name" in user
        assert "email" in user
        assert "password" not in user

        profile = user["profile"]
        assert "phone" in profile
        assert "address" in profile
        assert "ssn" not in profile

        settings = result["settings"]
        assert "theme" in settings
        assert "password" not in settings

    async def test_remove_keys_from_dict_with_lists(self, dictionary_utility):
        """Test key removal from dictionary with lists."""
        data = {
            "users": [
                {
                    "name": "John",
                    "password": "pass1",
                    "email": "john@example.com",
                },
                {
                    "name": "Jane",
                    "password": "pass2",
                    "email": "jane@example.com",
                },
            ],
        }

        keys_to_remove = ["password", "api_key"]
        result = dictionary_utility.remove_keys_from_dict(data, keys_to_remove)

        users = result["users"]
        assert len(users) == 2
        assert "name" in users[0]
        assert "email" in users[0]
        assert "password" not in users[0]
        assert "name" in users[1]
        assert "email" in users[1]
        assert "password" not in users[1]

        assert "users" in result
        assert "config" not in result

    async def test_remove_keys_from_dict_empty_keys(self, dictionary_utility):
        """Test key removal with empty keys list."""
        data = {"name": "John", "email": "john@example.com"}
        result = dictionary_utility.remove_keys_from_dict(data, [])

        assert result == data

    async def test_remove_keys_from_dict_non_dict(self, dictionary_utility):
        """Test key removal with non-dictionary data."""
        assert (
            dictionary_utility.remove_keys_from_dict("hello", ["key"])
            == "hello"
        )

        assert dictionary_utility.remove_keys_from_dict(123, ["key"]) == 123

        data = ["item1", "item2"]
        result = dictionary_utility.remove_keys_from_dict(data, ["key"])
        assert result == data

    async def test_dictionary_utility_inheritance(self, dictionary_utility):
        """Test that DictionaryUtility properly inherits from IUtility."""
        from abstractions.utility import IUtility

        assert isinstance(dictionary_utility, IUtility)

    async def test_round_trip_conversion(self, dictionary_utility):
        """
        Test round-trip conversion: snake_case -> camelCase -> snake_case.
        """
        original_data = {
            "user_name": "john",
            "email_address": "john@example.com",
            "nested_data": {"first_name": "John", "last_name": "Doe"},
        }

        camel_data = dictionary_utility.convert_dict_keys_to_camel_case(
            original_data
        )

        snake_data = dictionary_utility.convert_dict_keys_to_snake_case(
            camel_data
        )

        assert snake_data == original_data

    async def test_edge_cases(self, dictionary_utility):
        """Test various edge cases."""
        assert dictionary_utility.convert_dict_keys_to_camel_case({}) == {}
        assert dictionary_utility.convert_dict_keys_to_snake_case({}) == {}
        assert dictionary_utility.mask_dict_values({}) == {}
        assert dictionary_utility.remove_keys_from_dict({}, ["key"]) == {}

        data = {"key": None}
        assert (
            dictionary_utility.convert_dict_keys_to_camel_case(data)
            == {"key": None}
        )
        assert dictionary_utility.mask_dict_values(data) == {"key": None}

        data = {"is_active": True, "is_deleted": False}
        masked = dictionary_utility.mask_dict_values(data)
        assert masked["is_active"] == 0
        assert masked["is_deleted"] == 0
