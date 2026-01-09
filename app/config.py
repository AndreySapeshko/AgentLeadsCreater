from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(BASE_DIR / ".env")

OPEN_AI_KEY = env("OPEN_AI_KEY", default="my_open_ai_key")

TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", default="my_telegrambot_token")

POSTGRES_DB = env("POSTGRES_DB", default="agent_researcher")
POSTGRES_USER = env("POSTGRES_USER", default="postgres")
POSTGRES_PASSWORD = env("POSTGRES_PASSWORD", default="my_password")
POSTGRES_HOST = env("POSTGRES_HOST", default="localhost")
POSTGRES_PORT = env("POSTGRES_PORT", default="5432")

DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:" f"{POSTGRES_PASSWORD}@{POSTGRES_HOST}:" f"{POSTGRES_PORT}/{POSTGRES_DB}"
)
