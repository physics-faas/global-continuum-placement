from marshmallow import Schema, fields


class PlacementSchema(Schema):
    site = fields.String(description="site identifier")
    task = fields.String(description="task identifier")
