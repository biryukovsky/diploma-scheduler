from uuid import UUID
from fastapi import APIRouter, Depends, Response
from dependency_injector.wiring import inject, Provide

from scheduler.modules.scheduler.repository import JobRepository
from scheduler.modules.scheduler.services import SchedulerManager
from scheduler.modules.scheduler.schemas import JobIn, JobOut
from scheduler.modules.security.repository import UserRepository
from scheduler.modules.security.security import get_user_from_token
from scheduler.modules.security.schemas import DisplayableUserResponse


router = APIRouter(tags=["jobs"])


@router.get("/", response_model=list[JobOut], dependencies=[Depends(get_user_from_token),])
@inject
async def get_jobs(
    scheduler_manager: SchedulerManager = Depends(Provide["scheduler_manager"]),
    job_repo: JobRepository = Depends(Provide["job_repo"]),
):
    aps_jobs = scheduler_manager.get_jobs()
    aps_jobs_by_id = {j.id: j for j in aps_jobs}
    db_jobs = await job_repo.get_jobs_by_apscheduler_ids(list(aps_jobs_by_id))

    jobs = []
    for db_job in db_jobs:
        job = JobOut.aggregate(db_job, aps_jobs_by_id[db_job.scheduler_job_id])
        jobs.append(job)

    return jobs


@router.get("/{job_id}", response_model=JobOut, dependencies=[Depends(get_user_from_token),])
@inject
async def get_job(
    job_id: UUID,
    scheduler_manager: SchedulerManager = Depends(Provide["scheduler_manager"]),
    job_repo: JobRepository = Depends(Provide["job_repo"]),
):
    db_job = await job_repo.get_job_by_id(job_id)
    aps_job = scheduler_manager.get_job(db_job.scheduler_job_id)
    return JobOut.aggregate(db_job, aps_job)


@router.post("/", response_model=JobOut)
@inject
async def add_job(
    job_in: JobIn,
    scheduler_manager: SchedulerManager = Depends(Provide["scheduler_manager"]),
    user: DisplayableUserResponse = Depends(get_user_from_token),
    job_repo: JobRepository = Depends(Provide["job_repo"]),
    user_repo: UserRepository = Depends(Provide["user_repo"]),
):
    scheduler_job = scheduler_manager.add_job(
        job_name=job_in.job_name,
        trigger=job_in.job_trigger.to_apscheduler_trigger(),
        params=job_in.params,
    )
    db_user = await user_repo.get_user_by_login(user.login)
    db_job = await job_repo.create_job(
        author_id=db_user.id,
        scheduler_job_id=scheduler_job.id,
        description=job_in.description,
        params=job_in.params,
    )

    return JobOut.aggregate(db_job, scheduler_job)


@router.delete("/{job_id}", response_class=Response, dependencies=[Depends(get_user_from_token),])
@inject
async def delete_job(
    job_id: UUID,
    scheduler_manager: SchedulerManager = Depends(Provide["scheduler_manager"]),
    job_repo: JobRepository = Depends(Provide["job_repo"]),
):
    job = await job_repo.get_job_by_id(job_id)
    await job_repo.delete_job(job_id)
    scheduler_manager.delete_job(job.scheduler_job_id)
    return Response()
