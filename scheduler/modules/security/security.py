import datetime as dt

from sqlalchemy import select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dependency_injector.wiring import inject, Provide
from jose import JWTError, jwt
from passlib.context import CryptContext

from scheduler.config import SecuritySettings
from scheduler.db import Database
from scheduler.models import User
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


@inject
async def get_user_from_token(
    token: str = Depends(oauth_token),
    settings: SecuritySettings = Depends(Provide["config.security"]),
    db: Database = Depends(Provide["db"]),
) -> DisplayableUserResponse:
    try:
        payload = jwt.decode(
            token,
            key=settings["secret_key"],
            algorithms=settings["algorithm"],
        )
        if dt.datetime.fromtimestamp(payload["exp"]) < dt.datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async with db.session() as session:
        user = (await session.execute(select(User).where(User.login == payload["login"]))).scalar()

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
