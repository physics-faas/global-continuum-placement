from marshmallow import Schema, fields


class FunctionSchema(Schema):
    id = fields.String()
    displayName = fields.String()
    type = fields.String()
    code = fields.String()
    sequence = fields.Integer()
    annotations = fields.Dict()
    allocations = fields.List(fields.String)


class FlowSchema(Schema):
    flowID = fields.String()
    flowName = fields.String()
    type = fields.String()
    executorMode = fields.String()
    native = fields.Boolean()
    artifact = fields.String()
    annotations = fields.Dict()
    hasAction = fields.String()
    functions = fields.Nested(FunctionSchema, many=True)


class ApplicationSchema(Schema):
    appName = fields.String()
    owner = fields.String()
    SoftwareImage = fields.String()
    app_id = fields.String()
    flows = fields.Nested(FlowSchema, many=True)
