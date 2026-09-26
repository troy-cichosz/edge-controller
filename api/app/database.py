import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.environ["DATABASE_URL"]


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def ensure_schema():
    """
    Create the SQLAlchemy schema and apply small idempotent schema
    additions required by the current application model.

    The project does not currently use Alembic or another migration
    framework. PostgreSQL's IF NOT EXISTS semantics make these
    additions safe to execute at every controller startup.
    """

    Base.metadata.create_all(
        bind=engine
    )

    with engine.begin() as connection:

        connection.execute(
            text(
                """
                ALTER TABLE services
                ADD COLUMN IF NOT EXISTS capabilities JSON
                """
            )
        )

        connection.execute(
            text(
                """
                ALTER TABLE services
                ADD COLUMN IF NOT EXISTS observation_resources JSON
                """
            )
        )