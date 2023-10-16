from enum import Enum

from fastapi import Request


class FlashCategory(Enum):
    primary = "primary"
    secondary = "secondary"
    success = "success"
    danger = "danger"
    warning = "warning"
    info = "info"


def flash(
    request: Request,
    message: str,
    category: FlashCategory = FlashCategory.primary,
) -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []

    request.session["_messages"].append({
        "message": message,
        "category": category.value
    })


def get_flashed_messages(request: Request):
    return request.session.pop("_messages", [])
