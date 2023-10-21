import datetime as dt
import pathlib
import typing as t

from fastapi import APIRouter, Form, Request, Depends
from fastapi.datastructures import FormData
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dependency_injector.wiring import inject, Provide
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from scheduler.db import Database
from scheduler.models import User
from scheduler.web.dependencies.auth import auth_required
from scheduler.web.utils.flash import get_flashed_messages, flash, FlashCategory
from scheduler.modules.scheduler.job_registry import JOB_REGISTRY, JobName


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
templates.env.globals['get_flashed_messages'] = get_flashed_messages


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

    if password != password2:
        flash(request, "Пароли не совпадают", FlashCategory.danger)
        return RedirectResponse("/register")

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
            flash(request,
                  "Такой пользователь уже зарегистрирован",
                  FlashCategory.danger)
            return RedirectResponse("/register")

    request.session["user"] = {
        "id": user.id,
        "login": user.login,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }

    return RedirectResponse("/", status_code=302)


@router.get("/login", response_class=HTMLResponse)
async def render_login_page(request: Request):
    if "user" in request.session:
        referer = request.headers.get("Referer", "/")
        flash(request, "Вы уже вошли в учетную запись")
        return RedirectResponse(referer, status_code=302)
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

    if "user" in request.session:
        referer = request.headers.get("Referer", "/")
        flash(request, "Вы уже вошли в учетную запись")
        return RedirectResponse(referer, status_code=302)

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


@router.get("/create",
            response_class=HTMLResponse,
            dependencies=[Depends(auth_required)])
async def render_create_job_page(request: Request):
    renderable_jobs = [{
        "name": k,
        "display_name": v["display_name"]
    } for k, v in JOB_REGISTRY.items()]
    return templates.TemplateResponse("create_job.html", context={
        "request": request,
        "jobs": renderable_jobs,
    })


@router.post("/create", dependencies=[Depends(auth_required)])
@inject
async def create_job(request: Request):
    form = await request.form()

    # TODO: validate form

    params = parse_create_job_params(form)

    return RedirectResponse("/", status_code=302)


@router.get("/job_params/{job_name}", dependencies=[Depends(auth_required)])
async def get_job_params(job_name: JobName):
    response = []
    params = JOB_REGISTRY[job_name.value]["params"]
    type_map = {
        str: "text",
        list[str]: "text",
    }
    for param in params:
        param_data = {
            "name": param["name"],
            "display_name": param["display_name"],
            "type": type_map.get(param["type"], "text"),
            "is_list": "[]" in param["name"],
        }
        response.append(param_data)

    return response


def parse_create_job_params(form: FormData):
    data = {}
    job_name = form.get("name")
    params = JOB_REGISTRY[job_name]["params"]
    for param in params:
        key = param["name"]

        if '[]' in key:
            value = form.getlist(key)
        else:
            value = form[key]

        data[key] = value

    return data
