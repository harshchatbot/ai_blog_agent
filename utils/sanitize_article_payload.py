def sanitize_article_payload(article: dict) -> dict:
    """
    Ensures that mandatory article fields exist.
    If missing, fill with placeholder values so local LLM failures don't crash pipeline.
    """

    required = {
        "title": "Untitled Article",
        "slug": "untitled-article",
        "excerpt": "This is an auto-generated excerpt.",
        "content_html": "<p>No content provided.</p>"
    }

    cleaned = {}

    for key, default in required.items():
        value = article.get(key)

        # If missing, empty, or None → replace
        if not value or not isinstance(value, str):
            cleaned[key] = default
        else:
            cleaned[key] = value.strip()

    # Return the entire structure, preserving extra fields if present
    # But ensuring required ones are present
    return {**article, **cleaned}
