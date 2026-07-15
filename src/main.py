from fastapi import FastAPI
from src.api.routes import recommendations, health
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Movie Recommender AI Agent")

# ... existing routers ...

# Serve frontend (optional)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

app = FastAPI(title="Movie Recommender AI Agent")

app.include_router(recommendations.router, prefix="/api/v1", tags=["recommendations"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])

@app.get("/")
async def root():
    return {"message": "Movie Recommender Agent API"}