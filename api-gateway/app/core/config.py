import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- general ---
    debug: bool = False

    # --- jwt ---
    secret_key: str
    algorithm: str = "HS256"

    # --- redis ---
    redis_host: str
    redis_port: int
    redis_db: int

    # --- url backend ---
    backend_url: str = "http://localhost:5000"

    # --- Bản đồ định tuyến ---
    @property
    def router_map(self) -> dict[str, str]:
        return {
            "/auth": self.backend_url,
            "/admin/users": self.backend_url
        }


    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        extra="ignore"
    )


settings = Settings()
