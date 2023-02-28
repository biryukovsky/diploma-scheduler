from pydantic import BaseSettings, Field


class DatabaseSettings(BaseSettings):
    user: str = Field(env="DB_USER")
    password: str = Field(env="DB_PASSWORD")
    host: str = Field(env="DB_HOST")
    port: str = Field(env="DB_PORT")
    db_name: str = Field(env="DB_NAME")

    class Config:
        env_file = ".env"


class SchedulerSettings(BaseSettings):
    schema_name: str = Field(env="SCHEDULER_SCHEMA")
    table_name: str = Field(env="SCHEDULER_TABLE")

    class Config:
        env_file = ".env"


class Settings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()
    scheduler: SchedulerSettings = SchedulerSettings()

    class Config:
        env_file = ".env"
