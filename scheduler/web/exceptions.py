from fastapi import HTTPException


class AlreadyLoggedIn(Exception):
    def __init__(self, referer: str, *args: object) -> None:
        self.referer = referer


class Unauthorized(HTTPException):
    def __init__(
        self,
        status_code=401,
        detail="Вы не авторизованы.",
        headers: dict[str, str] | None = None
    ) -> None:
        super().__init__(status_code, detail, headers)
