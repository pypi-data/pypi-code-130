from dynatrace.opentelemetry.tracing._util.hashes import tenant_id_hash


class QualifiedTenantId:
    def __init__(self, cluster_id: int, tenant_uuid: str):
        self._cluster_id = cluster_id
        self._tenant_uuid = tenant_uuid
        self._tenant_id = tenant_id_hash(tenant_uuid)

    @property
    def cluster_id(self) -> int:
        """Returns the identifier of the cluster to which spans are reported."""
        return self._cluster_id

    @property
    def tenant_uuid(self):
        """Returns the UUID of the tenant for which spans are reported."""
        return self._tenant_uuid

    @property
    def tenant_id(self) -> int:
        """Returns the ID of the tenant for which spans are reported.

        The tenant ID corresponds to the hashed tenant UUID.
        """
        return self._tenant_id
