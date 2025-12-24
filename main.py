from crewai import Crew, Task, Process

from agents.content_planner import content_planner
from agents.seo_optimiser import seo_optimiser
from agents.visual_artist import visual_artist

from tools.search_tools import web_search
from tools.cms_tools import post_to_wordpress_raw

from datetime import datetime
from agents.topic_scout import topic_scout
import json
from textwrap import dedent

import time
import threading

from llm_metrics import metrics

from utils.sanitize_article_payload import sanitize_article_payload
from tools.image_tools import generate_diagram_image_b64
from tools.cms_tools import upload_image_base64_to_wordpress
import re

from datetime import datetime

CURRENT_YEAR = datetime.now().year


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
    },
    {
        "title": "Salesforce Data Loader: A Comprehensive Guide",
        "url": "https://thetechnologyfiction.com/blog/salesforce-data-loader-a-comprehensive-guide/",
        "anchor": "Salesforce Data Loader"
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

        Use web_search to quickly scan ONLY:
        - Latest Salesforce release notes ({CURRENT_YEAR})
        - Salesforce official blogs and announcements
        - Recent (last 6 months) interview-focused Salesforce articles


        FRESHNESS & DATE RULES (CRITICAL):
        - Today's year is {CURRENT_YEAR}.
        - If you search Salesforce releases, ALWAYS target the latest available release for {CURRENT_YEAR} or {CURRENT_YEAR + 1}.
        - NEVER intentionally search or select topics from:
        - "Spring 24"
        - "2024 Salesforce release"
        - Any outdated release
        - If older content appears in search results, IGNORE it unless explicitly asked.


        CONTENT STRATEGY (VERY IMPORTANT):

        This blog focuses heavily on INTERVIEW-DRIVEN and JOB-ORIENTED Salesforce topics.

        You MUST select topics primarily from these pillars:
        - Apex & Triggers (interview-focused)
        - Async Apex (Batch, Queueable, Future)
        - Salesforce Flows (all types & async paths)
        - Admin security & architecture
        - API integrations & patterns
        - CI/CD tools (Gearset, Copado, Azure DevOps)
        - Data migration (DBAmp)
        - Platform Events
        - Apex frameworks & error logging
        - Lightning Web Components best practices
        - Salesforce interview questions (Admin & Developer)
        - Salesforce Agentforce questions and Data Cloud (Admin & Developer)

        Prefer topics that:
        - Are frequently asked in MNC interviews
        - Help candidates crack Salesforce interviews
        - Are commonly used in real production projects

        
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
    metrics.register_call(label="Topic Scout")
    result = crew.kickoff()

    # Parse JSON from result

    text = str(result)

    # 1️⃣ Try to extract JSON from a ```json ... ``` fenced block
    json_str = None
    fence_match = re.search(r"```json\s*(\{.*?})\s*```", text, re.DOTALL)
    if fence_match:
        json_str = fence_match.group(1)
    else:
        # 2️⃣ Fallback: scan for any dict that contains "topic"
        best_data = None
        idx = 0
        while True:
            start = text.find("{", idx)
            if start == -1:
                break
            end = text.find("}", start)
            if end == -1:
                break

            candidate_str = text[start : end + 1]
            try:
                candidate = json.loads(candidate_str)
            except Exception:
                idx = start + 1
                continue

            if isinstance(candidate, dict) and "topic" in candidate:
                best_data = candidate
                break

            idx = start + 1

        if best_data is None:
            print("\n⚠️ Topic Scout did not return JSON with a 'topic' key.")
            print("Raw result (truncated):\n", text[:800])
            fallback_topic = "Salesforce Flow Best Practices in 2025"
            fallback_keyword = "Salesforce Flow best practices"
            print(f"➡️ Falling back to topic: {fallback_topic}")
            return fallback_topic, fallback_keyword

        data = best_data
    # If we got JSON from the fenced block, parse it
    if json_str is not None:
        try:
            data = json.loads(json_str)
        except Exception as e:
            print("\n⚠️ Failed to parse Topic Scout JSON from fenced block.")
            print("Error:", e)
            print("JSON-ish string (truncated):\n", json_str[:800])
            fallback_topic = "Salesforce Flow Best Practices in 2025"
            fallback_keyword = "Salesforce Flow best practices"
            print(f"➡️ Falling back to topic: {fallback_topic}")
            return fallback_topic, fallback_keyword

    topic = data.get("topic")
    main_keyword = data.get("main_keyword")

    if not topic:
        print("\n⚠️ Topic missing in JSON. Falling back to default topic.")
        topic = "Salesforce Flow Best Practices in 2025"
    if not main_keyword:
        main_keyword = topic

    print(f"✅ Chosen topic: {topic}")
    print(f"✅ Main keyword: {main_keyword}")
    print(f"📝 Reason: {data.get('reason')}")
    print(f"🎯 Mode: {data.get('content_mode')} | Audience: {data.get('target_audience')}")

    return topic, main_keyword



def inject_images_into_content(content_html: str) -> str:
    """
    Finds IMAGE placeholders, generates diagrams via OpenAI,
    uploads to WordPress, replaces placeholders with <img>.
    """
    pattern = r"<!-- IMAGE:\s*(.*?)\s*-->"
    matches = re.findall(pattern, content_html)

    if not matches:
        print("🖼 No IMAGE placeholders found. Skipping image generation.")
        return content_html

    for idx, description in enumerate(matches, start=1):
        print(f"🖼 Generating diagram {idx}/{len(matches)}: {description}")

        prompt = (
            f"Create a clean technical DIAGRAM / FLOWCHART / INFOGRAPHIC for Salesforce explaining: {description}. "
            "Use boxes, arrows, labels, and clear structure. White background. Flat 2D. No people. No logos/branding."
        )

        b64_img = generate_diagram_image_b64(prompt)

        media = upload_image_base64_to_wordpress(
            image_base64=b64_img,
            filename=f"diagram-{idx}.png"
        )

        img_url = media.get("source_url")
        if not img_url:
            print("⚠️ Media upload succeeded but source_url missing. Skipping replacement for this image.")
            continue

        img_tag = f"""
        <figure class="wp-block-image">
        <img src="{img_url}" alt="{description}">
        <figcaption>{description}</figcaption>
        </figure>
        """

        # Replace exactly one occurrence (first match)
        content_html = re.sub(rf"<!-- IMAGE:\s*{re.escape(description)}\s*-->", img_tag, content_html, count=1)

    return content_html




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
        - In content_html, use \\n for new lines (so JSON stays valid).

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

        IN-CONTENT IMAGES (VERY IMPORTANT):
        - Insert 2–4 image placeholders inside the content_html at relevant sections.
        - Use this exact format on its own line:
        <!-- IMAGE: <what diagram/infographic should show> -->
        - These must be DIAGRAMS / FLOWCHARTS / INFOGRAPHICS (not photos).
        - Place them near the most “visual” sections (comparison tables, architecture, step-by-step flows).
        
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
        - The JSON block must be valid and parsable as JSON and ensure the JSON is valid (escape quotes properly).
        - content_html must contain the complete HTML article, including internal links.


    """),
    agent=seo_optimiser,
    expected_output=(
        "A full HTML article PLUS a strict JSON block containing "
        "title, slug, meta_description, content_html."
    ),
)

    # 3) IMAGE PROMPT 
    image_task = Task(
        description=dedent("""
            You will receive the previous step output as JSON containing:
            - title
            - slug
            - meta_description
            - content_html

            TASK:
            1) Parse that JSON.
            2) Read ONLY the content_html field.
            3) Extract every placeholder that matches:
            <!-- IMAGE: description -->

            For EACH placeholder, generate ONE prompt for a technical diagram/infographic:
            - Must be a FLOW DIAGRAM, ARCHITECTURE DIAGRAM, PROCESS DIAGRAM, or COMPARISON INFOGRAPHIC
            - Use labels, arrows, boxes, numbering where relevant
            - No people, no artistic style, no logos/branding

            OUTPUT JSON ONLY:
            {
            "images": [
                { "description": "...", "prompt": "..." }
            ]
            }

            If there are no placeholders, return:
            { "images": [] }
        """),
        agent=visual_artist,
        context=[write_task],
        expected_output="JSON with diagram prompts for each image placeholder."
        )



    # 4) PUBLISH: send to WordPress as draft
    '''    publish_task = Task(
        description=(
            "Take the final JSON (title, slug, meta_description, content_html) from your article, "
            "and call the WordPress tool to create a draft post. Use meta_description as excerpt. "
            "Return the WordPress API response."
        ),
        agent=seo_optimiser,
        tools=[post_to_wordpress],
        expected_output="The WordPress API response with the created post's ID and link."
    )
    '''
    crew = Crew(
        agents=[content_planner, seo_optimiser, visual_artist],
        #tasks=[plan_task, write_task, image_task, publish_task],
        tasks=[plan_task, write_task, image_task],
        process=Process.sequential,
        verbose=True,
    )


    wait_for_rate_limit()
    metrics.register_call(label=f"Blog pipeline for topic '{topic}'")
    result = crew.kickoff(inputs={"topic": topic, "main_keyword": main_keyword})

    print("\n🎉 DONE! Final pipeline output:\n")
    print(result)

        # -------------------------------
    # 🔎 EXTRACT FINAL ARTICLE JSON (from writer, not final crew result)
    # -------------------------------
    writer_output = getattr(write_task.output, "raw", write_task.output)
    print("\n🧪 DEBUG: write_task.output =\n", writer_output)

    if writer_output is None:
        print("\n⚠️ write_task.output is None. Skipping WordPress posting.")
        return result

    # If CrewAI already gives us a dict, use it directly
    if isinstance(writer_output, dict):
        raw_article = writer_output
    else:
        # Otherwise, parse JSON from the text
        text = str(writer_output)
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            print("\n⚠️ Could not find article JSON in write_task.output. Skipping WordPress posting.")
            print("Raw writer_output (truncated):\n", text[:500])
            return result

        json_str = text[start:end+1]
        try:
            raw_article = json.loads(json_str)
        except Exception as e:
            print("\n⚠️ Failed to parse article JSON from write_task.output. Skipping WordPress posting.")
            print("Error:", e)
            print("JSON string (truncated):\n", json_str[:500])
            return result

    # ----------------------------------------
    # 🔥 SANITIZE THE ARTICLE (MANDATORY FIELDS)
    # ----------------------------------------
    article = sanitize_article_payload(raw_article)

    title = article["title"]
    slug = article["slug"]
    excerpt = article.get("meta_description") or "Salesforce article generated by AI automation."
    content_html = inject_images_into_content(article["content_html"])

    print("\n📝 Prepared article for WordPress:")
    print(f"  Title: {title}")
    print(f"  Slug: {slug}")
    print(f"  Excerpt: {excerpt[:120]}...")

    # 📨 Post to WordPress as draft (Python, not LLM)
    try:
        wp_res = post_to_wordpress_raw(
            title=title,
            content=content_html,
            slug=slug,
            excerpt=excerpt
        )
        print("\n✅ Posted to WordPress as draft:")
        print(f"  id={wp_res.get('id')}")
        print(f"  status={wp_res.get('status')}")
        print(f"  link={wp_res.get('link')}")
    except Exception as e:
        print("\n❌ Failed to post to WordPress.")
        print("Error:", e)

    return result




if __name__ == "__main__":
    # 1) Let Topic Scout choose the best topic for today
    topic, main_keyword = pick_salesforce_topic_for_today()

    # 2) Run your existing blog pipeline with that topic
    run_blog_pipeline(
        topic=topic,
        main_keyword=main_keyword
    )

    from llm_metrics import metrics
    print("========== LLM METRICS ==========")
    print(metrics.summary())

