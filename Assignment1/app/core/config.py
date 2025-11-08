from functools import lru_cache
from typing import Literal

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class MySQLDsn(AnyUrl):
    allowed_schemes = {"mysql+asyncmy"}


class AppSettings(BaseSettings):
    app_env: Literal["development", "test", "production"] = "development"
    mysql_host: str = "localhost"
    mysql_port: int = 29906
    mysql_user: str = "medisolve"
    mysql_password: str = "medisolve"
    mysql_database: str = "medisolve"
    patient_service_url: str = "http://patient-api:8001"
    admin_service_url: str = "http://admin-api:8002"
    patient_api_prefix: str = "/api/v1/patient"
    admin_api_prefix: str = "/api/v1/admin"
    gateway_request_timeout: float = 5.0

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.development", ".env.test"),
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore",
    )

    @property
    def sqlalchemy_dsn(self) -> str:
        return (
            f"mysql+asyncmy://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()
