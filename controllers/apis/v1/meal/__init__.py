from fastapi import APIRouter
from http import HTTPMethod

from constants.api_lk import APILK

from controllers.apis.v1.meal.add import AddMealController
from controllers.apis.v1.meal.fetch import FetchMealController
from controllers.apis.v1.meal.history import FetchMealHistoryController
from controllers.apis.v1.meal.recommendation import (
    FetchMealRecommendationController
)

from start_utils import logger


router = APIRouter(prefix="/meal")

logger.debug(f"Registering {AddMealController.__name__} route.")
router.add_api_route(
    path="/add",
    endpoint=AddMealController().post,
    methods=[HTTPMethod.POST.value],
    name=APILK.ADD_MEAL,
)
logger.debug(f"Registered {AddMealController.__name__} route.")

logger.debug(f"Registering {FetchMealController.__name__} route.")
router.add_api_route(
    path="/search",
    endpoint=FetchMealController().get,
    methods=[HTTPMethod.GET.value],
    name=APILK.SEARCH_MEAL,
)
logger.debug(f"Registered {FetchMealController.__name__} route.")

logger.debug(f"Registering {FetchMealHistoryController.__name__} route.")
router.add_api_route(
    path="/history",
    endpoint=FetchMealHistoryController().get,
    methods=[HTTPMethod.GET.value],
    name=APILK.MEAL_HISTORY,
)
logger.debug(f"Registered {FetchMealHistoryController.__name__} route.")

logger.debug(
    f"Registering {FetchMealRecommendationController.__name__} "
    f"route."
)
router.add_api_route(
    path="/recommendation",
    endpoint=FetchMealRecommendationController().get,
    methods=[HTTPMethod.GET.value],
    name=APILK.MEAL_RECOMMENDATION,
)
logger.debug(f"Registered {FetchMealRecommendationController.__name__} route.")
