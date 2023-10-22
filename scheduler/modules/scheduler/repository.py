from uuid import UUID

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
                  scheduler_job_id=scheduler_job_id)

        async with self.db.session() as session:
            session.add(job)
            await session.commit()
            await session.flush()
            await session.refresh(job)

        return job
