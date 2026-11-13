from sqlmodel import SQLModel, Session, create_engine

from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)


def get_session():
    return Session(engine)
