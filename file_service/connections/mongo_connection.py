from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)
from file_service.config import mongo_settings as conf


class MongoTool:
    def __init__(self) -> None:
        self.mongo_client: AsyncIOMotorClient | None = None
        self.mongo_db: AsyncIOMotorDatabase | None = None

    def get_mongo_uri(self) -> str:
        username = conf.MONGO_INITDB_ROOT_USERNAME
        password = conf.MONGO_INITDB_ROOT_PASSWORD.get_secret_value()
        host = conf.MONGO_HOST
        port = conf.MONGO_PORT
        return (
            f"mongodb://{username}:{password}@"
            f"{host}:{port}/?authSource=admin"
        )

    def get_mongo_client(
        self,
        mongo_uri: str | None = None,
    ) -> AsyncIOMotorClient:
        if self.mongo_client is None:
            if mongo_uri is None:
                raise ValueError(
                    "MongoDB client must be initialized. "
                    "Provide mongo_uri to initialize the client."
                )
            self.mongo_client = AsyncIOMotorClient(mongo_uri)
        return self.mongo_client

    def get_mongo_db(
        self,
        db_name: str = conf.MONGO_DB_NAME,
    ) -> AsyncIOMotorDatabase:
        if self.mongo_client is None:
            try:
                self.mongo_client = self.get_mongo_client(
                    mongo_uri=self.get_mongo_uri(),
                )
            except Exception as e:
                raise ValueError(
                    f"Mongo client is not initialized. {e}"
                )
        if self.mongo_db is None:
            self.mongo_db = self.mongo_client[db_name]
        return self.mongo_db

    def close(self) -> None:
        if self.mongo_client:
            self.mongo_client.close()
            self.mongo_client = None
            self.mongo_db = None


mongo_tool = MongoTool()
