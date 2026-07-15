from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from src.config.llm_config import get_llm
from src.tools.movie_db import MovieDBTool

def create_recommendation_chain():
    """A simple LCEL chain that retrieves movies and generates recommendations."""
    llm = get_llm(temperature=0.5)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a movie recommendation assistant. Based on user preferences: {preferences}, suggest 3 movies from the list: {movies}."),
        ("human", "Recommend movies.")
    ])
    
    # For demonstration, we fetch movies from mock DB based on a genre.
    # In reality, we'd use a retriever.
    def get_movies(_input):
        tool = MovieDBTool()
        # If preferences contain a genre, search for it
        genre = _input.get("preferences", {}).get("liked_genres", [""])[0] if _input.get("preferences", {}).get("liked_genres") else "Sci-Fi"
        result = tool._run(genre)
        return result
    
    chain = (
        RunnablePassthrough.assign(movies=get_movies)
        | prompt
        | llm
    )
    return chain