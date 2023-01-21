class JobNotFound(Exception):
    def __init__(self, job_id, *args: object) -> None:
        self.job_id = job_id
        super().__init__(*args)


class UnknownJobFunction(ValueError):
    def __init__(self, job_name: str, *args: object) -> None:
        self.job_name = job_name
        super().__init__(*args)


class SchedulerAlreadyRunning(Exception):
    ...


class SchedulerStopped(Exception):
    ...
