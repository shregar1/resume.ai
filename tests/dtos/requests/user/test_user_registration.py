import pytest

from pydantic import ValidationError

from dtos.requests.user.registration import UserRegistrationRequestDTO

from tests.dtos.requests.user.test_user_dto_abstractions import (
    TestIUserRequestDTO
)


@pytest.mark.asyncio
class TestRegistrationRequestDTO(TestIUserRequestDTO):

    async def test_user_registration_requests_dto_all_field_valid(
        self,
        reference_number,
        email,
        password,
    ):
        request_dto = UserRegistrationRequestDTO(
            reference_number=reference_number,
            email=email,
            password=password,
        )

        assert request_dto.reference_number == reference_number
        assert request_dto.email == email
        assert request_dto.password == password

    @pytest.mark.parametrize(
        ("field_name"), [
            ("reference_number"),
            ("email"),
            ("password"),
        ]
    )
    async def test_user_registration_parameter_none_error(
        self,
        field_name,
        reference_number,
        email,
        password,
    ):

        if field_name == "reference_number":
            reference_number = None
        elif field_name == "email":
            email = None
        elif field_name == "password":
            password = None

        with pytest.raises(ValidationError) as exc_info:
            UserRegistrationRequestDTO(
                reference_number=reference_number,
                email=email,
                password=password,
            )

        for error in exc_info.value.errors():
            assert error["input"] is None
            assert error["loc"] == (field_name,)
            assert (
                error["msg"] == 'Field required' or
                error["msg"] == "Input should be a valid string"
            )
            assert (
                error["type"] == "string_type" or
                error["type"] == "missing"
            )

    async def test_user_registration_requests_dto_all_none_error(self):

        with pytest.raises(ValidationError) as exc_info:
            UserRegistrationRequestDTO(
                reference_number=None,
                email=None,
                password=None,
            )

        assert len(exc_info.value.errors()) == 3
        for error in exc_info.value.errors():
            assert error["input"] is None
            assert error["loc"] == (error["loc"][0],)
            assert (
                error["msg"] == 'Field required' or
                error["msg"] == "Input should be a valid string"
            )
            assert (
                error["type"] == "string_type" or
                error["type"] == "missing"
            )
