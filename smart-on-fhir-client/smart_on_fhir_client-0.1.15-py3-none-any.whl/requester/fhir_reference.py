from fhirpy.base.exceptions import ResourceNotFound
from fhirpy.lib import AsyncFHIRReference, AsyncFHIRResource

from smart_on_fhir_client.requester.mixin import SerializeMixin


class CustomFHIRReference(SerializeMixin, AsyncFHIRReference):
    def __init__(self, fhir_manager, client, **kwargs):
        self.client = client
        self.fhir_client_manager = fhir_manager
        super().__init__(self.client, **kwargs)

    async def to_resource(self):
        """
        Returns Resource instance for this reference
        from fhir server otherwise.
        """
        if not self.is_local:
            raise ResourceNotFound("Can not resolve not local resource")
        # here we perform a get /id because lifen does not support post
        # search with _id
        # noinspection PyProtectedMember
        resource = await self.client._do_request(
            "GET", f"{self.client.url}/{self.resource_type}/{self.id}"
        )
        return self.fhir_client_manager.create_async_fhir_resource(
            self.client,
            AsyncFHIRResource(
                self.client, resource_type=self.resource_type, **resource
            ),
        )

    def __str__(self):  # pragma: no cover
        return f"<CustomFHIRReference {self.reference}>"
