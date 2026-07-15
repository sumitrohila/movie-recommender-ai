from crewai import Crew, Task
from src.agents.movie_expert import create_movie_expert
from src.agents.user_analyst import create_user_analyst
from src.agents.critic import create_critic

def create_crew():
    movie_expert = create_movie_expert()
    user_analyst = create_user_analyst()
    critic = create_critic()
    
    task1 = Task(
        description="Analyze the user's preferences from the input: {user_input}",
        agent=user_analyst,
        expected_output="A structured summary of user tastes."
    )
    task2 = Task(
        description="Based on the user's preferences, suggest 3 movie titles with reasoning.",
        agent=movie_expert,
        expected_output="List of 3 movie suggestions with explanations.",
        context=[task1]
    )
    task3 = Task(
        description="Evaluate the suggested movies for relevance and quality. Provide final top 2.",
        agent=critic,
        expected_output="Final 2 movie recommendations with critique.",
        context=[task2]
    )
    
    crew = Crew(
        agents=[user_analyst, movie_expert, critic],
        tasks=[task1, task2, task3],
        verbose=True,
    )
    return crew