import asyncio
import json

from aiokafka import AIOKafkaProducer
from aiokafka.admin import (
    AIOKafkaAdminClient,
    NewTopic,
)
from aiokafka.errors import (
    KafkaError,
    TopicAlreadyExistsError,
)
from aiokafka.structs import RecordMetadata

from file_service.config import kafka_settings
from file_service.custom_exceptions.custom import TransactionalOutboxError
from file_service.repositories.outbox import (
    OutboxMongoRepository,
)
from file_service.repositories.outbox import outbox_repository as repo
from file_service.schemes.outbox import OutboxScheme
from logger.logger_conf import logger


class KafkaTopicChecker:
    def __init__(
        self,
        bootstrap_servers: str,
        kafka_topic: str,
    ) -> None:
        self.bootstrap = bootstrap_servers
        self.kafka_topic = kafka_topic
        self.admin_client: AIOKafkaAdminClient | None = None

    def get_new_topic(
        self,
        n_partitions: int = 2,
        n_replicas: int = 1,
    ) -> NewTopic:
        return NewTopic(
            name=self.kafka_topic,
            num_partitions=n_partitions,
            replication_factor=n_replicas,
        )

    async def start(self) -> None:
        self.admin_client = AIOKafkaAdminClient(
            bootstrap_servers=self.bootstrap,
        )
        await self.admin_client.start()

    async def stop(self) -> None:
        if self.admin_client is not None:
            await self.admin_client.close()
            self.admin_client = None

    async def ensure_topic(
        self,
        n_partitions: int = 2,
        n_replicas: int = 1,
    ) -> None:
        if self.admin_client is None:
            raise RuntimeError(
                "KafkaTopicChecker is not started. Call the method start."
            )
        topic = self.get_new_topic(n_partitions, n_replicas)
        backoff = 1.0
        for attempt in range(5):
            try:
                await self.admin_client.create_topics([topic])
                return
            except TopicAlreadyExistsError:
                return
            except KafkaError:
                if attempt == 4:
                    raise
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 10)


kafka_topic_checker = KafkaTopicChecker(
    bootstrap_servers=kafka_settings.ENTRY_POINT,
    kafka_topic=kafka_settings.FILE_TOPIC,
)


class BaseKafkaProducer:
    def __init__(
        self,
        bootstrap_servers: str,
        kafka_topic: str,
    ) -> None:
        self.bootstrap = bootstrap_servers
        self.kafka_topic = kafka_topic
        self.producer: AIOKafkaProducer | None = None

    async def open_connection(self) -> None:
        if self.producer is None:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap,
            )
        await self.producer.start()

    async def close_connection(self) -> None:
        if self.producer is not None:
            await self.producer.stop()


class KafkaFileProducer(BaseKafkaProducer):
    """
    Aiokafka producer that delivers file keys to the core service
    """

    def __init__(
        self,
        bootstrap_servers: str,
        kafka_topic: str,
        outbox_repository: OutboxMongoRepository = repo,
    ) -> None:
        super().__init__(
            bootstrap_servers=bootstrap_servers,
            kafka_topic=kafka_topic,
        )
        self.outbox_repository = outbox_repository

    async def send_file_key_to_core(
        self,
        key_doc: bytes,
    ) -> RecordMetadata:
        if self.producer is None:
            raise RuntimeError("KafkaFileProducer is not started.")
        metadata = await self.producer.send_and_wait(
            topic=self.kafka_topic,
            value=key_doc,
        )
        return metadata

    async def check_files_in_mongo(
        self,
        poll_interval: float = 3,
    ) -> None:
        while True:
            try:
                logger.debug("Try to get record from the mongo")
                event = await self.outbox_repository.get_one_unsent_document()

                if not event:
                    logger.debug("There are no active records")
                    await asyncio.sleep(poll_interval)
                    continue
                logger.debug(f"Record received - {event}")
                data = OutboxScheme(**event)
                bytes_data = json.dumps(data.model_dump()).encode("utf-8")
                metadata = await self.send_file_key_to_core(
                    key_doc=bytes_data,
                )
                if metadata.topic == self.kafka_topic:
                    await self.outbox_repository.change_status(
                        key=data.key,
                    )
            except TransactionalOutboxError:
                await asyncio.sleep(poll_interval)


file_producer = KafkaFileProducer(
    bootstrap_servers=kafka_settings.ENTRY_POINT,
    kafka_topic=kafka_settings.FILE_TOPIC,
)
