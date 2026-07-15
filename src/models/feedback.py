from pydantic import BaseModel
from enum import Enum

class FeedbackType(str, Enum):
    like = "like"
    dislike = "dislike"
    skip = "skip"

class Feedback(BaseModel):
    user_id: str
    movie_id: int
    feedback: FeedbackType