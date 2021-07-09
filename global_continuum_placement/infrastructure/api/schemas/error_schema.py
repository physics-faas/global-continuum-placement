from marshmallow import Schema, fields


class ErrorSchema(Schema):
    error = fields.String(description="Error details", example="Object not found")
