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

settings = Settings()
