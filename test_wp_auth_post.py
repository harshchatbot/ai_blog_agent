import base64
import os
import requests
from dotenv import load_dotenv

load_dotenv()

WP_BASE_URL = os.getenv("WP_BASE_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

auth = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
token = base64.b64encode(auth.encode()).decode()

headers = {
    "Authorization": f"Basic {token}",
    "Content-Type": "application/json"
}

url = f"{WP_BASE_URL.rstrip('/')}/wp-json/wp/v2/posts"
payload = {
    "title": "Auth Test from ai_blog_agent",
    "status": "draft"
}

print("Testing POST to:", url)
print("With username:", WP_USERNAME)

res = requests.post(url, json=payload, headers=headers)
print("Status code:", res.status_code)
print("Body:", res.text[:500])
