from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from _pytest.monkeypatch import MonkeyPatch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pytest_mock import MockerFixture

from file_service.main import app as real_app


@pytest.fixture(autouse=True)
def fake_env(
    monkeypatch: MonkeyPatch,
) -> None:
    # AWS SETTINGS
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")
    monkeypatch.setenv("S3_BUCKET_NAME", "files")
    monkeypatch.setenv("S3_ENDPOINT_URL", "http://localstack:4566")

    # SECURE CODE
    monkeypatch.setenv("SECURE_CODE", "file_secure_code_123")

    # MONGODB
    monkeypatch.setenv("MONGO_HOST", "mongo")
    monkeypatch.setenv("MONGO_PORT", "27017")
    monkeypatch.setenv("MONGO_DB_NAME", "file_keys")
    monkeypatch.setenv("MONGO_INITDB_ROOT_USERNAME", "root")
    monkeypatch.setenv("MONGO_INITDB_ROOT_PASSWORD", "example")
    monkeypatch.setenv("ME_CONFIG_BASICAUTH_USERNAME", "admin")
    monkeypatch.setenv("ME_CONFIG_BASICAUTH_PASSWORD", "admin")


MockS3RepoMethods = tuple[AsyncMock, AsyncMock]


@pytest.fixture
def mock_s3_repo_methods(
    mocker: MockerFixture,
) -> MockS3RepoMethods:
    mock_upload_file = mocker.patch(
        "file_service.repositories.files.S3Repository.upload_file",
    )
    mock_upload_file.return_value = "mocked_file_key"
    mock_download_file = mocker.patch(
        "file_service.repositories.files.S3Repository.download_file",
    )
    mock_download_file.return_value = (b"mocked content", "text/plain")
    return mock_upload_file, mock_download_file


MockOutboxRepoMethods = tuple[AsyncMock, AsyncMock, AsyncMock, AsyncMock]


@pytest.fixture
def mock_outbox_repo_methods(
    mocker: MockerFixture,
) -> MockOutboxRepoMethods:
    mock_add_document = mocker.patch(
        "file_service.repositories.outbox.OutboxMongoRepository.add_document",
    )
    mock_add_document.return_value = None
    mock_get_document = mocker.patch(
        "file_service.repositories.outbox.OutboxMongoRepository.get_document",
    )
    mock_add_document.return_value = {"key": "test_document", "status": False}
    mock_change_status = mocker.patch(
        "file_service.repositories.outbox.OutboxMongoRepository.change_status",
    )
    mock_change_status.return_value = None
    mock_delete_documents = mocker.patch(
        "file_service.repositories.outbox.OutboxMongoRepository.delete_documents",
    )
    mock_delete_documents.return_value = None
    return (
        mock_add_document,
        mock_get_document,
        mock_change_status,
        mock_delete_documents,
    )


@pytest.fixture
def session_mock() -> MagicMock:
    return MagicMock()


@pytest.fixture
def client_mock() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_response() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def app_without_lifespan() -> FastAPI:
    app = FastAPI()
    app.include_router(real_app.router)
    return app


@pytest_asyncio.fixture
async def client(app_without_lifespan: FastAPI) -> AsyncClient:
    transport = ASGITransport(app=app_without_lifespan)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
