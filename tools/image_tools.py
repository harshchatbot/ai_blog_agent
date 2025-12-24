# tools/image_tools_openai.py
import base64
from openai import OpenAI
from config.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_diagram_image_b64(prompt: str) -> str:
    """
    Returns base64 png bytes as a base64 string (no data: prefix).
    """
    img = client.images.generate(
        model="gpt-image-1.5",   # best quality
        prompt=prompt,
        size="1536x1024",        # nice for blog diagrams (landscape)
        n=1
    )
    return img.data[0].b64_json  # GPT image models return base64 always :contentReference[oaicite:1]{index=1}

def b64_to_bytes(b64_str: str) -> bytes:
    return base64.b64decode(b64_str)
