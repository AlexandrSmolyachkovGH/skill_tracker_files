from unittest.mock import MagicMock

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from file_service.connections.mongo_connection import mongo_tool


def test_get_mongo_uri() -> None:
    uri = mongo_tool.get_mongo_uri()

    assert isinstance(uri, str)
    assert uri.startswith("mongodb://")
    assert uri.endswith("/?authSource=admin")


test_uri = mongo_tool.get_mongo_uri()


def test_get_mongo_client(
    mongo_uri: str = test_uri,
) -> None:
    client = mongo_tool.get_mongo_client(mongo_uri)

    assert isinstance(client, AsyncIOMotorClient)


def test_get_mongo_db() -> None:
    db = mongo_tool.get_mongo_db()

    assert isinstance(db, AsyncIOMotorDatabase)


def test_close_mongo_connection() -> None:
    mock_client = MagicMock()
    mongo_tool.mongo_client = mock_client
    mongo_tool.mongo_db = MagicMock()

    mongo_tool.close()

    mock_client.close.assert_called_once()
    assert mongo_tool.mongo_client is None
    assert mongo_tool.mongo_db is None
