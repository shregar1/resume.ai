from fastapi import APIRouter
from http import HTTPMethod

from constants.api_lk import APILK

from controllers.apis.v1.ranking_job.create import  CreateRankingJobController  
from controllers.apis.v1.ranking_job.status import  FetchRankingJobStatusController
from controllers.apis.v1.ranking_job.result import FetchRankingJobResultController

from start_utils import logger

router = APIRouter(prefix="/ranking_jobs")

logger.debug(f"Registering {CreateRankingJobController.__name__} route.")
router.add_api_route(
    path="/create",
    endpoint=CreateRankingJobController().post,
    methods=[HTTPMethod.POST.value],
    name=APILK.CREATE_RANKING_JOB,
)
logger.debug(f"Registered {CreateRankingJobController.__name__} route.")

logger.debug(f"Registering {FetchRankingJobStatusController.__name__} route.")
router.add_api_route(
    path="/{job_id}/status",
    endpoint=FetchRankingJobStatusController().get,
    methods=[HTTPMethod.POST.value],
    name=APILK.FETCH_RANKING_JOB_STATUS,
)
logger.debug(f"Registered {FetchRankingJobStatusController.__name__} route.")

logger.debug(f"Registering {FetchRankingJobResultController.__name__} route.")
router.add_api_route(
    path="/{job_id}/results",
    endpoint=FetchRankingJobResultController().get,
    methods=[HTTPMethod.GET.value],
    name=APILK.FETCH_RANKING_JOB_RESULT,
)
logger.debug(f"Registered {FetchRankingJobResultController.__name__} route.")
