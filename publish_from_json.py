import json
from pathlib import Path

from config.settings import settings
from tools.cms_tools import (
    post_to_wordpress_raw,
    upload_image_base64_to_wordpress,
    set_post_featured_image,
)
from tools.image_tools import generate_featured_image_raw
from tools.image_file_loader import load_image_as_base64


# ✅ EDIT THIS per article you want to publish
JSON_FILENAME = "data/generated_posts/salesforce-agentforce-use-cases.json"


def inject_hero_image(content_html: str, media_url: str, title: str) -> str:
    """
    Inject a hero <img> tag right after the first <h1>...</h1> in the HTML.
    If no <h1> is found, prepend the hero image at the top.
    """
    hero_img_html = (
        f'\n<p>'
        f'<img src="{media_url}" alt="{title}" loading="lazy" '
        f'style="max-width:100%;height:auto;border-radius:12px;margin:16px 0;" />'
        f'</p>\n'
    )

    lower_html = content_html.lower()
    h1_close_idx = lower_html.find("</h1>")

    if h1_close_idx != -1:
        insert_pos = h1_close_idx + len("</h1>")
        return content_html[:insert_pos] + hero_img_html + content_html[insert_pos:]
    else:
        return hero_img_html + content_html



def get_best_media_url(media_json: dict) -> str | None:
    """
    Try to pick a valid image URL from the WordPress media JSON.
    Priority:
    1) guid.rendered (original upload URL)
    2) media_details.sizes.full.source_url (or large/medium)
    3) top-level source_url
    """
    # 1) Original uploaded URL
    url = media_json.get("guid", {}).get("rendered")
    if url:
        return url

    # 2) Look into media_details.sizes
    details = media_json.get("media_details", {})
    sizes = details.get("sizes", {}) or {}
    if isinstance(sizes, dict) and sizes:
        for size_name in ["full", "large", "medium_large", "medium"]:
            size = sizes.get(size_name)
            if size and "source_url" in size:
                return size["source_url"]

    # 3) Fallback to source_url
    return media_json.get("source_url")



def publish_from_json(json_path: str):
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    print(f"📄 Loading article JSON from: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))

    title = data["title"]
    slug = data["slug"]
    meta_description = data["meta_description"]
    content_html = data["content_html"]

    print("📝 Title:", title)
    print("📝 Slug:", slug)

    # ----------------------------------------------------
    # 1️⃣ Decide image strategy: MOCK vs REAL
    # ----------------------------------------------------
    if settings.GEMINI_IMAGE_MOCK:
        print("\n🧪 MOCK MODE: Using local test image instead of Gemini...")

        # Load your real test image (adjust name if needed)
        local_img_path = "data/test_images/sample.png"
        img_b64 = load_image_as_base64(local_img_path)

        print("📤 Uploading local test image to WordPress media library...")
        media_json = upload_image_base64_to_wordpress(img_b64, filename=f"{slug}.png")
        media_id = media_json.get("id")
        media_url = get_best_media_url(media_json)

        print("📦 Full media JSON (debug, first 500 chars):")
        print(str(media_json)[:500])

        print(f"🎉 Uploaded LOCAL TEST IMAGE. Media ID = {media_id}")
        print("🖼️ Test Image URL:", media_url)



    else:
        # REAL MODE → call Gemini + upload to WP
        print("\n🖼️ Generating featured image via Gemini...")
        prompt = (
            f"Featured image for blog article titled '{title}'. "
            "Minimal, flat tech illustration, Salesforce automation theme, 16:9 aspect ratio."
        )
        img_b64 = generate_featured_image_raw(prompt)

        print("📤 Uploading image to WordPress media library...")
        media_json = upload_image_base64_to_wordpress(img_b64, filename=f"{slug}.png")
        media_id = media_json.get("id")
        media_url = get_best_media_url(media_json)

        print("📦 Full media JSON (debug, first 500 chars):")
        print(str(media_json)[:500])

        print(f"🎉 Uploaded LOCAL TEST IMAGE. Media ID = {media_id}")
        print("🖼️ Test Image URL:", media_url)


    # ----------------------------------------------------
    # 2️⃣ Inject hero <img> into HTML content (both modes)
    # ----------------------------------------------------
    print("\n🧩 Injecting hero image into article HTML...")
    content_with_hero = inject_hero_image(content_html, media_url, title)

    # ----------------------------------------------------
    # 3️⃣ Create the WordPress Post (draft)
    # ----------------------------------------------------
    print("\n📨 Creating WordPress post as draft...")
    post_json = post_to_wordpress_raw(
        title=title,
        content=content_with_hero,
        slug=slug,
        excerpt=meta_description,
    )

    post_id = post_json.get("id")
    post_link = post_json.get("link")
    print(f"📝 Post created with ID: {post_id}")
    print("🔗 Draft URL:", post_link)

    # ----------------------------------------------------
    # 4️⃣ Attach Featured Image (only in REAL mode)
    # ----------------------------------------------------
    if not settings.GEMINI_IMAGE_MOCK and media_id:
        print("\n📌 Setting featured image on the post...")
        updated_post = set_post_featured_image(post_id, media_id)
        print("Post 'featured_media' field:", updated_post.get("featured_media"))
    else:
        print("\n📌 Skipping featured_media update (MOCK mode).")

    print("\n✅ DONE — Post created with hero image injected into content!")
    print("Final Post URL:", post_link)


if __name__ == "__main__":
    publish_from_json(JSON_FILENAME)
