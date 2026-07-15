# movie-recommender-ai
an intelligent movie recommendation system powered by LangChain, LangGraph, CrewAI, and FastAPI. Supports three orchestration modes: LCEL chain, state‑machine graph, and multi‑agent crew. Includes a beautiful frontend.
# 🎬 Movie Recommender AI Agent

An intelligent, multi‑paradigm movie recommendation system that leverages **LangChain**, **LangGraph**, and **CrewAI** to deliver personalised film suggestions. Built with **FastAPI** for high‑performance REST APIs and a sleek frontend for seamless interaction.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.12-009688)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.15-1C3C3C)](https://www.langchain.com/)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.80.2-FF6B00)](https://www.crewai.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## ✨ Features

- **Three orchestration modes** – choose between:
  - **LangChain LCEL chain** – simple, fast, single‑pass generation.
  - **LangGraph state machine** – multi‑step reasoning with persistent state.
  - **CrewAI multi‑agent crew** – collaborative agents (User Analyst, Movie Expert, Critic) for richer recommendations.
- **Modular design** – easily swap LLMs, add tools, or integrate vector databases.
- **Async FastAPI** – high concurrency, non‑blocking I/O.
- **Beautiful frontend** – responsive HTML/CSS/JS interface to test all modes interactively.
- **Singleton LLM clients** – reduce latency and token costs.
- **Docker‑ready** – quick deployment with `docker-compose`.

---

## 🛠 Tech Stack

| Component          | Technology                                                                 |
|--------------------|----------------------------------------------------------------------------|
| Backend Framework  | [FastAPI](https://fastapi.tiangolo.com/)                                   |
| Orchestration      | [LangChain](https://www.langchain.com/), [LangGraph](https://langchain-ai.github.io/langgraph/), [CrewAI](https://www.crewai.com/) |
| LLMs               | OpenAI (default) – extensible to Anthropic, Cohere, etc.                   |
| Database           | SQLite (can be swapped for PostgreSQL, etc.)                               |
| Cache / Memory     | Redis (optional)                                                           |
| Frontend           | Plain HTML, CSS, JavaScript (served as static files)                      |
| Deployment         | Docker, Docker Compose                                                     |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher (3.12 recommended)
- OpenAI API key (or other LLM key)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/movie-recommender-ai.git
cd movie-recommender-ai
