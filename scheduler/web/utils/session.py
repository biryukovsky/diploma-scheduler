from fastapi import Request

from scheduler.models import User
from scheduler.web.exceptions import AlreadyLoggedIn
from .flash import flash


def prevent_logged_in(request: Request):
    if "user" in request.session:
        referer = request.headers.get("Referer", "/")
        flash(request, "Вы уже вошли в учетную запись")
        raise AlreadyLoggedIn(referer=referer)


def add_user_to_session(request: Request, user: User):
    request.session["user"] = {
        "id": user.id,
        "login": user.login,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }
