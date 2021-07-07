from marshmallow import Schema, fields


class ErrorSchema(Schema):
    name = fields.String(description="Error name", example="Object not found")
