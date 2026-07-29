from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    CONEKTA_API_KEY: str = ""
    CONEKTA_PUBLIC_KEY: str = ""
    CONEKTA_WEBHOOK_SECRET: str = ""
    CONEKTA_WEBHOOK_PUBLIC_KEY: str = ""
    LOG_LEVEL: str = "DEBUG"
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
