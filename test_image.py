from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID"),
    project=os.getenv("OPENAI_PROJECT_ID"),
)

img = client.images.generate(
    model="gpt-image-1.5",
    prompt="A simple black-and-white flowchart diagram: Start -> Validate -> Process -> Done",
    size="1024x1024",
)
print("OK b64 length:", len(img.data[0].b64_json))
