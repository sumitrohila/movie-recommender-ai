from crewai import Agent
from src.config.llm_config import get_llm

def create_user_analyst() -> Agent:
    return Agent(
        role="User Analyst",
        goal="Analyze user preferences from their history and profile to tailor recommendations.",
        backstory="You are a data scientist specialising in user behaviour and taste prediction.",
        tools=[],  # Could include a tool to fetch user history
        llm=get_llm(temperature=0.2),
        verbose=True,
        allow_delegation=False,
    )