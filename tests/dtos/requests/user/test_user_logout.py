import pytest

from pydantic import ValidationError

from dtos.requests.user.logout import UserLogoutRequestDTO

from tests.dtos.requests.user.test_user_dto_abstractions import (
    TestIUserRequestDTO
)


@pytest.mark.asyncio
class TestLogoutRequestDTO(TestIUserRequestDTO):

    async def test_user_logout_requests_dto_all_field_valid(
        self,
        reference_number,
    ):
        request_dto = UserLogoutRequestDTO(
            reference_number=reference_number
        )

        assert request_dto.reference_number == reference_number

    @pytest.mark.parametrize(
        ("field_name"), [
            ("reference_number")
        ]
    )
    async def test_user_logout_parameter_none_error(
        self,
        field_name,
        reference_number,
    ):

        if field_name == "reference_number":
            reference_number = None

        with pytest.raises(ValidationError) as exc_info:
            UserLogoutRequestDTO(
                reference_number=reference_number,
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

    async def test_user_logout_requests_dto_all_none_error(self):

        with pytest.raises(ValidationError) as exc_info:
            UserLogoutRequestDTO(
                reference_number=None,
            )

        assert len(exc_info.value.errors()) == 1
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
