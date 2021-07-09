from infrastructure.api.schemas.initialize_request_schema import ResourcesSchema
from marshmallow import Schema, fields


class ConstraintsSchema(Schema):
    site = fields.String()
    site_type = fields.String()


class TaskSchema(Schema):
    resources = fields.Nested(ResourcesSchema)
    constraints = fields.Nested(ConstraintsSchema, many=True)


class WorkflowScheduleRequestSchema(Schema):
    name = fields.String(description="Workflow unique name")
    workflow = fields.Dict(
        keys=fields.String(description="tasks id"), values=fields.Nested(TaskSchema)
    )
