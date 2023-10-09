import typing as t
import datetime as dt

from pydantic import BaseModel, Field, conint
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger  # noqa
from apscheduler.triggers.interval import IntervalTrigger


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
    job_name: str  # TODO: validate by list of possible jobs
    job_trigger: DateJobTrigger | IntervalJobTrigger = Field(..., discriminator="trigger_name")
    args: dict | None = Field(default_factory=dict)


class JobOut(BaseModel):
    id: str
    name: str
    next_run_time: dt.datetime

    class Config:
        orm_mode = True
