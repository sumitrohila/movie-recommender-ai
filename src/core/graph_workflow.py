from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from src.config.llm_config import get_llm
from src.tools.movie_db import MovieDBTool

class GraphState(TypedDict):
    user_input: str
    preferences: dict
    movie_candidates: List[int]
    final_recommendations: List[dict]
    messages: List

def analyze_preferences(state: GraphState) -> GraphState:
    """Node: Extract preferences from user input."""
    llm = get_llm(temperature=0.0)
    # Simple mock: assume user likes Sci-Fi
    state["preferences"] = {"liked_genres": ["Sci-Fi"]}
    state["messages"].append(AIMessage(content="Analyzed preferences: Sci-Fi"))
    return state

def retrieve_candidates(state: GraphState) -> GraphState:
    """Node: Retrieve movies based on preferences."""
    tool = MovieDBTool()
    genre = state["preferences"].get("liked_genres", [""])[0]
    result = tool._run(genre)
    # Parse result (mock: get IDs from string)
    # In real, we'd parse list of movies
    # For now, just assign some IDs
    state["movie_candidates"] = [1, 2, 4]  # hardcoded for demo
    state["messages"].append(AIMessage(content="Retrieved candidate movies."))
    return state

def rank_recommendations(state: GraphState) -> GraphState:
    """Node: Rank candidates using LLM."""
    llm = get_llm(temperature=0.3)
    # Mock: just pick first two
    state["final_recommendations"] = [{"id": 1, "title": "The Matrix"}, {"id": 2, "title": "Inception"}]
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