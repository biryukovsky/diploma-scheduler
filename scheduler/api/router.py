from fastapi import APIRouter

from .jobs import router as jobs_router


router = APIRouter(prefix="/api")
router.include_router(jobs_router, prefix="/jobs")
