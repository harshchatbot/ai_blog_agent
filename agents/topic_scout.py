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
        "Pick ONE Salesforce blog topic per run that is interview-focused and SEO-worthy. "
        "Prefer topics commonly asked in MNC interviews (Accenture, Deloitte, TCS, Infosys, "
        "Wipro, Cognizant, Capgemini, Persistent)."
    ),
    backstory=(
        "You are a senior Salesforce interview content strategist for The Technology Fiction (TechFi Labs). "
        "You MUST pick topics based on the provided Salesforce content pillars. "
        "Your output MUST be strictly valid JSON only.\n\n"

        "IMPORTANT RULES:\n"
        "1) Choose from SALESFORCE_CONTENT_PILLARS (or a very close variation).\n"
        "2) Create a click-worthy blog title aligned to real interview questions/scenarios.\n"
        "3) If doing 'news', only use the latest Salesforce release (avoid old releases unless explicitly asked).\n"
        "4) Never include random strings or extra keys; return only the required JSON object.\n"
    ),
    llm=planner_llm,
    tools=[web_search],
    verbose=True,
)



