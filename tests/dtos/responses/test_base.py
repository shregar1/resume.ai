import pytest

from pydantic import ValidationError

from dtos.responses.base import BaseResponseDTO

from tests.dtos.responses.test_responses_abstractions import TestIResponsesDTO


@pytest.mark.asyncio
class TestBaseResponseDTO(TestIResponsesDTO):

    async def test_base_response_dto_all_field_valid(
        self,
        transaction_urn: str,
        status: str,
        response_message: str,
        response_key: str,
        errors: dict,
        data: str,
    ):
        response_dto = BaseResponseDTO(
            transactionUrn=transaction_urn,
            status=status,
            responseMessage=response_message,
            responseKey=response_key,
            errors=errors,
            data=data,
        )

        assert response_dto.transactionUrn == transaction_urn
        assert response_dto.status == status
        assert response_dto.responseMessage == response_message
        assert response_dto.responseKey == response_key
        assert response_dto.errors == errors
        assert response_dto.data == data

    async def test_base_response_dto_all_none_error(self):

        with pytest.raises(ValidationError) as exc_info:
            BaseResponseDTO(
                transactionUrn=None,
                status=None,
                responseMessage=None,
                responseKey=None,
                errors=None,
                data=None,
            )

        assert isinstance(exc_info.value.errors(), list)
        assert len(exc_info.value.errors()) == 4
        assert exc_info.value.errors()[0]["input"] is None
