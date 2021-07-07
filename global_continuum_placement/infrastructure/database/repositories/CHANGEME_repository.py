from typing import List

from sqlalchemy.orm import Session

from global_continuum_placement.domain.CHANGEME_object.CHANGEME_object import CHANGEME
from global_continuum_placement.domain.CHANGEME_object.CHANGEME_repository import (
    ICHANGEMERepository,
)


class DatabaseCHANGEMERepository(ICHANGEMERepository):
    """ Postgres implementation of workflow repository """

    def __init__(self, session: Session):
        self.session = session

    def list_projects(self) -> List[CHANGEME]:
        return self.session.query(CHANGEME).all()
