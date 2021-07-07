from typing import Callable

from sqlalchemy.orm import Session

from global_continuum_placement.application.unit_of_work import IUnitOfWork
from global_continuum_placement.infrastructure.database.engine import DatabaseEngine
from global_continuum_placement.infrastructure.database.repositories.CHANGEME_repository import (
    DatabaseCHANGEMERepository,
)


class DatabaseUnitOfWork(IUnitOfWork):
    def __init__(
        self,
        engine: DatabaseEngine,
        CHANGEME_repository_factory: Callable[..., DatabaseCHANGEMERepository],
    ):
        self.engine = engine
        self.session: Session = None
        self.CHANGEME_repository_factory = CHANGEME_repository_factory
        self.project = None

    def __enter__(self):
        self.session = self.engine.get_session()
        self.projects = self.CHANGEME_repository_factory(session=self.session)

    def __exit__(self, *args):
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
        self.session.refresh()
