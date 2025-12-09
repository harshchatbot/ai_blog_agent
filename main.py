from crewai import Crew, Task, Process

from agents.content_planner import content_planner
from agents.seo_optimiser import seo_optimiser
from agents.visual_artist import visual_artist

from tools.search_tools import web_search
from tools.cms_tools import post_to_wordpress


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
        description=(
            "Using the outline, write a full SEO-optimized blog article in HTML.\n"
            "Requirements:\n"
            "- Include <h1> title at top.\n"
            "- Use <h2> and <h3> for sections and sub-sections.\n"
            f"- Main keyword: '{main_keyword}' (use it in title, intro, and at least one H2).\n"
            "- Add bullet points and numbered lists where helpful.\n"
            "- Add an FAQ section at the end with 4–6 Q&A.\n"
            "- At the very end of your response, output a JSON block ONLY with:\n"
            "  {\"title\": \"...\", \"slug\": \"...\", \"meta_description\": \"...\", \"content_html\": \"...\"}\n"
            "  where content_html is the full HTML body as a single string.\n"
        ),
        agent=seo_optimiser,
        expected_output=(
            "A full HTML article plus a final JSON object with keys: "
            "title, slug, meta_description, content_html."
        )
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
