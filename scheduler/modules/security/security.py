import datetime as dt

from dependency_injector.wiring import inject, Provide
from jose import JWTError, jwt
from passlib.context import CryptContext

from scheduler.config import SecuritySettings


pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def verify_password(input_password: str, hashed_password: str) -> bool:
    return pwd_ctx.verify(input_password, hashed_password)


@inject
def create_access_token(
    data: dict,
    settings: dict = Provide["config.security"]
):
    to_encode = data.copy()
    exp = dt.datetime.utcnow() + dt.timedelta(settings["access_token_expire_minutes"])
    to_encode.update({"exp": exp})
    encoded_jwt = jwt.encode(to_encode, settings["secret_key"], algorithm=settings["algorithm"])
    return encoded_jwt


@inject
def create_refresh_token(
    data: dict,
    settings: SecuritySettings = Provide["config.security"]
):
    to_encode = data.copy()
    exp = dt.datetime.utcnow() + dt.timedelta(settings["refresh_token_expire_minutes"])
    to_encode.update({"exp": exp})
    encoded_jwt = jwt.encode(to_encode, settings["secret_key"], algorithm=settings["algorithm"])
    return encoded_jwt


def get_user_from_token(token: str, secret_key: str, algorithm: str):
    ...
