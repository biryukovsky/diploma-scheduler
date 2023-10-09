import datetime as dt
import pathlib

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


template_dir = pathlib.Path(__file__).parent / "templates"

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=template_dir)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
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
async def create_job_page(request: Request):
    return templates.TemplateResponse("create_job.html", context={
        "request": request,
    })


@router.post("/create")
async def create_job():
    return RedirectResponse("/", status_code=302)
