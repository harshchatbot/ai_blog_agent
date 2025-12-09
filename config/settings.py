import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

    WP_BASE_URL = os.getenv("WP_BASE_URL")
    WP_USERNAME = os.getenv("WP_USERNAME")
    WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

    DEFAULT_CATEGORY_ID = int(os.getenv("DEFAULT_CATEGORY_ID", 1))
    DEFAULT_AUTHOR_ID = int(os.getenv("DEFAULT_AUTHOR_ID", 1))

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
    GEMINI_IMAGE_MOCK = os.getenv("GEMINI_IMAGE_MOCK", "false").lower() == "true"

settings = Settings()
