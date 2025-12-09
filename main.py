from crewai import Crew, Task, Process

from agents.content_planner import content_planner
from agents.seo_optimiser import seo_optimiser
from agents.visual_artist import visual_artist

from tools.search_tools import web_search
from tools.cms_tools import post_to_wordpress

from datetime import datetime
from agents.topic_scout import topic_scout
import json
from textwrap import dedent

import time
import threading


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




# OpenAI allows 3 requests per minute on your plan
MAX_REQUESTS_PER_MIN = 3
REQUEST_WINDOW = 60  # seconds

request_count = 0
window_start_time = time.time()
lock = threading.Lock()

def wait_for_rate_limit():
    global request_count, window_start_time

    with lock:
        current_time = time.time()
        elapsed = current_time - window_start_time

        # If 60 sec window passed → reset counter
        if elapsed >= REQUEST_WINDOW:
            window_start_time = current_time
            request_count = 0

        # If limit reached → wait until new window
        if request_count >= MAX_REQUESTS_PER_MIN:
            sleep_time = REQUEST_WINDOW - elapsed
            print(f"⏳ Rate limit: sleeping {sleep_time:.1f}s to avoid 429...")
            time.sleep(sleep_time)
            window_start_time = time.time()
            request_count = 0

        request_count += 1



def get_content_mode_for_today() -> str:
    """
    Decide whether today's post should be NEWS (releases/updates)
    or EVERGREEN (fundamentals, how-tos) based on weekday.
    
    0 = Monday, 1 = Tuesday, 2 = Wednesday, 3 = Thursday, ...
    """
    weekday = datetime.now().weekday()
    if weekday == 1:  # Tuesday
        return "news"
    if weekday == 3:  # Thursday
        return "evergreen"
    # default if you run on another day
    return "news"



def pick_salesforce_topic_for_today() -> tuple[str, str]:
    """
    Uses the Topic Scout agent + web search to select a Salesforce blog topic
    and main keyword for today. Returns (topic, main_keyword).
    """
    mode = get_content_mode_for_today()
    print(f"🧠 Topic mode for today: {mode.upper()}")

    # Explanation text for the agent
    mode_instructions = {
        "news": (
            "Focus on the latest Salesforce releases, features, and updates. "
            "Examples: Salesforce Agentforce, Einstein Copilot, Data Cloud updates, "
            "new Flow features, release highlights from the latest Salesforce Release (e.g. Spring/Summer/Winter). "
            "Pick something that would be relevant in the next 2–4 weeks and likely to be highly searched."
        ),
        "evergreen": (
            "Focus on beginner to intermediate educational topics that stay relevant over time. "
            "Examples: Apex class basics with examples, Lightning Web Components for beginners, "
            "Flow best practices, difference between Workflow/Process Builder/Flow, "
            "Salesforce clouds overview (Sales Cloud vs Service Cloud vs Experience Cloud), "
            "Health Cloud basics, OmniStudio use cases."
        )
    }

    description = dedent(f"""
        You are selecting ONE best blog topic for a Salesforce-specific blog called
        'The Technology Fiction'. The audience is:
        - Salesforce admins, developers, consultants
        - Freshers and career switchers
        - People preparing for Salesforce interviews

        CONTENT MODE TODAY: "{mode}".

        {mode_instructions[mode]}

        REQUIREMENTS:
        - The topic MUST be 100% Salesforce-related.
        - It should be specific enough to write a 1500–2500 word blog.
        - Prefer topics where:
          - There is clear search intent (how-to, comparison, use cases, explanation), AND
          - We can include practical sections: examples, use cases, screenshots (in future), FAQs.

        Use web_search to quickly scan:
        - Salesforce official docs / release notes
        - Salesforce+ / blog / developer.salesforce.com
        - Top-ranking blogs in the Salesforce ecosystem

        OUTPUT FORMAT (STRICT):
        Return ONLY a JSON object, no extra text, in this structure:

        {{
          "topic": "<final blog post title idea>",
          "main_keyword": "<main SEO keyword phrase>",
          "content_mode": "{mode}",
          "target_audience": "<short description of who this post is for>",
          "reason": "<1-2 sentence reason why this topic is valuable now>",
          "outline_seed": [
            "<H2 idea 1>",
            "<H2 idea 2>",
            "<H2 idea 3>",
            "<H2 idea 4>"
          ]
        }}

        - "topic" should already look like a strong blog title (you may refine it slightly for clicks, but stay professional).
        - "main_keyword" should be a realistic keyword someone would type into Google.
        - "outline_seed" is just rough section ideas; the planner + writer will flesh them out.
    """)

    topic_task = Task(
        description=description,
        agent=topic_scout,
        expected_output="A single JSON object with topic, main_keyword, content_mode, target_audience, reason, outline_seed."
    )

    crew = Crew(
        agents=[topic_scout],
        tasks=[topic_task],
        process=Process.sequential,
        verbose=True,
    )

    wait_for_rate_limit()
    result = crew.kickoff()

    # Parse JSON from result
    text = str(result)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Topic Scout did not return a valid JSON object.")

    json_str = text[start: end + 1]
    data = json.loads(json_str)

    topic = data.get("topic")
    main_keyword = data.get("main_keyword") or topic

    print(f"✅ Chosen topic: {topic}")
    print(f"✅ Main keyword: {main_keyword}")
    print(f"📝 Reason: {data.get('reason')}")
    print(f"🎯 Mode: {data.get('content_mode')} | Audience: {data.get('target_audience')}")

    return topic, main_keyword




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

    wait_for_rate_limit()
    result = crew.kickoff(inputs={"topic": topic, "main_keyword": main_keyword})

    print("\n🎉 DONE! Final pipeline output:\n")
    print(result)

    return result


if __name__ == "__main__":
    # 1) Let Topic Scout choose the best topic for today
    topic, main_keyword = pick_salesforce_topic_for_today()

    # 2) Run your existing blog pipeline with that topic
    run_blog_pipeline(
        topic=topic,
        main_keyword=main_keyword
    )

