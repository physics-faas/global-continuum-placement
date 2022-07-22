from marshmallow import INCLUDE, Schema, fields


class FunctionSchema(Schema):
    class Meta:
        unknown = INCLUDE

    id = fields.String()
    displayName = fields.String()
    type = fields.String()
    code = fields.String()
    sequence = fields.Integer()
    annotations = fields.Dict()
    allocations = fields.List(fields.String)


class FlowSchema(Schema):
    class Meta:
        unknown = INCLUDE

    flowID = fields.String()
    flowName = fields.String()
    type = fields.String()
    executorMode = fields.String()
    native = fields.Boolean()
    artifact = fields.String()
    annotations = fields.Dict()
    functions = fields.Nested(FunctionSchema, many=True)
    allocations = fields.List(fields.String())


class ApplicationSchema(Schema):
    class Meta:
        unknown = INCLUDE

    appName = fields.String()
    owner = fields.String()
    SoftwareImage = fields.String()
    app_id = fields.String()
    flows = fields.Nested(FlowSchema, many=True)
