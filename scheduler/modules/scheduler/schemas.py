import typing as t
import datetime as dt

from pydantic import BaseModel, Field, conint, validator
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger  # noqa
from apscheduler.triggers.interval import IntervalTrigger
from scheduler.modules.scheduler.job_registry import JOB_REGISTRY, JobName


class DateJobTrigger(BaseModel):
    trigger_name: t.Literal["date"]

    run_date: dt.datetime

    def to_apscheduler_trigger(self,) -> DateTrigger:
        return DateTrigger(run_date=self.run_date)


class IntervalJobTrigger(BaseModel):
    trigger_name: t.Literal["interval"]

    weeks: conint(ge=0) = 0
    days: conint(ge=0) = 0
    hours: conint(ge=0) = 0
    minutes: conint(ge=0) = 0
    seconds: conint(ge=0) = 0
    start_date: dt.datetime | None = None
    end_date: dt.datetime | None = None

    def to_apscheduler_trigger(self) -> IntervalTrigger:
        return IntervalTrigger(
            weeks=self.weeks,
            days=self.days,
            hours=self.hours,
            minutes=self.minutes,
            seconds=self.seconds,
            start_date=self.start_date,
            end_date=self.end_date,
        )


class JobIn(BaseModel):
    job_name: JobName
    description: str | None = None
    job_trigger: DateJobTrigger | IntervalJobTrigger = Field(..., discriminator="trigger_name")
    params: dict | None = Field(default_factory=dict)

    class Config:
        use_enum_values = True

    @validator("params")
    def validate_params(cls, in_params, values, **kwargs):
        if "job_name" not in values:
            raise ValueError("job_name is required")

        job_params = JOB_REGISTRY[values["job_name"]]["params"]

        if not in_params and job_params:
            raise ValueError(f"params for job `{values['job_name']}` must not be empty")

        if not job_params and in_params:
            raise ValueError(f"params for job `{values['job_name']}` must be empty")

        errors = []

        for p in job_params:
            if p["name"] in in_params:
                if not isinstance(in_params[p["name"]], p["type"]):
                    errors.append(f"expected type `{p['type']}` for param `{p['name']}`, got `{type(in_params[p['name']])}`")
            else:
                errors.append(f"param `{p['name']}` is missing")

        # TODO: возможно эта проверка не нужна
        if in_params:
            for k in in_params:
                if k not in job_params:
                    errors.append(f"unknown param `{k}`")

        if errors:
            raise ValueError(";".join(errors))

        return in_params


class JobOut(BaseModel):
    id: str
    name: str
    next_run_time: dt.datetime
    author: str
    description: str | None = None

    class Config:
        orm_mode = True

    @classmethod
    def aggregate(cls, db_job, aps_job):
        return cls(
            id=db_job.id,
            name=aps_job.name,
            next_run_time=aps_job.next_run_time,
            author=f"{db_job.author.first_name} {db_job.author.last_name}".strip() or db_job.author.login,
            description=db_job.description,
        )
