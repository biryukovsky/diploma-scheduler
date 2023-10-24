from uuid import UUID
import datetime as dt

from sqlalchemy import select, delete
from sqlalchemy.orm import contains_eager

from scheduler.db import Database
from scheduler.models import Job


class JobRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    async def create_job(
        self,
        author_id: UUID,
        scheduler_job_id: str,
        description: str | None = None,
        params: dict | None = None,
    ) -> Job:
        job = Job(description=description,
                  author_id=author_id,
                  scheduler_job_id=scheduler_job_id,
                  params=self._process_params(params))

        async with self.db.session() as session:
            session.add(job)
            await session.commit()
            await session.flush()
            await session.refresh(job)

        return job

    async def get_jobs_by_apscheduler_ids(self, ids: list[str]) -> list[Job]:
        query = self._get_select_job_query().where(Job.scheduler_job_id.in_(ids))

        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalars()

    async def delete_job(self, job_id: UUID):
        query = delete(Job).where(Job.id == str(job_id))
        async with self.db.session() as session:
            await session.execute(query)
            await session.commit()

    async def get_job_by_id(self, job_id: UUID) -> Job:
        query = self._get_select_job_query().where(Job.id == str(job_id))

        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalar_one()

    def _process_params(self, params: dict):
        if not params:
            return params

        for k, v in params.items():
            if isinstance(v, dt.datetime):
                params[k] = v.isoformat()
            if isinstance(v, dict):
                params[k] = self._process_params(v)
        return params

    def _get_select_job_query(self):
        return (
            select(Job)
            .join(Job.author)
            .options(contains_eager(Job.author))
        )
