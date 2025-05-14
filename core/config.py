from pathlib import Path
from pydantic_settings import BaseSettings
import os 
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent

UPLOAD_DIR = "images"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# static files
STATIC_MOUNT_PATH = "/images"
STATIC_DIR = UPLOAD_DIR


class Setting(BaseSettings):
    user: str = os.getenv("user")
    password: str = os.getenv("password")
    host: str = os.getenv("host")
    port: str = os.getenv("port")
    database: str = os.getenv("database")

    api_v1_prefix: str = "/api/v1"

    #posgreesql settings example
    db_url: str = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
    db_echo: bool = False
    # db_echo: bool = True


settings = Setting()