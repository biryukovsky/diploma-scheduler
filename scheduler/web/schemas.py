import datetime as dt

from pydantic import BaseModel

from scheduler.modules.scheduler.job_registry import JobName


class CreateJobRequest(BaseModel):
    name: JobName
    description: str | None = None
    next_run_time: dt.datetime

    class Config:
        use_enum_values = True
