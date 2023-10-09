from scheduler.utils.exception import SchedulerException


class JobNotFound(SchedulerException):
    status_code = 404

    def __init__(self, job_id, *args: object) -> None:
        self.job_id = job_id
        super().__init__(f"Job `{self.job_id}` not found")


class UnknownJobFunction(SchedulerException):
    def __init__(self, job_name: str, *args: object) -> None:
        self.job_name = job_name
        super().__init__(f"Unknown function: `{self.job_name}`")


class SchedulerAlreadyRunning(SchedulerException):
    ...


class SchedulerStopped(SchedulerException):
    ...
