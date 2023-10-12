import datetime as dt
import pathlib
import typing as t

from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dependency_injector.wiring import inject, Provide
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from scheduler.db import Database
from scheduler.models import User


template_dir = pathlib.Path(__file__).parent / "templates"
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def user_context(request: Request) -> dict[str, t.Any]:
    user = request.session.get("user")
    if not user:
        return {}

    return {
        "user": user
    }


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=template_dir,
                            context_processors=[
                                user_context,
                            ])


@router.get("/register", response_class=HTMLResponse)
async def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", context={
        "request": request,
    })


@router.post("/register")
@inject
async def register(
    request: Request,
    login: t.Annotated[str, Form()],
    password: t.Annotated[str, Form()],
    password2: t.Annotated[str, Form()],
    first_name: t.Annotated[str, Form()],
    last_name: t.Annotated[str, Form()],
    db: Database = Depends(Provide["db"])
):
    """
    - check user not in db
    - hash password
    - store in db
    - set session
    - redirect to index
    """

    response = RedirectResponse("/", status_code=302)

    if password != password2:
        print("passwords don't match")
        return response

    async with db.session() as session:
        user = User(
            login=login,
            password=pwd_ctx.hash(password),
            first_name=first_name,
            last_name=last_name,
        )
        session.add(user)
        try:
            await session.commit()
            await session.refresh(user)
        except IntegrityError as e:
            print("user exists", e)
            return response

    request.session["user"] = {
        "login": user.login,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }

    return response


@router.get("/login", response_class=HTMLResponse)
async def render_login_page(request: Request):
    # TODO: reject logged in users
    return templates.TemplateResponse("login.html", context={
        "request": request,
    })


@router.post("/login", response_class=HTMLResponse)
@inject
async def login_user(
    request: Request,
    login: t.Annotated[str, Form()],
    password: t.Annotated[str, Form()],
    db: Database = Depends(Provide["db"])
):
    """
    - search in db by login
    - verify password
    - set session
    - redirect to index
    """

    # TODO: reject logged in users

    async with db.session() as session:
        query = select(User).where(User.login == login)
        user = (await session.execute(query)).scalar()
        if not user:
            print("user not found")
            return RedirectResponse("/login", status_code=302)

        if not pwd_ctx.verify(password, user.password):
            print("invalid password")
            return RedirectResponse("/login", status_code=302)

        request.session["user"] = {
            "login": user.login,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

    return RedirectResponse("/", status_code=302)


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)


@router.get("/", response_class=HTMLResponse)
async def render_index_page(request: Request):
    jobs = [
        {
            "id": 1,
            "name": "notify_students",
            "author": "Илья Бирюков",
            "next_run_time": dt.datetime(year=2023, month=10, day=10, hour=10)
        }
    ]
    return templates.TemplateResponse("index.html", context={
        "request": request,
        "jobs": jobs,
    })


@router.get("/create", response_class=HTMLResponse)
async def render_create_job_page(request: Request):
    return templates.TemplateResponse("create_job.html", context={
        "request": request,
    })


@router.post("/create")
async def create_job():
    return RedirectResponse("/", status_code=302)
