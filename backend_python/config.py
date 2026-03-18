import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "")
    DATABASE_URL: str = (
        os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("DATABASE_PRIVATE_URL")
        or ""
    )
    SERVER_PORT: str = (
        os.getenv("SERVER_PORT")
        or os.getenv("PORT")
        or "8000"
    )
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT") or "587")
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "English Story")
    API_TOKEN: str = os.getenv("API_TOKEN", "")


config = Config()
