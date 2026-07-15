from pydantic import BaseModel
from typing import Any

class RecommendResponse(BaseModel):
    recommendations: Any
    mode: str