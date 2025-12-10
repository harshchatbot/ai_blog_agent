from crewai import Agent
from llm_factory import get_default_llm

planner_llm = get_default_llm()

visual_artist = Agent(
    role="Visual Artist",
    goal="Generate clean, professional images that enhance Salesforce blogs.",
    backstory="You create minimalistic illustrations and diagrams.",
    verbose=True,
    #llm="gpt-4.1-mini"
    llm=planner_llm
)
