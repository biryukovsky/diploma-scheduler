from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from scheduler.modules.scheduler.services import SchedulerManager


router = APIRouter(tags=["jobs"])


@router.get("/")  # TODO: schema
@inject
async def get_jobs(scheduler_manager: SchedulerManager = Depends(Provide["scheduler_manager"])):
    jobs = scheduler_manager.get_jobs()
    print(jobs)


@router.get("/{job_id}")
@inject
async def get_job(job_id):
    ...


@router.post("/")
@inject
async def add_job():
    ...


@router.delete("/{job_id}")
@inject
async def delete_job(job_id):
    ...
