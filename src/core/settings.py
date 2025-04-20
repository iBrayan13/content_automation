from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    ADMINISTRATOR_IDS: List[str]
    PROJECT_FLAG: str

    OPENAI_API_KEY: str
    OPENAI_MODEL_NAME: str = "gpt-4o"
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL_NAME: str = "claude-3-5-sonnet"
    DEEPSEEK_API_KEY: str
    DEEPSEEK_MODEL_NAME: str = "deepseek-chat"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")