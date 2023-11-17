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
