from marshmallow import Schema, fields


class PlacementSchema(Schema):
    cluster = fields.String(description="cluster identifier")
    resource_id = fields.String(description="function or flow identifier")
    fallback_cluster = fields.String(description="fallback cluster identifier")


class FlowAllocationSchema(Schema):
    flowID = fields.String(metadata={"description": "The flow id"})
    allocations = fields.Nested(
        PlacementSchema,
        many=True,
        metadata={"description": "The resource allocations in the flow"},
    )
