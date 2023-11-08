from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from dependency_injector.wiring import inject, Provide
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from scheduler.db import Database
from scheduler.models import User
from scheduler.modules.security.schemas import (
    RegisterRequest,
    AuthResponse,
    DisplayableUserResponse,
    TokenData,
)
from scheduler.modules.security.exceptions import (
    UserAlreadyExists,
    UserNotFound,
    IncorrectPassword,
)
from scheduler.modules.security.security import (
    create_access_token,
    create_refresh_token,
    get_user_from_token,
    verify_password,
    hash_password,
)


router = APIRouter(tags=["auth"])


@router.post("/register", response_model=AuthResponse)
@inject
async def register(
    register_data: RegisterRequest,
    db: Database = Depends(Provide["db"])
):
    async with db.session() as session:
        user = User(
            login=register_data.login,
            password=hash_password(register_data.password),
            first_name=register_data.first_name,
            last_name=register_data.last_name,
        )
        session.add(user)
        try:
            await session.commit()
            await session.refresh(user)
        except IntegrityError as e:
            raise UserAlreadyExists(status_code=400, detail=f"Пользователь с логином `{register_data.login}` уже зарегистрирован") from e

    token_payload = {
        "user_id": user.id,
        "login": user.login,
    }
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)

    return AuthResponse(
        user=DisplayableUserResponse(
            login=user.login,
            first_name=user.first_name,
            last_name=user.last_name
        ),
        token_data=TokenData(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
    )


@router.post("/login", response_model=TokenData)
@inject
async def login(
    login_data: OAuth2PasswordRequestForm = Depends(),
    db: Database = Depends(Provide["db"])
):
    async with db.session() as session:
        query = select(User).where(User.login == login_data.username)
        user = (await session.execute(query)).scalar()
        if not user:
            raise UserNotFound(
                status_code=404,
                detail=f"Пользователь `{login_data.username}` не существует"
            )

        if not verify_password(login_data.password, user.password):
            raise IncorrectPassword(status_code=403, detail="Неверный пароль")

    token_payload = {
        "user_id": user.id,
        "login": user.login,
    }
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)

    return TokenData(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/me")
async def get_me(user: DisplayableUserResponse = Depends(get_user_from_token)):
    return user
