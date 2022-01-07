from marshmallow import Schema, fields
from marshmallow.validate import OneOf

from global_continuum_placement.domain.platform.platfom_values import ArchitectureType
from global_continuum_placement.infrastructure.api.schemas.initialize_request_schema import (
    ResourcesSchema,
)


class ConstraintsSchema(Schema):
    site = fields.String()
    site_type = fields.String()


class TaskSchema(Schema):
    resources = fields.Nested(ResourcesSchema)
    constraints = fields.Nested(ConstraintsSchema, many=True)
    next_tasks = fields.List(fields.String())
    architecture = fields.String(validate=OneOf(list(ArchitectureType)))


class WorkflowScheduleRequestSchema(Schema):
    name = fields.String(description="Workflow unique name")
    workflow = fields.Dict(
        keys=fields.String(description="tasks id"), values=fields.Nested(TaskSchema)
    )
