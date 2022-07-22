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
    memory = fields.String()
    timeout = fields.String()
    appID = fields.String()
    appName = fields.String()
    functions = fields.Nested(FunctionSchema, many=True)
    objectives = fields.Dict()


class ApplicationSchema(Schema):
    appName = fields.String()
    owner = fields.String()
    SoftwareImage = fields.String()
    flows = fields.Nested(FlowSchema, many=True)
