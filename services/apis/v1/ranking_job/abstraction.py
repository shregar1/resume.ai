from pydantic import BaseModel

from dtos.responses.base import BaseResponseDTO

from services.apis.v1.abstraction import IV1APIService


class IV1RankingJobService(IV1APIService):
    """
    Abstract base class for v1 ranking job services.
    Provides shared logic for v1 ranking job endpoints.
    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: int = None,
    ) -> None:
        super().__init__(urn, user_urn, api_name, user_id)
        self.logger.debug(
            f"IV1RankingJobService initialized for "
            f"user_id={user_id}, urn={urn}, api_name={api_name}"
        )

    def run(self, request_dto: BaseModel) -> BaseResponseDTO:
        pass
