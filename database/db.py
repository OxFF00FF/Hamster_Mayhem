from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from config import app_config

engine = create_engine(
    url=app_config.DB_URL_sqlite,
    echo=False
)

Session = sessionmaker(bind=engine)


def get_session():
    return Session()


def close_session(session):
    session.close()
