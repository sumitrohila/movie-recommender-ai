from pydantic import BaseModel
from typing import List, Optional

class UserPreferences(BaseModel):
    liked_genres: List[str] = []
    disliked_genres: List[str] = []
    favorite_movies: List[int] = []
    watched_movies: List[int] = []