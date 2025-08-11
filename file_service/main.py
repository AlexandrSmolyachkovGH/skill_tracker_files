from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI

from file_service.config import aws_settings
from file_service.connections.mongo_connection import mongo_tool
from file_service.connections.s3_connection import (
    ensure_bucket_exists,
    get_aws_session,
    get_s3_client,
    wait_for_localstack,
)
from file_service.kafka.producer import file_producer
from file_service.msg_creator import msg_creator
from file_service.routers.files import router as file_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await wait_for_localstack(
        url=aws_settings.S3_ENDPOINT_URL,
    )

    await file_producer.open_connection()
    app.state.file_producer = file_producer

    mongo_tool.mongo_init()

    session = get_aws_session()
    async with get_s3_client(session=session) as s3_client:
        await ensure_bucket_exists(
            bucket_name=aws_settings.S3_BUCKET_NAME,
            client=s3_client,
        )

        try:
            yield
        finally:
            mongo_tool.close()
            await file_producer.close_connection()


app = FastAPI(lifespan=lifespan)
app.include_router(file_router)


@app.get("/", tags=["root"])
async def root() -> dict:
    return {
        "title": msg_creator.get_root_title(),
        "description": msg_creator.get_root_description(),
        "paths": {
            "swagger": "/docs",
            "redoc": "/redoc",
        },
    }


if __name__ == "__main__":
    uvicorn.run(
        "file_service.main:app",
        host="localhost",
        port=8002,
    )
