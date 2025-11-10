import json
from http import HTTPStatus
from pydantic import BaseModel
from redis import Redis
from typing import Dict, Any


from constants.api_status import APIStatus

from dtos.responses.base import BaseResponseDTO

from errors.bad_input_error import BadInputError
from errors.not_found_error import NotFoundError

from services.apis.v1.ranking_job.abstraction import IV1RankingJobService


class FetchRankingJobStatusService(IV1RankingJobService):
    """
    Service for getting the status of a ranking job.
    """

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: int = None,
        redis_session: Redis = None
    ) -> None:
        super().__init__(urn, user_urn, api_name, user_id)

        if not redis_session:
            raise RuntimeError("Redis session not found")

        self.redis_session = redis_session

    def run(self, request_dto: BaseModel) -> BaseResponseDTO:

        try:
            job_id = request_dto.job_id
            if not job_id:
                raise BadInputError(
                    responseMessage="Job ID is required",
                    responseKey="error_job_id_required",
                    httpStatusCode=HTTPStatus.BAD_REQUEST
                )
            
            job_data_bytes = self.redis_session.get(job_id)

            if not job_data_bytes:
                raise NotFoundError(
                    responseMessage="Job not found",
                    responseKey="error_job_not_found",
                    httpStatusCode=HTTPStatus.NOT_FOUND
                )
            
            job_data = json.loads(job_data_bytes)
            
            response_payload: Dict[str, Any] = {
                "job_id": job_id,
                "status": job_data["status"],
                "created_at": job_data.get("created_at"),
                "completed_at": job_data.get("completed_at"),
                "cv_count": job_data.get("cv_count", 0),
                "error": job_data.get("error")
            }

            return BaseResponseDTO(
                transactionUrn=self.urn,
                status=APIStatus.SUCCESS,
                responseMessage="Job status retrieved successfully",
                responseKey="success_job_status_retrieved",
                data=response_payload
            )

        except Exception as err:
            self.logger.error(f"Error creating ranking job: {err}")
            raise err
