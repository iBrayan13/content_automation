from pydantic_settings import BaseSettings, SettingsConfigDict


class GlobalSettings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_MODEL_NAME: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")