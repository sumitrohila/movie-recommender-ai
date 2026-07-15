from crewai import Agent
from src.config.llm_config import get_llm

def create_critic() -> Agent:
    return Agent(
        role="Critic",
        goal="Evaluate the quality and relevance of movie recommendations before final output.",
        backstory="You are a tough but fair movie critic who ensures only the best suggestions reach the user.",
        tools=[],  # Could use rating tool
        llm=get_llm(temperature=0.4),
        verbose=True,
        allow_delegation=False,
    )