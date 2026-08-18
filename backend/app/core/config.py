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
    iss: str


    # --- redis ---
    redis_host: str
    redis_port: int
    redis_db: int

    # --- reset password ---
    reset_token_expire_second: int
    admin_reset_token_expire_second: int = 86400  # Mặc định 24 giờ cho link do admin tạo
    frontend_url: str

    # --- smtp server ---
    mail_server: str
    mail_port: int
    mail_use_tls: bool
    mail_use_ssl: bool
    mail_username: str | None = None
    mail_password: str | None = None
    mail_default_sender: str | None = None

    # --- database url ---
    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = SettingsConfigDict(env_file=os.getenv("ENV_FILE", ".env"), extra="ignore")

settings = Settings()