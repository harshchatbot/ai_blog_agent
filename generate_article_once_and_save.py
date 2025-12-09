import json
import os
import re
from pathlib import Path
from textwrap import dedent

from crewai import Crew, Task, Process
from agents.seo_optimiser import seo_optimiser

# ✅ INTERNAL LINKS – update URLs/titles to your real posts
INTERNAL_LINKS = [
    {
        "title": "Salesforce Health Cloud Explained Simply",
        "url": "https://thetechnologyfiction.com/blog/salesforce-health-cloud-explained-simply/",
        "anchor": "Salesforce Health Cloud explained simply"
    },
    {
        "title": "Beginner’s Guide to Salesforce Flow",
        "url": "https://thetechnologyfiction.com/blog/salesforce-flow-beginners-guide/",
        "anchor": "Salesforce Flow beginner’s guide"
    },
    {
        "title": "Salesforce OmniStudio (Vlocity) Explained With Use Cases",
        "url": "https://thetechnologyfiction.com/blog/salesforce-omnistudio-use-cases/",
        "anchor": "Salesforce OmniStudio explained with use cases"
    }
]

# ✅ EDIT THESE TWO VALUES FOR EACH NEW ARTICLE
TOPIC = "Salesforce Agentforce Use Cases"
MAIN_KEYWORD = "Salesforce Agentforce"


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def _extract_article_from_result(result) -> dict:
    """
    Try to extract a JSON object with title, slug, meta_description, content_html
    from the Crew result. Handles both dict and string outputs.
    """
    if isinstance(result, dict):
        # Already-structured result
        if all(k in result for k in ["title", "slug", "meta_description", "content_html"]):
            return result

    # Otherwise, treat as string and try to parse JSON block
    text = str(result)

    # Find first { and last } and attempt to load as JSON
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Could not find JSON block in SEO agent output.")

    json_str = text[start : end + 1]

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from SEO output: {e}\nRaw JSON string: {json_str[:500]}")

    # Basic safety defaults
    title = data.get("title") or TOPIC
    slug = data.get("slug") or _slugify(MAIN_KEYWORD)
    meta_description = data.get("meta_description") or f"Learn about {TOPIC}."
    content_html = data.get("content_html") or ""

    return {
        "title": title,
        "slug": slug,
        "meta_description": meta_description,
        "content_html": content_html,
    }


def generate_and_save_article(topic: str, main_keyword: str) -> Path:
    """
    Use the SEO agent once to generate an article and save it as JSON file.
    Returns the path to the saved file.
    """
    print("🚀 Starting single-run article generation (SEO agent only)...")

    description = dedent(f"""
        Write a full SEO-optimized blog article in clean HTML.

        TOPIC: {topic}
        MAIN KEYWORD:
        - '{main_keyword}' must appear in the title, introduction paragraph,
          and at least one <h2> header.

        HTML STRUCTURE RULES:
        - Start with a single <h1> at the top.
        - Use <h2> for major sections and <h3> for subsections.
        - Use <p>, <ul>, <ol>, and <strong> tags where appropriate.
        - Include a properly formatted FAQ section with 4–6 Q&A items at the end.

        BRAND & CONTACT RULES:
        - If the article references contacting the company, always use the email: thetechfilabs@gmail.com
        - Never invent any consulting company, email domain, or third-party contact details.
        - Use the brand name "The Technology Fiction" or "TechFi Labs" when needed.

        INTERNAL LINKING (VERY IMPORTANT):
        - You MUST include 2–3 contextual internal links to the following articles:

          {INTERNAL_LINKS}

        - Insert these links naturally inside the article body.
        - Format them using clickable <a href="URL" target="_blank" rel="noopener noreferrer">anchor text</a>.
        - Do NOT include external links (like Salesforce docs) for now.

        OUTPUT FORMAT (STRICT):
        After writing the full HTML article, output ONLY a final JSON block with this structure:

        {{
          "title": "<title>",
          "slug": "<seo-friendly-slug>",
          "meta_description": "<155-character SEO description>",
          "content_html": "<FULL HTML CONTENT AS A SINGLE STRING>"
        }}

        VERY IMPORTANT:
        - Outside the JSON, do NOT include explanations, notes, comments, markdown, or chat text.
        - The JSON block must be valid and parsable as JSON.
        - content_html must contain the complete HTML article, including internal links.
    """)

    write_task = Task(
        description=description,
        agent=seo_optimiser,
        expected_output="A strict JSON object with title, slug, meta_description, content_html."
    )

    crew = Crew(
        agents=[seo_optimiser],
        tasks=[write_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff(inputs={"topic": topic, "main_keyword": main_keyword})

    print("\n🧩 Raw SEO agent result obtained. Parsing JSON...\n")

    article = _extract_article_from_result(result)

    # Ensure folder exists
    output_dir = Path("data/generated_posts")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Use slug for filename
    safe_slug = _slugify(article["slug"])
    output_path = output_dir / f"{safe_slug}.json"

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, indent=2)

    print(f"✅ Article saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_and_save_article(TOPIC, MAIN_KEYWORD)
