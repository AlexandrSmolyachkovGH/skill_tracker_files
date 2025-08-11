from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_mock import MockerFixture

from file_service.config import aws_settings, mongo_settings, secret_settings
from file_service.routers.files import upload_file
from file_service.services.files import s3_service
from tests.conftest import MockOutboxRepoMethods, MockS3RepoMethods


@pytest.mark.asyncio
async def test_s3service(
    mock_s3_repo_methods: MockS3RepoMethods,
    mock_outbox_repo_methods: MockOutboxRepoMethods,
) -> None:
    file_name = "test_file"
    content_type = "application/octet-stream"
    content = file_name.encode("utf-8")

    service = s3_service

    key = service.build_key(filename=file_name)
    assert isinstance(key, str)
    assert key.endswith("_" + file_name)

    upload_file_key = await service.upload_file(
        content=content,
        content_type=content_type,
        filename=file_name,
    )
    assert isinstance(upload_file_key, str)
    assert upload_file_key == "mocked_file_key"
    service.s3_repo.upload_file.assert_awaited_once()
    service.outbox_repo.add_document.assert_awaited_once()

    download_file = await service.download_file(key=key)
    assert isinstance(download_file, tuple)
    assert download_file == (b"mocked content", "text/plain")
    service.s3_repo.download_file.assert_awaited_once()
