import logging

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from global_continuum_placement.infrastructure.database.mapper import start_mapping
from global_continuum_placement.infrastructure.database.metadata import metadata

Base = declarative_base()

Session = sessionmaker()


def _remove_password_from_URI(uri: str):
    passw = uri.split("://")[1].split("@")[0].split(":")[1]
    return uri.replace(passw, "******")


class DatabaseEngine:
    def __init__(self, connection_url: str):
        self.logger = logging.getLogger(DatabaseEngine.__name__)
        self.connection_url: str = connection_url
        self.connection: Engine = None

    def connect(self):
        self.logger.info("Connecting to database")
        self.logger.debug(
            "Database connection url: %s",
            _remove_password_from_URI(self.connection_url),
        )
        self.connection = create_engine(self.connection_url)
        metadata.create_all(bind=self.connection)
        start_mapping()

    def disconnect(self):
        self.logger.info("Disconnecting from database")
        self.connection.dispose()

    def get_session(self):
        return Session(bind=self.connection)
