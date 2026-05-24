from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "DocuShield API"
    api_version: str = "v1"
    registry_timeout_seconds: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
