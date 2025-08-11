from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
)
from pydantic import ValidationError

from file_service.connections.mongo_connection import mongo_tool
from file_service.schemes.outbox import OutboxScheme


class OutboxMongoRepository:
    def __init__(self) -> None:
        self.coll = "file_keys"

    @property
    def db(self) -> AsyncIOMotorDatabase:
        return mongo_tool.get_mongo_db()

    async def add_document(self, document: dict) -> None:
        try:
            data = OutboxScheme(**document)
        except ValidationError as e:
            raise e

        validated_doc = data.model_dump()
        await self.db[self.coll].insert_one(validated_doc)

    async def get_document(self, key: str) -> dict:
        """
        Get relevant doc by using unique key
        """
        doc = await self.db[self.coll].find_one({"key": key})
        if not doc:
            raise ValueError(f"Key {key} not found or already deleted")
        try:
            data = OutboxScheme(**doc)
        except ValidationError as e:
            raise e
        return data.model_dump()

    async def get_one_unsent_document(self) -> dict | None:
        """
        Get one document with the status False
        """
        doc = await self.db[self.coll].find_one({"status": False})
        if not doc:
            return None
        try:
            data = OutboxScheme(**doc)
        except ValidationError as e:
            raise e
        return data.model_dump()

    async def change_status(self, key: str, status: bool = True) -> None:
        await self.db[self.coll].update_one(
            {"key": key},
            {"$set": {"status": status}},
        )

    async def delete_documents(self, status: bool = True) -> None:
        """
        Delete all delivered documents
        """
        await self.db[self.coll].delete_many({"status": status})


outbox_repository = OutboxMongoRepository()
