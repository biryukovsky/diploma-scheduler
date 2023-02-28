from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import scheduler
from scheduler.containers import Container
from scheduler.api.jobs import router as jobs_router
from scheduler.config import Settings
from scheduler.utils.exception import SchedulerException


def create_app():
    container = Container()
    container.config.from_pydantic(Settings())

    scheduler_manager = container.scheduler_manager()

    app = FastAPI()
    app.container = container
    app.container.wire(packages=[scheduler])

    app.include_router(jobs_router, prefix="/jobs")

    @app.exception_handler(SchedulerException)
    async def handle_app_exception(request: Request, exc: SchedulerException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.__class__.__name__, "message": str(exc)}
        )

    @app.on_event("startup")
    def start_scheduler():
        scheduler_manager.start()

    @app.on_event("shutdown")
    def stop_scheduler():
        scheduler_manager.stop()

    return app
