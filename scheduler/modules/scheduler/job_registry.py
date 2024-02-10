import typing as t
from enum import Enum
from pydantic import BaseModel

from scheduler.modules.scheduler.jobs.send_mail import send_email
from scheduler.modules.scheduler.jobs.schemas import SendMailPayload


class JobParam(t.TypedDict):
    name: str
    display_name: str
    type: t.Any


class JobInfoDict(t.TypedDict):
    display_name: str
    func: t.Callable
    params: list[JobParam]
    schema_cls: BaseModel | None


class JobName(Enum):
    send_email = "send_email"


JOB_REGISTRY: dict[JobName, JobInfoDict] = {
    JobName.send_email.value: {
        "display_name": "Уведомление студентам",
        "func": send_email,
        "params": [
            # {
            #     "name": "from_addr",
            #     "display_name": "Почтовый ящик отправителя",
            #     "type": str,
            # },
            {
                "name": "subject",
                "display_name": "Заголовок",
                "type": str,
            },
            {
                "name": "text",
                "display_name": "Текст письма",
                "type": str,
            },
            {
                "name": "to_addrs[]",
                "display_name": "Email адрес",
                "type": list[str],
            },
            {
                "name": "cc[]",
                "display_name": "Копия",
                "type": list[str],
            }
        ],
        "schema_cls": SendMailPayload,
    },
}
