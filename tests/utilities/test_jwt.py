import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch
from jwt import PyJWTError

from start_utils import SECRET_KEY, ALGORITHM

from tests.utilities.test_utility_abstraction import TestIUtility

from utilities.jwt import JWTUtility


class TestJWTUtility(TestIUtility):

    @pytest.fixture
    def jwt_utility(self):
        """Create a JWT utility instance for testing."""
        return JWTUtility(
            urn="test-urn",
            user_urn="test-user-urn",
            api_name="TEST_API",
            user_id="123",
        )

    @pytest.fixture
    def sample_payload(self):
        """Create a sample payload for token creation."""
        return {"user_id": "123", "email": "test@example.com", "role": "user"}

    async def test_jwt_utility_initialization(self, jwt_utility):
        """Test JWT utility initialization with correct properties."""
        assert jwt_utility.urn == "test-urn"
        assert jwt_utility.user_urn == "test-user-urn"
        assert jwt_utility.api_name == "TEST_API"
        assert jwt_utility.user_id == "123"

    async def test_jwt_utility_property_setters(self, jwt_utility):
        """Test JWT utility property setters."""
        jwt_utility.urn = "new-urn"
        jwt_utility.user_urn = "new-user-urn"
        jwt_utility.api_name = "NEW_API"
        jwt_utility.user_id = "456"

        assert jwt_utility.urn == "new-urn"
        assert jwt_utility.user_urn == "new-user-urn"
        assert jwt_utility.api_name == "NEW_API"
        assert jwt_utility.user_id == "456"

    async def test_create_access_token_success(
        self,
        jwt_utility,
        sample_payload,
    ):
        """Test successful token creation."""
        token = jwt_utility.create_access_token(sample_payload)

        assert isinstance(token, str)
        assert len(token) > 0

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        for key, value in sample_payload.items():
            assert decoded[key] == value

        assert "exp" in decoded
        assert isinstance(decoded["exp"], int)

    async def test_create_access_token_with_expiration(
        self,
        jwt_utility,
        sample_payload,
    ):
        """Test token creation with expiration time."""
        token = jwt_utility.create_access_token(sample_payload)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        exp_timestamp = decoded["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        now = datetime.now()

        assert exp_datetime > now

        min_expiry = now - timedelta(minutes=5)
        assert exp_datetime > min_expiry

    async def test_create_access_token_without_expiration_config(
        self,
        sample_payload,
    ):
        """Test token creation when ACCESS_TOKEN_EXPIRE_MINUTES is None."""
        with patch("start_utils.ACCESS_TOKEN_EXPIRE_MINUTES", None):
            jwt_utility = JWTUtility()
            token = jwt_utility.create_access_token(sample_payload)

            decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            exp_timestamp = decoded["exp"]
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            now = datetime.now()

            assert exp_datetime > now

    async def test_create_access_token_preserves_original_data(
        self,
        jwt_utility,
    ):
        """Test that token creation doesn't modify the original payload."""
        original_payload = {
            "user_id": "123",
            "email": "test@example.com",
            "role": "user",
            "custom_field": "custom_value",
        }

        # Create a copy to compare later
        payload_copy = original_payload.copy()

        token = jwt_utility.create_access_token(original_payload)

        assert original_payload == payload_copy

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        for key, value in original_payload.items():
            assert decoded[key] == value

    async def test_decode_token_success(self, jwt_utility, sample_payload):
        """Test successful token decoding."""
        token = jwt_utility.create_access_token(sample_payload)

        decoded = jwt_utility.decode_token(token)

        for key, value in sample_payload.items():
            assert decoded[key] == value

        assert "exp" in decoded

    async def test_decode_token_invalid_signature(
        self,
        jwt_utility,
        sample_payload,
    ):
        """Test token decoding with invalid signature."""
        wrong_secret = "wrong_secret_key"
        token = jwt.encode(sample_payload, wrong_secret, algorithm=ALGORITHM)

        with pytest.raises(PyJWTError):
            jwt_utility.decode_token(token)

    async def test_decode_token_expired_token(
        self,
        jwt_utility,
        sample_payload,
    ):
        """Test decoding an expired token."""
        expired_payload = sample_payload.copy()
        expired_payload["exp"] = int(
            (datetime.now() - timedelta(hours=1)).timestamp()
        )

        token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)

        with pytest.raises(PyJWTError):
            jwt_utility.decode_token(token)

    async def test_decode_token_malformed_token(self, jwt_utility):
        """Test decoding a malformed token."""
        malformed_token = "not.a.valid.jwt.token"

        with pytest.raises(PyJWTError):
            jwt_utility.decode_token(malformed_token)

    async def test_decode_token_empty_string(self, jwt_utility):
        """Test decoding an empty token string."""
        with pytest.raises(PyJWTError):
            jwt_utility.decode_token("")

    async def test_decode_token_none_value(self, jwt_utility):
        """Test decoding None token."""
        with pytest.raises(PyJWTError):
            jwt_utility.decode_token(None)

    async def test_decode_token_wrong_algorithm(
        self,
        jwt_utility,
        sample_payload,
    ):
        """Test token decoding with wrong algorithm."""
        token = jwt.encode(sample_payload, SECRET_KEY, algorithm="HS256")

        try:
            decoded = jwt_utility.decode_token(token)
            assert decoded["user_id"] == sample_payload["user_id"]
        except PyJWTError:
            pass

    async def test_create_access_token_with_empty_payload(self, jwt_utility):
        """Test token creation with empty payload."""
        empty_payload = {}
        token = jwt_utility.create_access_token(empty_payload)

        assert isinstance(token, str)
        assert len(token) > 0

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded
        assert len(decoded) == 1

    async def test_create_access_token_with_nested_data(self, jwt_utility):
        """Test token creation with nested data structures."""
        nested_payload = {
            "user": {"id": "123", "profile": {"name": "John Doe", "age": 30}},
            "permissions": ["read", "write"],
            "metadata": {"created_at": "2024-01-01", "is_active": True},
        }

        token = jwt_utility.create_access_token(nested_payload)
        decoded = jwt_utility.decode_token(token)

        assert decoded["user"]["id"] == "123"
        assert decoded["user"]["profile"]["name"] == "John Doe"
        assert decoded["user"]["profile"]["age"] == 30
        assert decoded["permissions"] == ["read", "write"]
        assert decoded["metadata"]["created_at"] == "2024-01-01"
        assert decoded["metadata"]["is_active"] is True

    async def test_create_access_token_with_special_characters(
        self,
        jwt_utility,
    ):
        """Test token creation with special characters in payload."""
        special_payload = {
            "user_id": "user@123",
            "email": "test+tag@example.com",
            "name": "José María",
            "description": "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
        }

        token = jwt_utility.create_access_token(special_payload)
        decoded = jwt_utility.decode_token(token)

        assert decoded["user_id"] == "user@123"
        assert decoded["email"] == "test+tag@example.com"
        assert decoded["name"] == "José María"
        assert (
            decoded["description"]
            == "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        )

    async def test_decode_token_raises_correct_exception_type(
        self,
        jwt_utility,
    ):
        """Test that decode_token raises PyJWTError for invalid tokens."""
        invalid_tokens = [
            "invalid.token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            "not_even_close_to_jwt",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.qvwsd.invalid_signature",
        ]

        for invalid_token in invalid_tokens:
            with pytest.raises(PyJWTError):
                jwt_utility.decode_token(invalid_token)

    async def test_jwt_utility_inheritance(self, jwt_utility):
        """Test that JWT utility properly inherits from IUtility."""
        from abstractions.utility import IUtility

        assert isinstance(jwt_utility, IUtility)

    async def test_create_access_token_with_large_payload(self, jwt_utility):
        """Test token creation with a large payload."""
        large_payload = {
            "user_id": "123",
            "data": "x" * 1000,
            "array": list(range(100)),
            "nested": {
                "level1": {
                    "level2": {
                        "level3": {
                            "data": "deeply nested data",
                        },
                    },
                },
            },
        }

        token = jwt_utility.create_access_token(large_payload)
        decoded = jwt_utility.decode_token(token)

        assert decoded["user_id"] == "123"
        assert decoded["data"] == "x" * 1000
        assert len(decoded["array"]) == 100
        assert (
            decoded["nested"]["level1"]["level2"]["level3"]["data"]
            == "deeply nested data"
        )
