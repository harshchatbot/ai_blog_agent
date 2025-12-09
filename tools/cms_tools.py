import base64
import requests
from crewai.tools import tool
from config.settings import settings

@tool
def post_to_wordpress(title: str, content: str, slug: str, excerpt: str):
    """Post an article to WordPress as a draft."""
    auth = f"{settings.WP_USERNAME}:{settings.WP_APP_PASSWORD}"
    token = base64.b64encode(auth.encode()).decode()

    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "title": title,
        "content": content,
        "slug": slug,
        "excerpt": excerpt,
        "status": "draft",
        "author": settings.DEFAULT_AUTHOR_ID,
        "categories": [settings.DEFAULT_CATEGORY_ID]
    }

    response = requests.post(
        f"{settings.WP_BASE_URL}/wp-json/wp/v2/posts",
        json=payload, headers=headers
    )
    response.raise_for_status()
    return response.json()
