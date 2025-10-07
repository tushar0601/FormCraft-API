from fastapi import APIRouter
from app.routes.form import router as form_router
from app.routes.response import router as response_router
router = APIRouter()

router.include_router(form_router,prefix="/form",tags=["form"])
router.include_router(response_router,prefix="/response",tags=["response"])