from marshmallow import Schema, fields
from marshmallow.validate import OneOf

from global_continuum_placement.domain.platform.platfom_values import (
    ArchitectureType,
    ClusterType,
)
from global_continuum_placement.domain.workload.workload_values import Objectives


class ResourcesSchema(Schema):
    nb_cpu = fields.Integer(description="total number of CPU cores")
    nb_gpu = fields.Integer(description="total number of GPU")
    memory_in_MB = fields.Integer(description="total memory in Mega Bytes")


class ClusterSchema(Schema):
    id = fields.String()
    name = fields.String(
        description="Unique name of the cluster",
        example="HPC-1",
    )
    type = fields.String(
        description="Type of the cluster",
        enum=list(item.value for item in ClusterType),
        example="HPC",
    )
    resources = fields.Nested(
        ResourcesSchema,
        description="The entire resources existing on this cluster",
    )
    architecture = fields.String(validate=OneOf(ArchitectureType.list()))
    objective_scores = fields.Dict(
        keys=fields.String(validate=OneOf(Objectives.list())),
        values=fields.Integer(validate=lambda x: 0 < x <= 100),
        load_default={},
    )


class PlatformSchema(Schema):
    platform = fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(ClusterSchema),
        description="The entire platform description with all clusters",
    )
