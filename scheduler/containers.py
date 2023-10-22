from dependency_injector.containers import DeclarativeContainer
from dependency_injector import providers

from scheduler.db import Database
from scheduler.modules.scheduler.repository import JobRepository
from scheduler.modules.scheduler.services import SchedulerManager


class Container(DeclarativeContainer):

    config = providers.Configuration()

    db = providers.Singleton(
        Database,
        host=config.db.host,
        port=config.db.port,
        user=config.db.user,
        password=config.db.password,
        db_name=config.db.db_name,
    )

    job_repo = providers.Factory(
        JobRepository,
        db=db,
    )

    scheduler_manager = providers.Singleton(
        SchedulerManager,
        db=db,
        scheduler_schema=config.scheduler.schema_name,
        scheduler_table=config.scheduler.table_name,
    )
