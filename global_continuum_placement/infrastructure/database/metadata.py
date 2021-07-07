from sqlalchemy import (
    Column,
    MetaData,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID

metadata = MetaData()

# table declaration
CHANGEME_table: Table = Table(
    "global_continuum_placement",
    metadata,
    Column("id", UUID, primary_key=True, nullable=False),
    Column("name", String, nullable=False),
)
