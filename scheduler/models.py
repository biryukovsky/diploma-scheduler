import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = sa.Column(PG_UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()"))
    login = sa.Column(sa.Text, nullable=False, unique=True)
    password = sa.Column(sa.Text, nullable=False)
    first_name = sa.Column(sa.Text, nullable=True)
    last_name = sa.Column(sa.Text, nullable=True)


class Job(Base):
    __tablename__ = "job"

    id = sa.Column(PG_UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()"))
    description = sa.Column(sa.Text, nullable=True)
    author_id = sa.Column(PG_UUID, sa.ForeignKey("user.id"), nullable=False)
    # scheduler.job.id reference, alembic refuses to generate foreign key for non-sqla tables
    scheduler_job_id = sa.Column(sa.Text, nullable=False)
    params = sa.Column(JSONB, nullable=True)

    author = relationship(User, backref="jobs")
