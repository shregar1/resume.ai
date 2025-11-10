from http import HTTPStatus
from pydantic import BaseModel
from redis import Redis
from typing import Dict, Any

from constants.api_status import APIStatus
from constants.workflow_satus import WorkflowStatusConstant

from dtos.responses.base import BaseResponseDTO

from errors.bad_input_error import BadInputError
from errors.not_found_error import NotFoundError

from services.apis.v1.ranking_job.abstraction import IV1RankingJobService


class FetchRankingJobResultService(IV1RankingJobService):
    """
    Service for getting the results of a ranking job.
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
            
            job_data = self.redis_session.get(job_id)

            if not job_data:
                raise NotFoundError(
                    responseMessage="Job not found",
                    responseKey="error_job_not_found",
                    httpStatusCode=HTTPStatus.NOT_FOUND
                )

            if job_data["status"] != WorkflowStatusConstant.COMPLETED:
                raise BadInputError(
                    responseMessage=f"Job is not completed. Current status: {job_data['status']}",
                    responseKey="error_job_not_completed",
                    httpStatusCode=HTTPStatus.BAD_REQUEST
                )
            
            results = job_data.get("results", {})
            ranked_candidates = results.get("ranked_candidates", [])
            
            if request_dto.top_n:
                ranked_candidates = ranked_candidates[:request_dto.top_n]
            
            candidates = []
            for candidate in ranked_candidates:
                candidates.append({
                    "rank": candidate.get("rank"),
                    "candidate_name": candidate.get("candidate_name", "Unknown"),
                    "tier": candidate.get("tier"),
                    "total_score": candidate.get("scores", {}).get("total", 0),
                    "skills_score": candidate.get("scores", {}).get("skills_match", 0),
                    "experience_score": candidate.get("scores", {}).get("experience_relevance", 0),
                    "education_score": candidate.get("scores", {}).get("education_fit", 0),
                    "strengths": candidate.get("strengths", []),
                    "weaknesses": candidate.get("weaknesses", []),
                    "explanation": candidate.get("explanation", "")
                })
            
            response_payload: Dict[str, Any] = {
                "job_id": job_id,
                "job_title": results.get("jd_data", {}).get("job_title", ""),
                "total_candidates": results.get("total_candidates_ranked", 0),
                "tier_distribution": results.get("tier_distribution", {}),
                "candidates": candidates,
                "completed_at": results.get("completed_at")
            }

            return BaseResponseDTO(
                transactionUrn=self.urn,
                status=APIStatus.SUCCESS,
                responseMessage="Job results retrieved successfully",
                responseKey="success_job_results_retrieved",
                data=response_payload
            )

        except Exception as err:
            self.logger.error(f"Error getting ranking job results: {err}")
            raise err


