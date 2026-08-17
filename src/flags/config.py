from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_")

    file_path: str
    driver: str = "sqlite+aiosqlite"


class AllSettings(BaseSettings):
    db: DBSettings


settings = AllSettings()
