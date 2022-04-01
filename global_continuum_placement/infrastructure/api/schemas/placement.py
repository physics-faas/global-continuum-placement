from marshmallow import Schema, fields


class PlacementSchema(Schema):
    cluster = fields.String(description="cluster identifier")
    function = fields.String(description="function identifier")
