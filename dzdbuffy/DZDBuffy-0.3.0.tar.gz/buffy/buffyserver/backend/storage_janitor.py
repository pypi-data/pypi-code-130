import logging
from buffy.buffyserver.backend.storage.interface import StorageInterface
from buffy.buffyserver.api.v1.models import Request, Response

log = logging.getLogger(__name__)


class StorageJanitor:
    def __init__(self, storage: StorageInterface):
        self.storage = storage

    def cleanup_storage(self):
        """Remove responses that are too old according to `Request.cache_configuration.max_cached_versions`"""
        for req in self.storage.list_requests():
            self._clean_up_request_responses(req)

    def _clean_up_request_responses(self, request: Request):
        ready_responses = [
            res
            for res in self.storage.list_responses(request_id=request.id)
            if res.status in ["ready"]
        ]
        if request.cache_configuration.max_cached_versions < len(ready_responses):
            for resp in ready_responses[
                request.cache_configuration.max_cached_versions :
            ]:
                self.storage.delete_response(resp)
            ready_responses = ready_responses[
                : request.cache_configuration.max_cached_versions
            ]

    def verifiy_storage(self):
        """Remove responses that have issues with their content like unexpected changes or just missing
        This can be a very expensive operation. Use wisely!
        """
        for req in self.storage.list_requests():
            self._verifiy_request_responses(req)

    def _verifiy_request_responses(self, request: Request):
        for resp in [
            res
            for res in self.storage.list_responses(request_id=request.id)
            if res.status in ["ready"]
        ]:
            old_hash = resp.content_hash_hex
            try:
                current_hash = self.storage.get_response_content_hash(
                    resp, cached_hash=False
                )
            except FileNotFoundError:
                # file is missing. we have a garbage response here. lets just delete it
                log.warning(
                    f"Request.id: '{request.id}' Response.id: '{resp.id}' -> Error during validation hashing. Response will be deleted"
                )
                self.storage.delete_response(resp)
                # go to next response
                continue
            if old_hash != current_hash:
                # the file changed. this means from our perspective the file is corrupt
                log.warning(
                    f"Request.id: '{request.id}' Response.id: '{resp.id}' -> Response content changed unexpected. Response will be deleted"
                )
                self.storage.delete_response(resp)
