# -*- coding: utf-8 -*-
import os

import pytest
import responses

from arkindex.mock import MockApiClient
from arkindex_worker.worker import BaseWorker
from arkindex_worker.worker.training import TrainingMixin, create_archive


class TrainingWorker(BaseWorker, TrainingMixin):
    """
    This class is only needed for tests
    """

    pass


def test_create_archive(model_file_dir):
    """Create an archive when the model's file is in a folder"""

    with create_archive(path=model_file_dir) as (
        zst_archive_path,
        hash,
        size,
        archive_hash,
    ):
        assert os.path.exists(zst_archive_path), "The archive was not created"
        assert (
            hash == "c5aedde18a768757351068b840c8c8f9"
        ), "Hash was not properly computed"
        assert 300 < size < 700

    assert not os.path.exists(zst_archive_path), "Auto removal failed"


def test_create_model_version():
    """A new model version is returned"""

    model_id = "fake_model_id"
    model_version_id = "fake_model_version_id"
    training = TrainingWorker()
    training.api_client = MockApiClient()
    model_hash = "hash"
    archive_hash = "archive_hash"
    size = "30"
    model_version_details = {
        "id": model_version_id,
        "model_id": model_id,
        "hash": model_hash,
        "archive_hash": archive_hash,
        "size": size,
        "s3_url": "http://hehehe.com",
        "s3_put_url": "http://hehehe.com",
    }

    training.api_client.add_response(
        "CreateModelVersion",
        id=model_id,
        response=model_version_details,
        body={"hash": model_hash, "archive_hash": archive_hash, "size": size},
    )
    assert (
        training.create_model_version(model_id, model_hash, size, archive_hash)
        == model_version_details
    )


@pytest.mark.parametrize(
    "content, status_code",
    [
        (
            {
                "hash": {
                    "id": "fake_model_version_id",
                    "model_id": "fake_model_id",
                    "hash": "hash",
                    "archive_hash": "archive_hash",
                    "size": "size",
                    "s3_url": "http://hehehe.com",
                    "s3_put_url": "http://hehehe.com",
                }
            },
            400,
        ),
        ({"hash": ["A version for this model with this hash already exists."]}, 403),
    ],
)
def test_retrieve_created_model_version(content, status_code):
    """
    If there is an existing model version in Created mode,
    A 400 was raised, but the model is still returned in error content.
    Else if an existing model version in Available mode,
    403 was raised, but None will be returned
    """

    model_id = "fake_model_id"
    training = TrainingWorker()
    training.api_client = MockApiClient()
    model_hash = "hash"
    archive_hash = "archive_hash"
    size = "30"
    training.api_client.add_error_response(
        "CreateModelVersion",
        id=model_id,
        status_code=status_code,
        body={"hash": model_hash, "archive_hash": archive_hash, "size": size},
        content=content,
    )
    if status_code == 400:
        assert (
            training.create_model_version(model_id, model_hash, size, archive_hash)
            == content["hash"]
        )
    elif status_code == 403:
        assert (
            training.create_model_version(model_id, model_hash, size, archive_hash)
            is None
        )


def test_handle_s3_uploading_errors(model_file_dir):
    training = TrainingWorker()
    training.api_client = MockApiClient()
    s3_endpoint_url = "http://s3.localhost.com"
    responses.add_passthru(s3_endpoint_url)
    responses.add(responses.Response(method="PUT", url=s3_endpoint_url, status=400))
    file_path = model_file_dir / "model_file.pth"
    with pytest.raises(Exception):
        training.upload_to_s3(file_path, {"s3_put_url": s3_endpoint_url})
