from crewai import Agent
from llm_factory import get_default_llm

planner_llm = get_default_llm()

content_planner = Agent(
    role="Content Planner",
    goal="Choose trending Salesforce topics and generate detailed blog outlines.",
    backstory=(
        "You analyze Salesforce ecosystem trends, web searches, and FAQs to propose "
        "high-quality blog topics and outlines."
    ),
    verbose=True,
    allow_delegation=True,
    llm=planner_llm
)
