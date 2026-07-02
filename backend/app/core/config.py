import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- database ---
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    # --- general ---
    debug: bool = False

    # --- jwt ---
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


    # --- redis ---
    redis_host: str
    redis_port: int
    redis_db: int

    # --- database url ---
    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = SettingsConfigDict(env_file=os.getenv("ENV_FILE", ".env"))

settings = Settings()