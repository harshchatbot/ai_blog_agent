import base64
import json
import requests
from crewai.tools import tool
from config.settings import settings

GEMINI_API_KEY = settings.GEMINI_API_KEY
GEMINI_IMAGE_MODEL = settings.GEMINI_IMAGE_MODEL

GEMINI_IMAGE_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_IMAGE_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

def generate_featured_image_raw(prompt: str) -> str:
    """
    RAW function: Generate image using Gemini and return base64 PNG string.
    In mock mode, returns a fake base64 string so the pipeline can be tested
    without hitting Gemini or consuming quota.
    """

    # ✅ Mock mode: don't call Gemini, just return a dummy placeholder
    if settings.GEMINI_IMAGE_MOCK:
        print("[Gemini] MOCK mode enabled – returning dummy image base64.")
        # This is just "hello" in base64 – enough to test wiring, not a real image.
        return "aGVsbG8="

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in .env")

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "imageConfig": {
                "aspectRatio": "16:9"
            }
        }
    }

    res = requests.post(GEMINI_IMAGE_URL, json=payload)

    if res.status_code == 429:
        # Fail gracefully in dev:
        raise RuntimeError(
            f"Gemini API rate limited (429). Check your quota in Google AI Studio. "
            f"Body: {res.text[:300]}"
        )

    res.raise_for_status()
    data = res.json()

    try:
        candidates = data["candidates"]
        parts = candidates[0]["content"]["parts"]

        for part in parts:
            if "inlineData" in part:
                return part["inlineData"]["data"]

        raise ValueError("No inline image data found in Gemini response")

    except Exception as e:
        raise ValueError(f"Failed to parse Gemini image response: {e}\nRaw: {json.dumps(data)[:500]}")


@tool("Generate Featured Image with Gemini")
def generate_featured_image(prompt: str) -> str:
    """
    CrewAI Tool wrapper (calls the RAW function).
    Use generate_featured_image_raw() for manual tests.
    """
    img = generate_featured_image_raw(prompt)
    return f"Image generated (base64 length: {len(img)})"
