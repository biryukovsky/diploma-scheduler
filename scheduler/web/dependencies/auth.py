from fastapi import Request

from scheduler.web.exceptions import Unauthorized, AlreadyLoggedIn
from scheduler.web.utils.flash import flash


def prevent_logged_in(request: Request):
    if "user" in request.session:
        referer = request.headers.get("Referer", "/")
        flash(request, "Вы уже вошли в учетную запись")
        raise AlreadyLoggedIn(referer=referer)


def auth_required(request: Request):
    if "user" not in request.session:
        raise Unauthorized
