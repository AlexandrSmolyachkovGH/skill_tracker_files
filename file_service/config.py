from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


class AWSSettings(BaseConfig):
    AWS_ACCESS_KEY_ID: SecretStr
    AWS_SECRET_ACCESS_KEY: SecretStr
    AWS_DEFAULT_REGION: str
    S3_BUCKET_NAME: str
    S3_ENDPOINT_URL: str


aws_settings = AWSSettings()


class SecretSettings(BaseConfig):
    SECURE_CODE: SecretStr


secret_settings = SecretSettings()


class MongoSettings(BaseConfig):
    MONGO_HOST: str
    MONGO_PORT: str
    MONGO_DB_NAME: str
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: SecretStr
    ME_CONFIG_BASICAUTH_USERNAME: str
    ME_CONFIG_BASICAUTH_PASSWORD: SecretStr


mongo_settings = MongoSettings()
