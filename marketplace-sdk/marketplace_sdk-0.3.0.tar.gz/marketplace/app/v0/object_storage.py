import json
from typing import Dict, Union

import marketplace_standard_app_api.models.object_storage as object_storage
from fastapi import UploadFile

from ..utils import check_capability_availability
from .base import _MarketPlaceAppBase
from .utils import _decode_metadata, _encode_metadata


class MarketPlaceObjectStorageApp(_MarketPlaceAppBase):
    @check_capability_availability
    def list_collections(
        self, limit: int = 100, offset: int = 0
    ) -> object_storage.CollectionListResponse:
        return object_storage.CollectionListResponse(
            **self._client.get(
                "listCollections", params={"limit": limit, "offset": offset}
            ).json()
        )

    @check_capability_availability
    def list_datasets(
        self,
        collection_name: object_storage.CollectionName,
        limit: int = 100,
        offset: int = 0,
    ) -> object_storage.DatasetListResponse:
        return object_storage.DatasetListResponse(
            **self._client.get(
                "listDatasets",
                params={
                    "collection_name": collection_name,
                    "limit": limit,
                    "offset": offset,
                },
            ).json()
        )

    @check_capability_availability
    def create_or_update_collection(
        self,
        metadata: dict = None,
        collection_name: object_storage.CollectionName = None,
    ) -> str:
        return self._client.put(
            "createOrUpdateCollection",
            params={"collection_name": collection_name} if collection_name else {},
            headers=_encode_metadata(metadata),
        ).text

    @check_capability_availability
    def delete_collection(self, collection_name: object_storage.CollectionName):
        self._client.delete(
            "deleteCollection", params={"collection_name": collection_name}
        )

    # NOTE: change to GET for the meeting if proxy doesn't support HEAD requests
    @check_capability_availability
    def get_collection_metadata(
        self, collection_name: object_storage.CollectionName
    ) -> Union[Dict, str]:
        response_headers: dict = self._client.head(
            "getCollectionMetadata", params={"collection_name": collection_name}
        ).headers
        return json.dumps(_decode_metadata(headers=response_headers))

    @check_capability_availability
    def create_collection(
        self,
        collection_name: object_storage.CollectionName = None,
        metadata: dict = None,
    ) -> str:
        return self._client.put(
            "createCollection",
            params={"collection_name": collection_name} if collection_name else {},
            headers=_encode_metadata(metadata),
        ).text

    @check_capability_availability
    def create_dataset(
        self,
        collection_name: object_storage.CollectionName,
        dataset_name: object_storage.DatasetName = None,
        metadata: dict = None,
        file: UploadFile = None,
    ) -> object_storage.DatasetCreateResponse:
        params = {"collection_name": collection_name}
        if dataset_name:
            params.update({"dataset_name": dataset_name})
        return object_storage.DatasetCreateResponse.parse_obj(
            json.loads(
                self._client.put(
                    "createDataset",
                    params=params,
                    headers=_encode_metadata(metadata),
                    data=file.file,
                )
            )
        )

    @check_capability_availability
    def create_dataset_metadata(
        self,
        collection_name: object_storage.CollectionName,
        dataset_name: object_storage.DatasetName = None,
        metadata: dict = None,
    ) -> str:
        params = {"collection_name": collection_name}
        if dataset_name:
            params.update({"dataset_name": dataset_name})
        return self._client.post(
            "createDatasetMetadata",
            params=params,
            headers=_encode_metadata(metadata),
        ).text

    @check_capability_availability
    def get_dataset(
        self,
        collection_name: object_storage.CollectionName,
        dataset_name: object_storage.DatasetName,
    ) -> Union[Dict, str]:
        return self._client.get(
            "getDataset",
            params={"collection_name": collection_name, "dataset_name": dataset_name},
        ).json()

    def create_or_replace_dataset(
        self,
        collection_name: object_storage.CollectionName,
        dataset_name: object_storage.DatasetName = None,
        metadata: dict = None,
        file: UploadFile = None,
    ) -> object_storage.DatasetCreateResponse:
        params = {"collection_name": collection_name}
        if dataset_name:
            params.update({"dataset_name": dataset_name})
        return object_storage.DatasetCreateResponse(
            **self._client.put(
                "createOrReplaceDataset",
                params=params,
                headers=_encode_metadata(metadata),
                data=file.file,
            )
        )

    @check_capability_availability
    def create_or_replace_dataset_metadata(
        self,
        collection_name: object_storage.CollectionName,
        dataset_name: object_storage.DatasetName,
        metadata: dict = None,
    ) -> str:
        return self._client.put(
            "createOrReplaceDatasetMetadata",
            params={"collection_name": collection_name, "dataset_name": dataset_name},
            headers=_encode_metadata(metadata),
        ).text

    @check_capability_availability
    def delete_dataset(
        self,
        collection_name: object_storage.CollectionName,
        dataset_name: object_storage.DatasetName,
    ):
        self._client.delete(
            "deleteDataset",
            params={"collection_name": collection_name, "dataset_name": dataset_name},
        )

    # NOTE: change to GET for the meeting if proxy doesn't support HEAD requests
    @check_capability_availability
    def get_dataset_metadata(
        self,
        collection_name: object_storage.CollectionName,
        dataset_name: object_storage.DatasetName,
    ) -> Union[Dict, str]:
        response_headers: dict = self._client.head(
            "getDatasetMetadata",
            params={"collection_name": collection_name, "dataset_name": dataset_name},
        ).headers
        return json.dumps(_decode_metadata(headers=response_headers))

    @check_capability_availability
    def list_semantic_mappings(
        self, limit: int = 100, offset: int = 0
    ) -> object_storage.SemanticMappingListResponse:
        return object_storage.SemanticMappingListResponse(
            **self._client.get(
                "listSemanticMappings", params={"limit": limit, "offset": offset}
            ).json()
        )

    @check_capability_availability
    def get_semantic_mapping(
        self, semantic_mapping_id: str
    ) -> object_storage.SemanticMappingModel:
        return object_storage.SemanticMappingModel.parse_obj(
            json.loads(
                self._client.get(
                    "getSemanticMapping",
                    params={"semantic_mapping_id": semantic_mapping_id},
                )
            )
        )
