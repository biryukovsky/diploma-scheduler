from fastapi import FastAPI

import scheduler
from scheduler.containers import Container
from scheduler.api.jobs import router as jobs_router
from scheduler.config import Settings


def create_app():
    container = Container()
    container.config.from_pydantic(Settings())

    scheduler_manager = container.scheduler_manager()

    app = FastAPI()
    app.container = container
    app.container.wire(packages=[scheduler])

    app.include_router(jobs_router, prefix="/jobs")

    @app.on_event("startup")
    def start_scheduler():
        scheduler_manager.start()

    @app.on_event("shutdown")
    def stop_scheduler():
        scheduler_manager.stop()

    return app
