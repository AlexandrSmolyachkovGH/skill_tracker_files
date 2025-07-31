from pydantic import (
    BaseModel,
    Field,
)


class OutboxScheme(BaseModel):
    key: str
    status: bool = Field(
        description="Delivering status to the Kafka topic",
        default=False,
    )
