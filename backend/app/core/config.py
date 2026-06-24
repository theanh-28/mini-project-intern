import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    @property
    def database_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = os.getenv("ENV_FILE", ".env")

settings = Settings()