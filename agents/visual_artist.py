from crewai import Agent

visual_artist = Agent(
    role="Visual Artist",
    goal="Generate clean, professional images that enhance Salesforce blogs.",
    backstory="You create minimalistic illustrations and diagrams.",
    verbose=True,
    llm="gpt-4.1-mini"
)
