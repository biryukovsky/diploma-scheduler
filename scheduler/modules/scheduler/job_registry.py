import typing as t
from enum import Enum

from scheduler.modules.scheduler.jobs import notify_students


class JobParam(t.TypedDict):
    name: str
    display_name: str
    type: t.Any


class JobInfoDict(t.TypedDict):
    display_name: str
    func: t.Callable
    params: list[JobParam]


class JobName(Enum):
    notify_students = "notify_students"


JOB_REGISTRY: dict[JobName, JobInfoDict] = {
    JobName.notify_students.value: {
        "display_name": "Уведомление студентам",
        "func": notify_students,
        "params": [
            {
                "name": "subject",
                "display_name": "Заголовок",
                "type": str,
            },
            {
                "name": "message",
                "display_name": "Сообщение",
                "type": str,
            },
            {
                "name": "emails[]",
                "display_name": "Email адрес",
                "type": list[str],
            },
        ]
    },
}
