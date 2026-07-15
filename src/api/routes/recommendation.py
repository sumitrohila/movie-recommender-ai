from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas.request import RecommendRequest
from src.api.schemas.response import RecommendResponse
from src.core.runner import RecommendationRunner
from functools import lru_cache

router = APIRouter()

@lru_cache(maxsize=1)
def get_runner():
    return RecommendationRunner(mode="crew")  # default mode

@router.post("/recommend", response_model=RecommendResponse)
async def recommend(
    req: RecommendRequest,
    runner: RecommendationRunner = Depends(get_runner)
):
    try:
        result = await runner.recommend(req.user_input, req.preferences)
        return RecommendResponse(recommendations=result["recommendations"], mode=req.mode or "crew")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))