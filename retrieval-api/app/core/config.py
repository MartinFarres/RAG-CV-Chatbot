from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    GROQ_API_KEY: str
    DATABASE_URL: str
    EMBEDDING_MODEL_NAME: str
    LLM_MODEL: str


settings = Settings()
