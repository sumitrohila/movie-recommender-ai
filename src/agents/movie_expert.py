from crewai import Agent
from langchain.tools import Tool
from src.tools.movie_db import MovieDBTool
from src.config.llm_config import get_llm

def create_movie_expert() -> Agent:
    """CrewAI agent specialised in movie knowledge."""
    return Agent(
        role="Movie Expert",
        goal="Provide detailed movie information and recommendations based on user queries.",
        backstory="You are a seasoned film critic with deep knowledge of cinema across genres and eras.",
        tools=[Tool(name="movie_db", func=MovieDBTool()._run, description="Query movie details")],
        llm=get_llm(temperature=0.3),
        verbose=True,
        allow_delegation=False,
    )