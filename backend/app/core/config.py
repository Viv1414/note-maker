from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Note Maker API"
    app_env: str = "development"
    database_url: str = "sqlite:///./note_maker.db"
    media_dir: str = "media"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
