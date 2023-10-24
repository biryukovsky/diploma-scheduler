from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

import scheduler
from scheduler.containers import Container
from scheduler.api.router import router as api_router
from scheduler.web.views import router as web_router
from scheduler.web.exception_handlers import apply_exception_handlers as apply_web_exception_handlers
from scheduler.config import Settings
from scheduler.utils.exception import SchedulerException


def create_app():
    container = Container()
    container.config.from_pydantic(Settings())

    scheduler_manager = container.scheduler_manager()

    app = FastAPI(
        middleware=[
            Middleware(SessionMiddleware,
                       secret_key=container.config.security.secret_key())
        ]
    )
    app.container = container
    app.container.wire(packages=[scheduler])

    app.include_router(api_router)
    app.include_router(web_router)

    apply_web_exception_handlers(app)

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
