# -*- coding: utf-8 -*-
import hashlib
import os
import tarfile
import tempfile
from contextlib import contextmanager
from typing import NewType, Tuple

import requests
import zstandard as zstd
from apistar.exceptions import ErrorResponse

from arkindex_worker import logger

CHUNK_SIZE = 1024

DirPath = NewType("DirPath", str)
Hash = NewType("Hash", str)
FileSize = NewType("FileSize", int)
Archive = Tuple[DirPath, Hash, FileSize]


@contextmanager
def create_archive(path: DirPath) -> Archive:
    """First create a tar archive, then compress to a zst archive.
    Finally, get its hash and size
    """
    assert path.is_dir(), "create_archive needs a directory"

    compressor = zstd.ZstdCompressor(level=3)
    content_hasher = hashlib.md5()
    archive_hasher = hashlib.md5()

    # Remove extension from the model filename
    _, path_to_tar_archive = tempfile.mkstemp(prefix="teklia-", suffix=".tar")

    # Create an uncompressed tar archive with all the needed files
    # Files hierarchy ifs kept in the archive.
    file_list = []
    with tarfile.open(path_to_tar_archive, "w") as tar:
        for p in path.glob("**/*"):
            x = p.relative_to(path)
            tar.add(p, arcname=x, recursive=False)
            file_list.append(p)

    # Sort by path
    file_list.sort()
    # Compute hash of the files
    for file_path in file_list:
        with open(file_path, "rb") as file_data:
            for chunk in iter(lambda: file_data.read(CHUNK_SIZE), b""):
                content_hasher.update(chunk)

    _, path_to_zst_archive = tempfile.mkstemp(prefix="teklia-", suffix=".tar.zst")

    # Compress the archive
    with open(path_to_zst_archive, "wb") as archive_file:
        with open(path_to_tar_archive, "rb") as model_data:
            for model_chunk in iter(lambda: model_data.read(CHUNK_SIZE), b""):
                compressed_chunk = compressor.compress(model_chunk)
                archive_hasher.update(compressed_chunk)
                archive_file.write(compressed_chunk)

    # Remove the tar archive
    os.remove(path_to_tar_archive)

    # Get content hash, archive size and hash
    hash = content_hasher.hexdigest()
    size = os.path.getsize(path_to_zst_archive)
    archive_hash = archive_hasher.hexdigest()

    yield path_to_zst_archive, hash, size, archive_hash

    # Remove the zstd archive
    os.remove(path_to_zst_archive)


class TrainingMixin(object):
    """
    Mixin for the Training workers to add Model and ModelVersion helpers
    """

    def publish_model_version(self, model_path: DirPath, model_id: str):
        """
        This method creates a model archive and its associated hash,
        to create a unique version that will be stored on a bucket and published on arkindex.
        """

        # Create the zst archive, get its hash and size
        with create_archive(path=model_path) as (
            path_to_archive,
            hash,
            size,
            archive_hash,
        ):
            # Create a new model version with hash and size
            model_version_details = self.create_model_version(
                model_id=model_id,
                hash=hash,
                size=size,
                archive_hash=archive_hash,
            )
            if model_version_details is None:
                return
            self.upload_to_s3(
                archive_path=path_to_archive,
                model_version_details=model_version_details,
            )

        # Update the model version with state, configuration parsed, tag, description (defaults to name of the worker)
        self.update_model_version(
            model_version_details=model_version_details,
        )

    def create_model_version(
        self,
        model_id: str,
        hash: str,
        size: int,
        archive_hash: str,
    ) -> dict:
        """
        Create a new version of the specified model with the given information (hashes and size).
        If a version matching the information already exist, there are two cases:
        - The version is in `Created` state: this version's details is used
        - The version is in `Available` state: you cannot create twice the same version, an error is raised
        """

        # Create a new model version with hash and size
        try:
            model_version_details = self.request(
                "CreateModelVersion",
                id=model_id,
                body={"hash": hash, "size": size, "archive_hash": archive_hash},
            )
        except ErrorResponse as e:
            if e.status_code >= 500:
                logger.error(f"Failed to create model version: {e.content}")

            model_version_details = e.content.get("hash")
            # If the existing model is in Created state, this model is returned as a dict.
            # Else an error in a list is returned.
            if model_version_details and isinstance(
                model_version_details, (list, tuple)
            ):
                logger.error(model_version_details[0])
                return

        return model_version_details

    def upload_to_s3(self, archive_path: str, model_version_details: dict) -> None:
        """
        Upload the archive of the model's files to an Amazon s3 compatible storage
        """

        s3_put_url = model_version_details.get("s3_put_url")
        logger.info("Uploading to s3...")
        # Upload the archive on s3
        with open(archive_path, "rb") as archive:
            r = requests.put(
                url=s3_put_url,
                data=archive,
                headers={"Content-Type": "application/zstd"},
            )
        r.raise_for_status()

    def update_model_version(
        self,
        model_version_details: dict,
        description: str = None,
        configuration: dict = None,
        tag: str = None,
    ) -> None:
        """
        Update the specified model version to the state `Available` and use the given information"
        """

        logger.info("Updating the model version...")
        try:
            self.request(
                "UpdateModelVersion",
                id=model_version_details.get("id"),
                body={
                    "state": "available",
                    "description": description,
                    "configuration": configuration,
                    "tag": tag,
                },
            )
        except ErrorResponse as e:
            logger.error(f"Failed to update model version: {e.content}")
