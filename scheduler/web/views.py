import datetime as dt
import pathlib
import typing as t
from uuid import UUID

from fastapi import APIRouter, Form, Request, Depends
from fastapi.datastructures import FormData
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dependency_injector.wiring import inject, Provide
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from scheduler.db import Database
from scheduler.models import User
from scheduler.modules.scheduler.repository import JobRepository
from scheduler.modules.scheduler.services import SchedulerManager
from scheduler.modules.scheduler.job_registry import JOB_REGISTRY, JobName
from scheduler.modules.scheduler.schemas import DateJobTrigger
from scheduler.web.schemas import CreateJobRequest
from scheduler.web.dependencies.auth import auth_required, prevent_logged_in
from scheduler.web.utils.flash import get_flashed_messages, flash, FlashCategory
from scheduler.web.utils.session import add_user_to_session
from scheduler.modules.security.security import hash_password, verify_password


template_dir = pathlib.Path(__file__).parent / "templates"


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


@router.get("/register",
            response_class=HTMLResponse,
            dependencies=[Depends(prevent_logged_in)])
async def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", context={
        "request": request,
    })


@router.post("/register",
             dependencies=[Depends(prevent_logged_in)])
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
            password=hash_password(password),
            first_name=first_name,
            last_name=last_name,
        )
        session.add(user)
        try:
            await session.commit()
            await session.refresh(user)
        except IntegrityError:
            flash(request,
                  "Такой пользователь уже зарегистрирован",
                  FlashCategory.danger)
            return RedirectResponse("/register")

    add_user_to_session(request, user)

    return RedirectResponse("/", status_code=302)


@router.get("/login",
            response_class=HTMLResponse,
            dependencies=[Depends(prevent_logged_in)])
async def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", context={
        "request": request,
    })


@router.post("/login",
             response_class=HTMLResponse,
             dependencies=[Depends(prevent_logged_in)])
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

    async with db.session() as session:
        query = select(User).where(User.login == login)
        user = (await session.execute(query)).scalar()
        if not user:
            flash(request, "Такого пользоваотеля не существует", FlashCategory.danger)
            return RedirectResponse("/login", status_code=302)

        if not verify_password(password, user.password):
            flash(request, "Неверный пароль", FlashCategory.danger)
            return RedirectResponse("/login", status_code=302)

        add_user_to_session(request, user)

    return RedirectResponse("/", status_code=302)


@router.get("/logout",
            response_class=HTMLResponse,
            dependencies=[Depends(auth_required)])
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)


@router.get("/", response_class=HTMLResponse)
@inject
async def render_index_page(
    request: Request,
    job_repo: JobRepository = Depends(Provide["job_repo"]),
    scheduler_manager: SchedulerManager = Depends(Provide["scheduler_manager"]),
):
    jobs = [
        {
            "id": 1,
            "name": "notify_students",
            "author": "Илья Бирюков",
            "next_run_time": dt.datetime(year=2023, month=10, day=10, hour=10)
        }
    ]
    apscheduler_jobs = scheduler_manager.get_jobs()
    apscheduer_job_ids = [j.id for j in apscheduler_jobs]

    jobs = await job_repo.get_jobs_by_apscheduler_ids(apscheduer_job_ids)

    renderable_jobs = []
    # TODO: не зипать, так как может нарушиться порядок
    for ap_job, job in zip(apscheduler_jobs, jobs):
        renderable_jobs.append({
            "id": job.id,
            "name": JOB_REGISTRY[JobName(ap_job.name).value]["display_name"],
            "author": f"{job.author.first_name} {job.author.last_name}".strip() or job.author.login,
            "description": job.description,
            "next_run_time": ap_job.next_run_time,
        })

    return templates.TemplateResponse("index.html", context={
        "request": request,
        "jobs": renderable_jobs,
    })


@router.post("/delete-job/{job_id}", dependencies=[Depends(auth_required)])
@inject
async def delete_job(
    job_id: UUID,
    job_repo: JobRepository = Depends(Provide["job_repo"]),
    scheduler_manager: SchedulerManager = Depends(Provide["scheduler_manager"]),
):
    """
    TODO:
        - select job
        - delete job from scheduler by scheduler_job_id
        - delete job from job table
    """
    job = await job_repo.get_job_by_id(job_id)
    await job_repo.delete_job(job_id)
    scheduler_manager.delete_job(job.scheduler_job_id)
    return RedirectResponse("/", status_code=302)


@router.get("/job/{job_name}",
            response_class=HTMLResponse,
            dependencies=[Depends(auth_required)])
@inject
async def render_job_page(request: Request, job_name: str):
    """
    - get job by name from db
    - render useful fields
    """
    return templates.TemplateResponse("job.html", context={
        "request": request,
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
async def create_job(
    request: Request,
    job_repo: JobRepository = Depends(Provide["job_repo"]),
    scheduler_manager: SchedulerManager = Depends(Provide["scheduler_manager"]),
):
    """
    job params is dynamic so we can't use `Form()` args
    """

    form = await request.form()

    request_data = CreateJobRequest.parse_obj(form)

    params = parse_create_job_params(form)

    scheduler_job = scheduler_manager.add_job(
        request_data.name,
        trigger=DateJobTrigger(
            trigger_name="date",
            run_date=request_data.next_run_time
        ).to_apscheduler_trigger(),
        **params,
    )
    await job_repo.create_job(
        author_id=request.session["user"]["id"],
        scheduler_job_id=scheduler_job.id,
        description=request_data.description,
        params=params,
    )

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

        if key.endswith("[]"):
            value = form.getlist(key)
            key = key.removesuffix("[]")
        else:
            value = form[key]

        data[key] = value

    return data
