from crewai import Crew, Task, Process

from agents.content_planner import content_planner
from agents.seo_optimiser import seo_optimiser
from agents.visual_artist import visual_artist

from tools.search_tools import web_search
from tools.cms_tools import post_to_wordpress

INTERNAL_LINKS = [
    {
        "title": "Apex Batch Class: The Ultimate Guide for Salesforce Developers (2025 Edition)",
        "url": "https://thetechnologyfiction.com/blog/apex-batch-class-the-ultimate-guide-for-salesforce-developers-2025-edition/",
        "anchor": "Salesforce Apex Batch Class beginner’s guide"
    },
    {
        "title": "Salesforce Vlocity (OmniStudio) Explained Simply With Use Cases",
        "url": "https://thetechnologyfiction.com/blog/salesforce-vlocity-omnistudio-explained-simply-with-use-cases/",
        "anchor": "Salesforce Omnistudio use cases"
    },
    {
        "title": "Linear Search and Sorting Algorithm in Salesforce Using Apex | 2025",
        "url": "https://thetechnologyfiction.com/blog/linear-search-and-sorting-algorithm-in-salesforce-using-apex-2025/",
        "anchor": "Algorithm in Salesforce"
    }
    # add more as you create new posts
]



def run_blog_pipeline(topic: str, main_keyword: str):
    print("🚀 Starting AI Blog Agent...\n")

    # 1) PLAN: research + outline
    plan_task = Task(
        description=(
            f"Research and prepare a detailed blog outline for: '{topic}'. "
            f"Use web search and propose H2/H3 structure, plus key points to cover."
        ),
        agent=content_planner,
        tools=[web_search],
        expected_output="A clear outline with H2/H3 headings and bullet points."
    )

    # 2) WRITE: full SEO article
    write_task = Task(
    description=dedent(f"""
        Using the outline from the planner, write a full SEO-optimized blog article in clean HTML.

        MAIN KEYWORD:
        - '{main_keyword}' must appear in the title, introduction paragraph, and at least one <h2> header.

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
        - Do NOT include external links (like Salesforce docs) unless absolutely necessary.

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
    """),
    agent=seo_optimiser,
    expected_output=(
        "A full HTML article PLUS a strict JSON block containing "
        "title, slug, meta_description, content_html."
    ),
)

    # 3) IMAGE PROMPT (we'll use later)
    image_task = Task(
        description=(
            f"Create one short prompt for generating a featured image for this topic: '{topic}'. "
            "Return just 1–2 sentences describing a clean, minimal tech illustration."
        ),
        agent=visual_artist,
        expected_output="One short image prompt sentence."
    )

    # 4) PUBLISH: send to WordPress as draft
    publish_task = Task(
        description=(
            "Take the final JSON (title, slug, meta_description, content_html) from your article, "
            "and call the WordPress tool to create a draft post. Use meta_description as excerpt. "
            "Return the WordPress API response."
        ),
        agent=seo_optimiser,
        tools=[post_to_wordpress],
        expected_output="The WordPress API response with the created post's ID and link."
    )

    crew = Crew(
        agents=[content_planner, seo_optimiser, visual_artist],
        tasks=[plan_task, write_task, image_task, publish_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff(inputs={"topic": topic, "main_keyword": main_keyword})

    print("\n🎉 DONE! Final pipeline output:\n")
    print(result)

    return result


if __name__ == "__main__":
    run_blog_pipeline(
        topic="Salesforce Flow vs Process Builder in 2025",
        main_keyword="Salesforce Flow vs Process Builder"
    )
