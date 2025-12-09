import base64
from pathlib import Path

def load_image_as_base64(image_path: str) -> str:
    """
    Load a local PNG/JPG image and return base64 string.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Local test image not found: {path}")

    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
