from fastapi import APIRouter

from .jobs import router as jobs_router
from .auth import router as auth_router


router = APIRouter(prefix="/api")
router.include_router(jobs_router, prefix="/jobs")
router.include_router(auth_router, prefix="/auth")
