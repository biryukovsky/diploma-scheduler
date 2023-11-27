from pydantic import BaseSettings, Field, EmailStr


class DatabaseSettings(BaseSettings):
    user: str
    password: str
    host: str
    port: str
    name: str

    class Config:
        env_file = ".env"
        env_prefix = "DB_"


class SchedulerSettings(BaseSettings):
    db_schema: str
    table: str

    class Config:
        env_file = ".env"
        env_prefix = "SCHEDULER_"


class SecuritySettings(BaseSettings):
    secret_key: str = Field(env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 3

    class Config:
        env_file = ".env"


class MailSettings(BaseSettings):
    host: str
    port: str
    from_addr: EmailStr

    class Config:
        env_file = ".env"
        env_prefix = "MAIL_"


class Settings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()
    scheduler: SchedulerSettings = SchedulerSettings()
    security: SecuritySettings = SecuritySettings()
    mail: MailSettings = MailSettings()

    class Config:
        env_file = ".env"
