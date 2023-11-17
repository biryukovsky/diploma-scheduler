import datetime as dt

from sqlalchemy import select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dependency_injector.wiring import inject, Provide
from jose import JWTError, jwt
from passlib.context import CryptContext

from scheduler.config import SecuritySettings
from scheduler.modules.security.repository import UserRepository
from scheduler.modules.security.schemas import DisplayableUserResponse


pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_token = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    scheme_name="JWT",
)


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


def _raise_unauthorized(message: str):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _get_token_payload(token: str, secret_key: str, algorithm: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            key=secret_key,
            algorithms=algorithm,
        )
        if dt.datetime.fromtimestamp(payload["exp"]) < dt.datetime.utcnow():
            _raise_unauthorized("Token expired")
        if "sub" not in payload:
            _raise_unauthorized("Could not validate credentials")
    except JWTError:
        _raise_unauthorized("Could not validate credentials")

    return payload


@inject
async def get_user_from_token(
    token: str = Depends(oauth_token),
    settings: SecuritySettings = Depends(Provide["config.security"]),
    user_repo: UserRepository = Depends(Provide["user_repo"]),
) -> DisplayableUserResponse:
    payload = _get_token_payload(token, settings["secret_key"], settings["algorithm"])

    user = await user_repo.get_user_by_login(payload["sub"])

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return DisplayableUserResponse(
        login=user.login,
        first_name=user.first_name,
        last_name=user.last_name,
    )
