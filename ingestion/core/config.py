from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str
    # Debe ser el mismo modelo que carga retrieval-api (ver
    # retrieval-api/app/core/config.py): si difieren, las queries y los
    # chunks quedan en espacios vectoriales distintos. No hay forma de
    # compartir este valor entre los dos servicios más que mantenerlo
    # sincronizado a mano en ambos .env.
    EMBEDDING_MODEL_NAME: str
    GITHUB_TOKEN: str | None = None


settings = Settings()
