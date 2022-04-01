from marshmallow import Schema, fields


class FunctionSchema(Schema):
    id = fields.String()
    displayName = fields.String()
    type = fields.String()
    code = fields.String()
    sequence = fields.Integer()
    annotations = fields.Dict()
    allocations = fields.List(fields.String)


class ApplicationSchema(Schema):
    id = fields.String()
    displayName = fields.String()
    type = fields.String()
    execution_mode = fields.String()
    native = fields.Boolean()
    functions = fields.Nested(FunctionSchema, many=True)
    objectives = fields.Dict()
