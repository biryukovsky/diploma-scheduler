from fastapi import Request

from scheduler.web.exceptions import Unauthorized


def auth_required(request: Request):
    if "user" not in request.session:
        raise Unauthorized
