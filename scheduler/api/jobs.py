from fastapi import APIRouter, Depends, Response
from dependency_injector.wiring import inject, Provide

from scheduler.modules.scheduler.services import SchedulerManager
from scheduler.modules.scheduler.schemas import JobIn, JobOut
from scheduler.modules.security.security import get_user_from_token
from scheduler.modules.security.schemas import DisplayableUserResponse


router = APIRouter(tags=["jobs"])


@router.get("/", response_model=list[JobOut], dependencies=[Depends(get_user_from_token),])
@inject
async def get_jobs(
    scheduler_manager: SchedulerManager = Depends(Provide["scheduler_manager"]),
):
    jobs = scheduler_manager.get_jobs()
    return list(map(JobOut.from_orm, jobs))


@router.get("/{job_id}", response_model=JobOut, dependencies=[Depends(get_user_from_token),])
@inject
async def get_job(
    job_id: str,
    scheduler_manager: SchedulerManager = Depends(Provide["scheduler_manager"])
):
    job = scheduler_manager.get_job(job_id)
    return JobOut.from_orm(job)


@router.post("/", response_model=JobOut)
@inject
async def add_job(
    job_in: JobIn,
    scheduler_manager: SchedulerManager = Depends(Provide["scheduler_manager"]),
    user: DisplayableUserResponse = Depends(get_user_from_token),
):
    # TODO: create job with author
    job = scheduler_manager.add_job(
        job_name=job_in.job_name,
        trigger=job_in.job_trigger.to_apscheduler_trigger(),
        **job_in.args,
    )
    return JobOut.from_orm(job)


@router.delete("/{job_id}", response_class=Response, dependencies=[Depends(get_user_from_token),])
@inject
async def delete_job(job_id, scheduler_manager: SchedulerManager = Depends(Provide["scheduler_manager"])):
    scheduler_manager.delete_job(job_id)
    return Response()
