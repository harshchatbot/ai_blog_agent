import base64
import requests
from crewai.tools import tool
from config.settings import settings

def post_to_wordpress_raw(title: str, content: str, slug: str, excerpt: str) -> dict:
    """Low-level helper: Post an article to WordPress as a draft and return raw JSON."""
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
        "categories": [settings.DEFAULT_CATEGORY_ID],
        "author": settings.DEFAULT_AUTHOR_ID
    }

    res = requests.post(
    f"{settings.WP_BASE_URL.rstrip('/')}/wp-json/wp/v2/posts",
    json=payload,
    headers=headers
    )

    print("Status:", res.status_code)
    print("Response text:", res.text[:500])  # debug, first 500 chars

    res.raise_for_status()
    return res.json()



@tool("Post to WordPress")
def post_to_wordpress(title: str, content: str, slug: str, excerpt: str) -> str:
    """
    CrewAI Tool: Post an article to WordPress as a draft.
    Returns a short string summary for the agent.
    """
    res = post_to_wordpress_raw(title, content, slug, excerpt)
    post_id = res.get("id")
    link = res.get("link")
    status = res.get("status")
    return f"Posted to WordPress. id={post_id}, status={status}, link={link}"




def upload_image_base64_to_wordpress(image_base64: str, filename: str = "featured.png"):
    """
    Uploads a base64 PNG image to WordPress and returns media JSON (includes media ID).
    Uses multipart/form-data which is the most compatible way with WordPress hosts.
    """

    auth = f"{settings.WP_USERNAME}:{settings.WP_APP_PASSWORD}"
    token = base64.b64encode(auth.encode()).decode()

    binary_data = base64.b64decode(image_base64)

    url = settings.WP_BASE_URL.rstrip("/") + "/wp-json/wp/v2/media"

    headers = {
        "Authorization": f"Basic {token}",
        # DO NOT set Content-Type here, requests will set correct multipart boundary
    }

    files = {
        "file": (filename, binary_data, "image/png"),
    }

    print("📤 Uploading image via multipart/form-data to:", url)
    response = requests.post(url, headers=headers, files=files)

    print("🔍 Media upload status:", response.status_code)
    print("🔍 Media upload response (first 500 chars):", response.text[:500])

    response.raise_for_status()
    return response.json()






def set_post_featured_image(post_id: int, media_id: int):
    """
    Updates a WordPress post so that the given media_id becomes the featured image.
    """
    auth = f"{settings.WP_USERNAME}:{settings.WP_APP_PASSWORD}"
    token = base64.b64encode(auth.encode()).decode()

    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "featured_media": media_id
    }

    url = settings.WP_BASE_URL.rstrip("/") + f"/wp-json/wp/v2/posts/{post_id}"

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
