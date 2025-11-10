import os

from datetime import datetime
from fastapi import BackgroundTasks
from pydantic import BaseModel
from redis import Redis
from typing import List, Dict

from constants.api_status import APIStatus
from constants.workflow_satus import WorkflowStatusConstant

from dtos.responses.base import BaseResponseDTO

from services.apis.v1.ranking_job.abstraction import IV1RankingJobService
from services.agents.orchestrator_agent import OrchestratorAgent


class CreateRankingJobService(IV1RankingJobService):
    """
    Service for creating a ranking job.
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
        self.orchestrator = OrchestratorAgent()
        self.redis_session = redis_session

    async def process_ranking_job(
        self,
        job_id: str,
        job_description: str,
        job_title: str,
        company: str,
        cv_files: List[Dict[str, str]]
    ):
        """Process ranking job in background.
        
        Args:
            job_id: Job ID
            job_description: Job description
            job_title: Job title
            company: Company name
            cv_files: List of CV file information
        """
        try:
            self.logger.info(f"Processing ranking job {job_id}")

            self.redis_session.set(job_id, {
                "status": WorkflowStatusConstant.PROCESSING,
                "created_at": datetime.now().isoformat(),
                "cv_count": len(cv_files),
                "job_title": job_title,
                "company": company
            })

            result = await self.orchestrator.process({
                "job_description": job_description,
                "job_title": job_title,
                "company": company,
                "cv_files": cv_files
            })
            
            if result.get("success"):
                self.redis_session.set(job_id, {
                    "status": WorkflowStatusConstant.COMPLETED,
                    "results": result,
                    "completed_at": datetime.now().isoformat(),
                    "job_title": job_title,
                    "company": company,
                    "cv_count": len(cv_files)
                })
                self.logger.info(f"Job {job_id} completed successfully")

            else:

                self.redis_session.set(job_id, {
                    "status": WorkflowStatusConstant.FAILED,
                    "error": result.get("error", "Unknown error"),
                    "completed_at": datetime.now().isoformat(),
                    "job_title": job_title,
                    "company": company,
                    "cv_count": len(cv_files)
                })
                self.logger.error(f"Job {job_id} failed: {result.get('error')}")

            for cv_file in cv_files:
                try:
                    os.remove(cv_file["file_path"])
                except Exception as e:
                    self.logger.warning(f"Could not delete file {cv_file['file_path']}: {e}")
        
        except Exception as e:
            self.logger.error(f"Error processing job {job_id}: {e}", exc_info=True)
            self.redis_session.set(job_id, {
                "status": WorkflowStatusConstant.FAILED,
                "error": str(e),
                "completed_at": datetime.now().isoformat(),
                "job_title": job_title,
                "company": company,
                "cv_count": len(cv_files)
            })

    def run(self, request_dto: BaseModel) -> BaseResponseDTO:

        try:
            
            job_data: Dict[str, str] = {
                "job_id": request_dto.job_id,
                "status": WorkflowStatusConstant.PROCESSING,
                "created_at": datetime.now().isoformat(),
                "cv_count": len(request_dto.saved_files),
                "job_title": request_dto.job_title,
                "company": request_dto.company
            }
            self.redis_session.set(request_dto.job_id, job_data)

            background_tasks: BackgroundTasks = request_dto.background_tasks or BackgroundTasks()
            background_tasks.add_task(
                self.process_ranking_job,
                request_dto.job_id,
                request_dto.job_description,
                request_dto.job_title,
                request_dto.company,
                request_dto.saved_files
            )
            self.logger.info(f"Ranking job {request_dto.job_id} created successfully")

            return BaseResponseDTO(
                transactionUrn=self.urn,
                status=APIStatus.SUCCESS,
                responseMessage="Ranking job created successfully",
                responseKey="success_ranking_job_created",
                data=job_data
            )

        except Exception as e:
            self.self.logger.error(f"Error creating ranking job: {e}")
            raise e
