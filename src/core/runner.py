from typing import Any, Dict, Optional
from src.core.chains import create_recommendation_chain
from src.core.graph_workflow import build_graph
from src.core.agent_crew import create_crew
import asyncio

class RecommendationRunner:
    def __init__(self, mode: str = "crew"):
        """
        mode: "chain", "graph", or "crew"
        """
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
            # CrewAI expects a dict with keys matching task descriptions
            inputs = {"user_input": user_input}
            # Run crew (blocking, but we can run in executor)
            result = await asyncio.get_event_loop().run_in_executor(None, crew.kickoff, inputs)
            return {"recommendations": result.raw}