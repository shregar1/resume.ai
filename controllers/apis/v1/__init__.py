from fastapi import APIRouter

from controllers.apis.v1.meal import router as meal_router


router = APIRouter(prefix="/v1")
router.include_router(meal_router)
