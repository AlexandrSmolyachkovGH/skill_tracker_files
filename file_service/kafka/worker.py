import asyncio

from file_service.connections.mongo_connection import mongo_tool
from file_service.custom_exceptions.custom import TransactionalOutboxError
from file_service.kafka.producer import (
    file_producer,
    kafka_topic_checker,
)
from logger.logger_conf import logger


async def main() -> None:
    mongo_tool.mongo_init()

    await kafka_topic_checker.start()
    await kafka_topic_checker.ensure_topic()

    await file_producer.open_connection()
    try:
        await file_producer.check_files_in_mongo()
    except asyncio.CancelledError:
        pass
    except TransactionalOutboxError as e:
        logger.error(e)
        await asyncio.sleep(5)
    finally:
        await file_producer.close_connection()
        mongo_tool.close()


if __name__ == "__main__":
    asyncio.run(main())
