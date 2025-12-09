from crewai import Agent

seo_optimiser = Agent(
    role="SEO Optimiser",
    goal="Turn raw content into SEO-optimized, structured blog posts with keywords, meta descriptions, and slugs.",
    backstory="You are an SEO expert specializing in Salesforce content.",
    verbose=True,
    llm="gpt-4.1-mini"
)
