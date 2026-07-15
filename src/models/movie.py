from pydantic import BaseModel, Field
from typing import List, Optional

class Movie(BaseModel):
    id: int
    title: str
    overview: Optional[str] = None
    genres: List[str] = Field(default_factory=list)
    release_year: Optional[int] = None
    rating: Optional[float] = None  # average user rating