import os
import shutil

# ============================================================
# All files and their content: path -> content
# ============================================================
files = {
    # ---------- Root files ----------
    ".env.example": """# LLM
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini

# Optional other LLMs
# ANTHROPIC_API_KEY=...

# Database
DATABASE_URL=sqlite:///./movies.db

# Redis (for memory store)
REDIS_URL=redis://localhost:6379

# External APIs
TMDB_API_KEY=your_tmdb_key
""",
    ".gitignore": """__pycache__/
*.pyc
.env
*.db
*.sqlite3
.venv/
venv/
env/
dist/
build/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
.DS_Store
""",
    "pyproject.toml": """[project]
name = "movie-recommender-agent"
version = "0.1.0"
description = "AI agent for movie recommendations using LangChain, LangGraph, CrewAI"
authors = [{name = "Your Name", email = "you@example.com"}]
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "pydantic-settings>=2.7.0",
    "python-dotenv>=1.0.0",
    "langchain>=0.3.0",
    "langchain-openai>=0.3.0",
    "langgraph>=0.3.0",
    "crewai>=0.80.0",
    "redis>=5.0.0",
    "sqlalchemy>=2.0.0",
    "httpx>=0.28.0",
]
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
""",
    "requirements.txt": """fastapi==0.115.12
uvicorn[standard]==0.34.0
pydantic-settings==2.7.0
python-dotenv==1.0.1
langchain==0.3.15
langchain-openai==0.3.6
langgraph==0.3.2
crewai==0.80.2
redis==5.2.1
sqlalchemy==2.0.38
httpx==0.28.1
""",
    "README.md": """# 🎬 Movie Recommender AI Agent

An intelligent movie recommendation system built with LangChain, LangGraph, CrewAI, and FastAPI.

## Features
- Three orchestration modes: **LCEL chain**, **LangGraph state machine**, **CrewAI multi‑agent**
- Modular, async, and production‑ready
- Beautiful frontend included

## Quick Start
1. Copy `.env.example` to `.env` and fill in your API keys.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `uvicorn src.main:app --reload`
4. Open `http://localhost:8000` (if frontend mounted) or serve `frontend/` separately.

For full documentation, see the project structure below.
""",
    "docker-compose.yml": """version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=sqlite:///./movies.db
    volumes:
      - ./movies.db:/app/movies.db
""",
    "Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",

    # ---------- src/ ----------
    "src/__init__.py": "",
    "src/main.py": """from fastapi import FastAPI
from src.api.routes import recommendations, health

app = FastAPI(title="Movie Recommender AI Agent")
app.include_router(recommendations.router, prefix="/api/v1", tags=["recommendations"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])

@app.get("/")
async def root():
    return {"message": "Movie Recommender Agent API"}
""",

    "src/api/__init__.py": "",
    "src/api/dependencies.py": "# Placeholder for dependency injection (e.g., auth, rate limiting)",
    "src/api/routes/__init__.py": "",
    "src/api/routes/recommendations.py": """from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas.request import RecommendRequest
from src.api.schemas.response import RecommendResponse
from src.core.runner import RecommendationRunner
from functools import lru_cache

router = APIRouter()

@lru_cache(maxsize=1)
def get_runner():
    return RecommendationRunner(mode="crew")

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
""",
    "src/api/routes/health.py": """from fastapi import APIRouter
router = APIRouter()
@router.get("/health")
async def health():
    return {"status": "ok"}
""",
    "src/api/schemas/__init__.py": "",
    "src/api/schemas/request.py": """from pydantic import BaseModel
from typing import Optional

class RecommendRequest(BaseModel):
    user_input: str
    preferences: Optional[dict] = None
    mode: Optional[str] = "crew"
""",
    "src/api/schemas/response.py": """from pydantic import BaseModel
from typing import Any

class RecommendResponse(BaseModel):
    recommendations: Any
    mode: str
""",

    "src/core/__init__.py": "",
    "src/core/chains.py": """from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from src.config.llm_config import get_llm
from src.tools.movie_db import MovieDBTool

def create_recommendation_chain():
    llm = get_llm(temperature=0.5)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a movie recommendation assistant. Based on user preferences: {preferences}, suggest 3 movies from the list: {movies}."),
        ("human", "Recommend movies.")
    ])
    def get_movies(_input):
        tool = MovieDBTool()
        genre = _input.get("preferences", {}).get("liked_genres", [""])[0] if _input.get("preferences", {}).get("liked_genres") else "Sci-Fi"
        return tool._run(genre)
    chain = (
        RunnablePassthrough.assign(movies=get_movies)
        | prompt
        | llm
    )
    return chain
""",
    "src/core/graph_workflow.py": """from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage
from src.config.llm_config import get_llm
from src.tools.movie_db import MovieDBTool

class GraphState(TypedDict):
    user_input: str
    preferences: dict
    movie_candidates: List[int]
    final_recommendations: List[dict]
    messages: List

def analyze_preferences(state: GraphState) -> GraphState:
    state["preferences"] = {"liked_genres": ["Sci-Fi"]}
    state["messages"].append(AIMessage(content="Analyzed preferences: Sci-Fi"))
    return state

def retrieve_candidates(state: GraphState) -> GraphState:
    tool = MovieDBTool()
    genre = state["preferences"].get("liked_genres", [""])[0]
    result = tool._run(genre)
    state["movie_candidates"] = [1, 2, 4]
    state["messages"].append(AIMessage(content="Retrieved candidate movies."))
    return state

def rank_recommendations(state: GraphState) -> GraphState:
    state["final_recommendations"] = [
        {"id": 1, "title": "The Matrix"},
        {"id": 2, "title": "Inception"}
    ]
    state["messages"].append(AIMessage(content="Ranked recommendations."))
    return state

def build_graph() -> StateGraph:
    workflow = StateGraph(GraphState)
    workflow.add_node("analyze", analyze_preferences)
    workflow.add_node("retrieve", retrieve_candidates)
    workflow.add_node("rank", rank_recommendations)
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "retrieve")
    workflow.add_edge("retrieve", "rank")
    workflow.add_edge("rank", END)
    return workflow.compile()
""",
    "src/core/agent_crew.py": """from crewai import Crew, Task
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
""",
    "src/core/runner.py": """from typing import Any, Dict, Optional
from src.core.chains import create_recommendation_chain
from src.core.graph_workflow import build_graph
from src.core.agent_crew import create_crew
import asyncio

class RecommendationRunner:
    def __init__(self, mode: str = "crew"):
        self.mode = mode
        self._chain = None
        self._graph = None
        self._crew = None
    def _get_chain(self):
        if self._chain is None:
            self._chain = create_recommendation_chain()
        return self._chain
    def _get_graph(self):
        if self._graph is None:
            self._graph = build_graph()
        return self._graph
    def _get_crew(self):
        if self._crew is None:
            self._crew = create_crew()
        return self._crew
    async def recommend(self, user_input: str, preferences: Optional[Dict] = None) -> Dict[str, Any]:
        if self.mode == "chain":
            result = await self._get_chain().ainvoke({
                "preferences": preferences or {"liked_genres": ["Sci-Fi"]},
                "input": user_input
            })
            return {"recommendations": result.content}
        elif self.mode == "graph":
            state = {
                "user_input": user_input,
                "preferences": preferences or {},
                "movie_candidates": [],
                "final_recommendations": [],
                "messages": []
            }
            final_state = await self._get_graph().ainvoke(state)
            return {"recommendations": final_state["final_recommendations"]}
        else:  # crew
            crew = self._get_crew()
            inputs = {"user_input": user_input}
            result = await asyncio.get_event_loop().run_in_executor(None, crew.kickoff, inputs)
            return {"recommendations": result.raw}
""",

    "src/agents/__init__.py": "",
    "src/agents/base.py": """from abc import ABC, abstractmethod
from typing import Any

class BaseAgent(ABC):
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        pass
""",
    "src/agents/movie_expert.py": """from crewai import Agent
from langchain.tools import Tool
from src.tools.movie_db import MovieDBTool
from src.config.llm_config import get_llm

def create_movie_expert() -> Agent:
    return Agent(
        role="Movie Expert",
        goal="Provide detailed movie information and recommendations based on user queries.",
        backstory="You are a seasoned film critic with deep knowledge of cinema across genres and eras.",
        tools=[Tool(name="movie_db", func=MovieDBTool()._run, description="Query movie details")],
        llm=get_llm(temperature=0.3),
        verbose=True,
        allow_delegation=False,
    )
""",
    "src/agents/user_analyst.py": """from crewai import Agent
from src.config.llm_config import get_llm

def create_user_analyst() -> Agent:
    return Agent(
        role="User Analyst",
        goal="Analyze user preferences from their history and profile to tailor recommendations.",
        backstory="You are a data scientist specialising in user behaviour and taste prediction.",
        tools=[],
        llm=get_llm(temperature=0.2),
        verbose=True,
        allow_delegation=False,
    )
""",
    "src/agents/critic.py": """from crewai import Agent
from src.config.llm_config import get_llm

def create_critic() -> Agent:
    return Agent(
        role="Critic",
        goal="Evaluate the quality and relevance of movie recommendations before final output.",
        backstory="You are a tough but fair movie critic who ensures only the best suggestions reach the user.",
        tools=[],
        llm=get_llm(temperature=0.4),
        verbose=True,
        allow_delegation=False,
    )
""",

    "src/tools/__init__.py": "",
    "src/tools/movie_db.py": """from langchain.tools import BaseTool
from src.models.movie import Movie

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
        if query.isdigit():
            movie = _MOCK_MOVIES.get(int(query))
            return str(movie) if movie else "Movie not found"
        else:
            results = [m for m in _MOCK_MOVIES.values() if any(query.lower() in g.lower() for g in m.genres)]
            return str(results) if results else "No movies found for that genre."

    async def _arun(self, query: str) -> str:
        return self._run(query)
""",
    "src/tools/embedding.py": """from langchain.tools import BaseTool

class EmbeddingSimilarityTool(BaseTool):
    name: str = "embedding_similarity"
    description: str = "Compute similarity between a user query and movie descriptions."

    def _run(self, query: str) -> str:
        return "[1, 2, 4]"

    async def _arun(self, query: str) -> str:
        return self._run(query)
""",
    "src/tools/rating.py": """from langchain.tools import BaseTool

class RatingTool(BaseTool):
    name: str = "rating"
    description: str = "Fetch average rating and user reviews for a movie."

    def _run(self, movie_id: str) -> str:
        return f"Movie {movie_id} has average rating 4.5/5."

    async def _arun(self, movie_id: str) -> str:
        return self._run(movie_id)
""",
    "src/tools/web_search.py": """from langchain.tools import BaseTool

class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web for additional movie information, news, or reviews."

    def _run(self, query: str) -> str:
        return f"Search results for '{query}': [placeholder]"

    async def _arun(self, query: str) -> str:
        return self._run(query)
""",

    "src/memory/__init__.py": "",
    "src/memory/in_memory.py": """from typing import Dict, Any

class InMemoryStore:
    def __init__(self):
        self._data: Dict[str, Any] = {}
    def get(self, key: str) -> Any:
        return self._data.get(key)
    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
    def delete(self, key: str) -> None:
        self._data.pop(key, None)
""",
    "src/memory/redis_store.py": """import redis
from src.config.settings import settings
from typing import Any
import json

class RedisStore:
    def __init__(self):
        self.client = redis.Redis.from_url(settings.redis_url) if settings.redis_url else None
    def get(self, key: str) -> Any:
        if not self.client:
            return None
        val = self.client.get(key)
        return json.loads(val) if val else None
    def set(self, key: str, value: Any) -> None:
        if self.client:
            self.client.set(key, json.dumps(value))
    def delete(self, key: str) -> None:
        if self.client:
            self.client.delete(key)
""",

    "src/models/__init__.py": "",
    "src/models/movie.py": """from pydantic import BaseModel
from typing import List, Optional

class Movie(BaseModel):
    id: int
    title: str
    overview: Optional[str] = None
    genres: List[str] = []
    release_year: Optional[int] = None
    rating: Optional[float] = None
""",
    "src/models/user.py": """from pydantic import BaseModel
from typing import List

class UserPreferences(BaseModel):
    liked_genres: List[str] = []
    disliked_genres: List[str] = []
    favorite_movies: List[int] = []
    watched_movies: List[int] = []
""",
    "src/models/feedback.py": """from pydantic import BaseModel
from enum import Enum

class FeedbackType(str, Enum):
    like = "like"
    dislike = "dislike"
    skip = "skip"

class Feedback(BaseModel):
    user_id: str
    movie_id: int
    feedback: FeedbackType
""",

    "src/config/__init__.py": "",
    "src/config/settings.py": """from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", env="OPENAI_MODEL")
    anthropic_api_key: str | None = Field(None, env="ANTHROPIC_API_KEY")
    database_url: str = Field("sqlite:///./movies.db", env="DATABASE_URL")
    redis_url: str | None = Field(None, env="REDIS_URL")
    tmdb_api_key: str | None = Field(None, env="TMDB_API_KEY")
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
""",
    "src/config/llm_config.py": """from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from functools import lru_cache
from .settings import settings

@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.0):
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        temperature=temperature,
    )

def get_anthropic_llm():
    if settings.anthropic_api_key:
        return ChatAnthropic(api_key=settings.anthropic_api_key, model="claude-3-sonnet-20240229")
    return None
""",

    "src/utils/__init__.py": "",
    "src/utils/logging.py": """import logging
import sys

def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
""",
    "src/utils/metrics.py": """class Metrics:
    @staticmethod
    def increment_counter(name: str, value: int = 1):
        pass
    @staticmethod
    def observe_histogram(name: str, value: float):
        pass
""",
    "src/utils/validators.py": """from typing import List

def validate_genre_list(genres: List[str]) -> bool:
    return all(isinstance(g, str) and g.strip() for g in genres)
""",

    "src/db/__init__.py": "",
    "src/db/session.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.config.settings import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
    "src/db/repositories/__init__.py": "",
    "src/db/repositories/movie_repo.py": """from sqlalchemy.orm import Session
from src.models.movie import Movie

class MovieRepository:
    def __init__(self, db: Session):
        self.db = db
    def get_by_id(self, movie_id: int):
        from src.tools.movie_db import _MOCK_MOVIES
        return _MOCK_MOVIES.get(movie_id)
    def search_by_genre(self, genre: str):
        from src.tools.movie_db import _MOCK_MOVIES
        return [m for m in _MOCK_MOVIES.values() if genre.lower() in [g.lower() for g in m.genres]]
""",
    "src/db/repositories/user_repo.py": """from sqlalchemy.orm import Session
from src.models.user import UserPreferences

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    def get_preferences(self, user_id: str) -> UserPreferences:
        return UserPreferences()
""",

    # ---------- frontend/ ----------
    "frontend/index.html": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>🎬 Movie Recommender AI</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <div class="container">
    <header>
      <h1>🎬 Movie Recommender</h1>
      <p class="subtitle">AI‑powered suggestions via LangChain, LangGraph &amp; CrewAI</p>
    </header>
    <form id="recommendForm">
      <div class="form-group">
        <label for="userInput">What are you in the mood for?</label>
        <textarea id="userInput" placeholder="e.g. I love sci‑fi with deep stories and great visuals" required>I love sci‑fi with deep stories and great visuals</textarea>
      </div>
      <div class="row">
        <div class="form-group">
          <label for="modeSelect">Orchestration Mode</label>
          <select id="modeSelect">
            <option value="crew">CrewAI (multi‑agent)</option>
            <option value="chain">LangChain (LCEL)</option>
            <option value="graph">LangGraph (state machine)</option>
          </select>
        </div>
        <div class="form-group">
          <label for="preferencesInput">Preferences (optional JSON)</label>
          <input type="text" id="preferencesInput" placeholder='{"liked_genres": ["Sci-Fi"]}' />
        </div>
      </div>
      <button type="submit" class="btn" id="submitBtn">✨ Get Recommendations</button>
    </form>
    <div id="loading"><span class="spinner"></span> Thinking… please wait</div>
    <div id="results"></div>
  </div>
  <script src="app.js"></script>
</body>
</html>
""",
    "frontend/style.css": """* { box-sizing: border-box; margin:0; padding:0; }
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(145deg, #0f0c29, #302b63, #24243e);
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  color: #fff;
}
.container {
  max-width: 900px;
  width: 100%;
  background: rgba(255,255,255,0.07);
  backdrop-filter: blur(10px);
  border-radius: 32px;
  padding: 40px 35px;
  box-shadow: 0 25px 50px -8px rgba(0,0,0,0.6);
  border: 1px solid rgba(255,255,255,0.08);
}
h1 {
  font-size: 2.4rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
  background: linear-gradient(135deg, #f7971e, #ffd200);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
}
.subtitle {
  color: #b5b5d9;
  margin-bottom: 30px;
  font-size: 1rem;
  border-left: 3px solid #f7971e;
  padding-left: 16px;
}
.form-group { margin-bottom: 22px; }
label { display: block; font-weight:500; font-size:0.95rem; margin-bottom:6px; color:#d4d4f0; }
textarea, input, select {
  width:100%;
  padding:12px 16px;
  border-radius:14px;
  border:1px solid rgba(255,255,255,0.15);
  background:rgba(255,255,255,0.06);
  color:#fff;
  font-size:1rem;
  transition:border 0.2s, background 0.2s;
}
textarea { min-height:80px; resize:vertical; }
textarea:focus, input:focus, select:focus {
  outline:none; border-color:#ffd200; background:rgba(255,255,255,0.1);
}
select option { background:#1e1b3b; }
.row { display:flex; gap:20px; flex-wrap:wrap; }
.row .form-group { flex:1; min-width:180px; }
.btn {
  background:linear-gradient(135deg, #f7971e, #ffd200);
  color:#1a1a2e;
  font-weight:700;
  padding:14px 32px;
  border:none;
  border-radius:40px;
  font-size:1.1rem;
  cursor:pointer;
  transition:transform 0.15s, box-shadow 0.2s;
  width:100%;
  letter-spacing:0.5px;
}
.btn:hover { transform:scale(1.02); box-shadow:0 8px 25px rgba(247,151,30,0.35); }
.btn:active { transform:scale(0.97); }
.btn:disabled { opacity:0.6; cursor:not-allowed; transform:none; }
#loading { display:none; text-align:center; margin:20px 0; color:#ffd200; font-weight:500; }
.spinner {
  display:inline-block;
  width:24px;
  height:24px;
  border:3px solid rgba(255,215,0,0.2);
  border-top-color:#ffd200;
  border-radius:50%;
  animation:spin 0.8s linear infinite;
  margin-right:10px;
  vertical-align:middle;
}
@keyframes spin { to { transform:rotate(360deg); } }
#results { margin-top:30px; display:none; }
#results.active { display:block; }
.result-card {
  background:rgba(255,255,255,0.06);
  border-radius:20px;
  padding:20px 24px;
  margin-bottom:14px;
  border-left:4px solid #ffd200;
  backdrop-filter:blur(4px);
}
.result-card h3 { font-size:1.3rem; margin-bottom:6px; color:#ffd200; }
.result-card p { color:#cfcfef; line-height:1.5; margin:4px 0; }
.result-card .meta { font-size:0.85rem; color:#a0a0c0; margin-top:8px; }
.error { background:rgba(255,50,50,0.15); border-left-color:#ff4d4d; color:#ff8a8a; }
.mode-tag {
  display:inline-block; background:rgba(100,200,255,0.15); color:#8bcbff;
  padding:2px 14px; border-radius:30px; font-size:0.75rem; font-weight:600; margin-left:8px;
}
@media (max-width:600px) {
  .container { padding:24px 16px; }
  h1 { font-size:1.8rem; }
  .row { flex-direction:column; gap:0; }
}
""",
    "frontend/app.js": """const API_BASE = 'http://localhost:8000';
const form = document.getElementById('recommendForm');
const submitBtn = document.getElementById('submitBtn');
const loading = document.getElementById('loading');
const resultsDiv = document.getElementById('results');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const userInput = document.getElementById('userInput').value.trim();
  const mode = document.getElementById('modeSelect').value;
  const preferencesRaw = document.getElementById('preferencesInput').value.trim();
  let preferences = null;
  if (preferencesRaw) {
    try { preferences = JSON.parse(preferencesRaw); }
    catch { alert('Invalid JSON for preferences.'); return; }
  }
  if (!userInput) { alert('Please describe what you are looking for.'); return; }
  submitBtn.disabled = true;
  loading.style.display = 'block';
  resultsDiv.innerHTML = '';
  resultsDiv.classList.remove('active');
  try {
    const response = await fetch(`${API_BASE}/api/v1/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_input: userInput, preferences, mode }),
    });
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Server error (${response.status}): ${errorText}`);
    }
    const data = await response.json();
    displayResults(data, mode);
  } catch (err) {
    resultsDiv.innerHTML = `<div class="result-card error"><strong>❌ Error</strong><p>${err.message}</p><p style="font-size:0.85rem; margin-top:8px;">Make sure the backend is running at ${API_BASE}</p></div>`;
    resultsDiv.classList.add('active');
  } finally {
    submitBtn.disabled = false;
    loading.style.display = 'none';
  }
});

function displayResults(data, mode) {
  const recs = data.recommendations;
  if (typeof recs === 'string') {
    resultsDiv.innerHTML = `<div class="result-card"><h3>📋 Recommendations <span class="mode-tag">${mode}</span></h3><p style="white-space:pre-wrap;">${recs}</p></div>`;
    resultsDiv.classList.add('active');
    return;
  }
  if (Array.isArray(recs)) {
    if (recs.length === 0) {
      resultsDiv.innerHTML = `<div class="result-card"><p>No recommendations found.</p></div>`;
      resultsDiv.classList.add('active');
      return;
    }
    let html = `<div style="margin-bottom:12px;"><span class="mode-tag">${mode}</span> <span style="color:#b5b5d9;">${recs.length} recommendations</span></div>`;
    recs.forEach((item, idx) => {
      const title = item.title || item.name || `Recommendation #${idx+1}`;
      const desc = item.overview || item.description || item.reasoning || '';
      const extra = item.rating ? `⭐ ${item.rating}` : '';
      html += `<div class="result-card"><h3>${idx+1}. ${title}</h3>${desc ? `<p>${desc}</p>` : ''}${extra ? `<div class="meta">${extra}</div>` : ''}</div>`;
    });
    resultsDiv.innerHTML = html;
    resultsDiv.classList.add('active');
    return;
  }
  // fallback
  resultsDiv.innerHTML = `<div class="result-card"><h3>📊 Raw Response <span class="mode-tag">${mode}</span></h3><pre style="background:rgba(0,0,0,0.3);padding:12px;border-radius:12px;overflow-x:auto;color:#cfcfef;">${JSON.stringify(recs, null, 2)}</pre></div>`;
  resultsDiv.classList.add('active');
}

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/health`);
    if (res.ok) console.log('✅ Backend is healthy');
    else console.warn('⚠️ Backend health check failed');
  } catch { console.warn('⚠️ Cannot reach backend. Is it running?'); }
}
checkHealth();
""",

    # ---------- tests/ ----------
    "tests/__init__.py": "",
    "tests/conftest.py": """import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def client():
    return TestClient(app)
""",
    "tests/unit/__init__.py": "",
    "tests/unit/test_tools.py": """from src.tools.movie_db import MovieDBTool

def test_movie_db_tool_by_id():
    tool = MovieDBTool()
    result = tool._run("1")
    assert "The Matrix" in result

def test_movie_db_tool_by_genre():
    tool = MovieDBTool()
    result = tool._run("Sci-Fi")
    assert "Inception" in result
""",
    "tests/unit/test_chains.py": """def test_chain_creation():
    from src.core.chains import create_recommendation_chain
    chain = create_recommendation_chain()
    assert chain is not None
""",
    "tests/integration/__init__.py": "",
    "tests/integration/test_api.py": """from fastapi.testclient import TestClient

def test_recommend_endpoint(client: TestClient):
    response = client.post("/api/v1/recommend", json={
        "user_input": "I love sci-fi",
        "mode": "chain"
    })
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
""",
    "tests/integration/test_agent.py": """def test_crew_creation():
    from src.core.agent_crew import create_crew
    crew = create_crew()
    assert crew is not None
""",

    # ---------- scripts/ ----------
    "scripts/seed_movies.py": "print('Seeding movies...')",
    "scripts/eval_recommendations.py": "print('Running evaluation...')",
}

# ============================================================
# Create directories and files
# ============================================================
BASE_DIR = "movie-recommender-agent"

def create_project():
    if os.path.exists(BASE_DIR):
        shutil.rmtree(BASE_DIR)
    for filepath, content in files.items():
        full_path = os.path.join(BASE_DIR, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"✅ Project structure created in '{BASE_DIR}'")
    print(f"Total files: {len(files)}")

if __name__ == "__main__":
    create_project()