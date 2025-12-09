from crewai import Crew, Task, Process

from agents.content_planner import content_planner
from agents.seo_optimiser import seo_optimiser
from agents.visual_artist import visual_artist

from tools.search_tools import web_search
from tools.cms_tools import post_to_wordpress

def run_blog_agent(topic: str, main_keyword: str):
    crew = Crew(
        agents=[content_planner, seo_optimiser, visual_artist],
        process=Process.sequential,
        verbose=True
    )

    tasks = [
        Task(
            description=f"Research and create outline for: {topic}",
            agent=content_planner,
            tools=[web_search]
        ),
        Task(
            description=f"Write and SEO optimise full article for: {main_keyword}. Return title, slug, meta_description, content_html.",
            agent=seo_optimiser
        ),
        Task(
            description=f"Create 1 featured image prompt for: {topic}",
            agent=visual_artist
        ),
        Task(
            description="Publish article to WordPress.",
            agent=seo_optimiser,
            tools=[post_to_wordpress]
        )
    ]

    result = crew.kickoff(inputs={"topic": topic, "main_keyword": main_keyword})
    return result


if __name__ == "__main__":
    output = run_blog_agent(
        topic="Salesforce Flow vs Apex in 2025",
        main_keyword="Salesforce Flow vs Apex"
    )
    print("\n\nFINAL OUTPUT:\n", output)
