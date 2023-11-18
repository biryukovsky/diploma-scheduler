from sqlalchemy import select

from scheduler.db import Database
from scheduler.models import User


class UserRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    async def get_user_by_login(self, login: str) -> User | None:
        async with self.db.session() as session:
            user = (await session.execute(select(User).where(User.login == login))).scalar()
            return user

    async def create(
        self,
        login: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ):
        async with self.db.session() as session:
            user = User(
                login=login,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
