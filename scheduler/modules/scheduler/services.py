from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
from apscheduler.job import Job

import pytz

from scheduler.db import Database
from scheduler.modules.scheduler.exceptions import (
    JobNotFound, UnknownJobFunction, SchedulerAlreadyRunning, SchedulerStopped,
)
from scheduler.utils.dates import HOUR_IN_SECS
from scheduler.modules.scheduler.job_registry import JOB_REGISTRY


class SchedulerManager:
    def __init__(
        self,
        db: Database,
        scheduler_schema: str,
        scheduler_table: str,
    ) -> None:
        self.scheduler = AsyncIOScheduler(
            timezone=pytz.utc,
            job_defaults={
                "misfire_grace_time": HOUR_IN_SECS * 2.
            }
        )
        self.db = db
        self.scheduler_schema = scheduler_schema
        self.scheduler_table = scheduler_table
        self._running = False

    def get_jobs(self) -> list[Job]:
        return self.scheduler.get_jobs()

    def get_job(self, job_id) -> Job:
        job = self.scheduler.get_job(job_id)
        if not job:
            raise JobNotFound(job_id)
        return job

    def delete_job(self, job_id):
        try:
            self.scheduler.remove_job(job_id)
        except JobLookupError:
            pass

    def add_job(
        self,
        job_name: str,
        trigger,
        job_id: str | None = None,
        replace_existing: bool | None = False,
        **kwargs
    ) -> Job:
        job_item = JOB_REGISTRY.get(job_name)
        if not job_item:
            raise UnknownJobFunction(job_name)

        job = self.scheduler.add_job(
            job_item["func"],
            trigger,
            name=job_name,
            kwargs=kwargs,
            max_instances=1,
            id=job_id,
            replace_existing=replace_existing,
        )
        return job

    def start(self):
        if self._running:
            raise SchedulerAlreadyRunning

        self._running = True

        self.scheduler.add_jobstore(
            "sqlalchemy",
            engine=self.db.sync_engine,
            tablename=self.scheduler_table,
            tableschema=self.scheduler_schema,
        )
        self.scheduler.start()

    def stop(self):
        if not self._running:
            raise SchedulerStopped

        self._running = False

        self.scheduler.shutdown()
