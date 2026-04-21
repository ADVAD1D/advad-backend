import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    APP_TOKEN: str = os.getenv("APP_TOKEN")
    ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY")
    PORT: int = int(os.getenv("PORT", 10000))
    DATABASE_URL: str = os.getenv("DATABASE_URL")

settings = Settings()
