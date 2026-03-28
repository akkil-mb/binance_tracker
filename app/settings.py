import os
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).resolve().parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

class BaseSettings:
    CORS_ORIGINS = os.getenv("CORS_ORIGINS")
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")

    def validate(self):
        required = {
            "DATABASE_URL": self.DATABASE_URL,
            "SECRET_KEY": self.SECRET_KEY
        }

        missing = [key for key, value in required.items() if not value]

        if missing:
            raise ValueError(f"Missing required env variables {', '.join(missing)}")
