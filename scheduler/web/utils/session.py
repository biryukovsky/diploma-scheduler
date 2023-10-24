from fastapi import Request

from scheduler.models import User


def add_user_to_session(request: Request, user: User):
    request.session["user"] = {
        "id": user.id,
        "login": user.login,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }
