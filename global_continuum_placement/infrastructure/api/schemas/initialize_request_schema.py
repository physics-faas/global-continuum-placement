from marshmallow import Schema, fields
from marshmallow.validate import OneOf

from global_continuum_placement.domain.platform.platfom_values import (
    ArchitectureType,
    SiteType,
)


class ResourcesSchema(Schema):
    nb_cpu = fields.Integer(description="total number of CPU cores")
    nb_gpu = fields.Integer(description="total number of GPU")
    memory_in_MB = fields.Integer(description="total memory in Mega Bytes")


class SitesSchema(Schema):
    name = fields.String(
        description="Unique name of the site",
        example="HPC-1",
    )
    type = fields.String(
        description="Type of the site",
        enum=list(item.value for item in SiteType),
        example="HPC",
    )
    resources = fields.Nested(
        ResourcesSchema,
        description="The entire resources existing on this site",
    )
    architecture = fields.String(validate=OneOf(ArchitectureType.list()))


class InitializeRequestSchema(Schema):
    platform = fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(SitesSchema),
        description="The entire platform description with all sites",
    )
