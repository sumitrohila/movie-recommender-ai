from langchain.tools import BaseTool
from typing import Optional, List
from src.models.movie import Movie

# Mock database (in reality, use SQLAlchemy or TMDB API)
_MOCK_MOVIES = {
    1: Movie(id=1, title="The Matrix", genres=["Sci-Fi", "Action"], release_year=1999, rating=8.7),
    2: Movie(id=2, title="Inception", genres=["Sci-Fi", "Thriller"], release_year=2010, rating=8.8),
    3: Movie(id=3, title="The Godfather", genres=["Drama", "Crime"], release_year=1972, rating=9.2),
    4: Movie(id=4, title="Interstellar", genres=["Sci-Fi", "Adventure"], release_year=2014, rating=8.6),
    5: Movie(id=5, title="The Dark Knight", genres=["Action", "Crime", "Drama"], release_year=2008, rating=9.0),
}

class MovieDBTool(BaseTool):
    name: str = "movie_db"
    description: str = "Retrieve movie details by ID or search by genre."

    def _run(self, query: str) -> str:
        # Simple mock: if query is numeric, treat as ID; else search by genre
        if query.isdigit():
            movie = _MOCK_MOVIES.get(int(query))
            return str(movie) if movie else "Movie not found"
        else:
            # search by genre (case-insensitive)
            results = [m for m in _MOCK_MOVIES.values() if any(query.lower() in g.lower() for g in m.genres)]
            return str(results) if results else "No movies found for that genre."

    async def _arun(self, query: str) -> str:
        return self._run(query)