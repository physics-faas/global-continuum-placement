from marshmallow import Schema, fields


class PlacementSchema(Schema):
    site = fields.String(description="cluster identifier")
    task = fields.String(description="function identifier")
