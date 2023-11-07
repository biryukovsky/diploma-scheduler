from fastapi import HTTPException


class UserAlreadyExists(HTTPException):
    ...


class UserNotFound(HTTPException):
    ...


class IncorrectPassword(HTTPException):
    ...
