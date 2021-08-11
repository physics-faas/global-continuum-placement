from marshmallow import Schema, fields

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


class WorkflowScheduleRequestSchema(Schema):
    name = fields.String(description="Workflow unique name")
    workflow = fields.Dict(
        keys=fields.String(description="tasks id"), values=fields.Nested(TaskSchema)
    )
