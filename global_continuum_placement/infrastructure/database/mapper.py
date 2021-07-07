from sqlalchemy.orm import mapper

from global_continuum_placement.domain.CHANGEME_object.CHANGEME_object import CHANGEME
from global_continuum_placement.infrastructure.database.metadata import CHANGEME_table


def start_mapping():
    """ Method to start mapping between database and domain models """
    mapper(
        CHANGEME,
        CHANGEME_table,
        properties={
            "id": CHANGEME_table.columns.id,
            "name": CHANGEME_table.columns.name,
        },
    )
