import os

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = Field(..., env='DATABASE_URL')

settings = Settings()