from pydantic import BaseModel
from typing import Optional, List

class RecommendRequest(BaseModel):
    user_input: str
    preferences: Optional[dict] = None
    mode: Optional[str] = "crew"  # chain, graph, crew