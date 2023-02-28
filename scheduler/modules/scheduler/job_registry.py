import typing as t

from scheduler.modules.scheduler.jobs import notify_students


JOB_REGISTRY: dict[str, t.Callable] = {
    "notify_students": notify_students,
}
