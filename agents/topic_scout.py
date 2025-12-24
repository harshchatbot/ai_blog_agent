# agents/topic_scout.py

from crewai import Agent
from tools.search_tools import web_search  # assuming you already created this tool
from llm_factory import get_default_llm

planner_llm = get_default_llm()

SALESFORCE_CONTENT_PILLARS = [
    "Apex Triggers interview questions and best practices",
    "Async Apex (Batch, Queueable, Future) with real-world use cases",
    "Salesforce Flows (Record-triggered, Scheduled, Auto-launched, Async)",
    "Salesforce Admin security (Profiles, Permission Sets, Sharing Rules)",
    "Salesforce data modeling and architecture",
    "Salesforce API integrations (REST, SOAP, Bulk, Streaming)",
    "Named Credentials, Connected Apps, Remote Site Settings",
    "Salesforce integration patterns (fire-and-forget, request-reply)",
    "CI/CD in Salesforce using Gearset, Copado, Azure DevOps",
    "Salesforce data migration using DBAmp",
    "Platform Events and event-driven architecture",
    "Apex enterprise frameworks (Kevin O’Hara style)",
    "Apex error handling and logging best practices",
    "Lightning Web Components use cases and best practices",
    "Salesforce interview questions for Admin & Developer roles"
]


topic_scout = Agent(
    role="Salesforce Topic Scout",
    goal=(
        "Continuously discover high-impact, SEO-worthy blog topics "
        "about Salesforce, including latest releases and evergreen fundamentals."
    ),
    backstory=(
        "You are a senior Salesforce content strategist working for "
        "The Technology Fiction (TechFi Labs). You understand Salesforce core "
        "products (Sales Cloud, Service Cloud, Experience Cloud, Health Cloud), "
        "platform features (Apex, LWC, Flows, SOQL), and new innovations "
        "(Agentforce, Data Cloud, Einstein, Hyperforce, OmniStudio). "
        "You balance trending/news topics with evergreen educational content."
    ),
    llm=planner_llm,
    tools=[web_search],
    verbose=True,
)
