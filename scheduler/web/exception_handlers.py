from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from scheduler.web.exceptions import Unauthorized, AlreadyLoggedIn
from scheduler.web.utils.flash import flash, FlashCategory


def apply_exception_handlers(app: FastAPI):
    app.add_exception_handler(Unauthorized, handle_unauthorized)
    app.add_exception_handler(AlreadyLoggedIn, handle_logged_in)


def handle_unauthorized(request: Request, exc: Unauthorized):
    flash(request=request, message=exc.detail, category=FlashCategory.danger)
    return RedirectResponse(url="/")


def handle_logged_in(request: Request, exc: AlreadyLoggedIn):
    return RedirectResponse(url=exc.referer)
