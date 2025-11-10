from fastapi import APIRouter

from controllers.apis.v1.ranking_job import router as ranking_job_router


router = APIRouter(prefix="/v1")
router.include_router(ranking_job_router)
