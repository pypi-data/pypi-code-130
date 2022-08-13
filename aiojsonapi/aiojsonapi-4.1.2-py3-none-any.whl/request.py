"""Module with request structure."""


class Request:
    """Request structure with data and template validated data."""

    def __init__(self, data, validated_data=None):
        self.data = data
        self.validated_data = validated_data
