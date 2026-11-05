# TripMate AI — Multi-Agent AI Travel Planner

TripMate AI is an intelligent, multi-agent travel planning system built with **LangGraph**, **LangChain**, **FastAPI**, and **Groq (`openai/gpt-oss-120b`)**. It coordinates specialized AI agents to search live flight schedules, retrieve top hotel recommendations, formulate a comprehensive day-by-day itinerary, and present the final plan through a modern web UI.

---

## 🚀 Key Features

- **Multi-Agent Orchestration**: Powered by LangGraph, delegating specialized tasks to dedicated agents.
- **Live Flight Information**: Fetches scheduled flight and route data using the AviationStack API and IATA code resolution.
- **Hotel & Accommodation Research**: Retrieves top-rated hotels and stays using Tavily Web Search.
- **Smart Day-by-Day Itineraries**: Synthesizes travel constraints, budgets, and recommendations into practical daily schedules.
- **PostgreSQL Session Memory**: Thread-based conversation persistence with `PostgresSaver`.
- **Modern Web Interface**: Clean, responsive frontend built with FastAPI, Jinja2, HTML, CSS, and Markdown rendering.

---

## 🏗️ Architecture & Agent Workflow

The LangGraph pipeline runs sequentially through specialized nodes:

```
[START]
   │
   ▼
1. Flight Agent      ─── (AviationStack API + airportsdata)
   │
   ▼
2. Hotel Agent       ─── (Tavily Search API)
   │
   ▼
3. Itinerary Agent   ─── (Groq LLM: openai/gpt-oss-120b)
   │
   ▼
4. Response Agent    ─── (Groq LLM: openai/gpt-oss-120b)
   │
   ▼
 [END]
```

---

## 📁 Project Structure

```
Multi-Agent-AI-Travel-Planner/
├── app/
│   ├── agents/                   # Individual LangGraph agent nodes
│   │   ├── flight_agent.py       # Resolves routes & fetches flight data
│   │   ├── hotel_agent.py        # Searches accommodations with Tavily
│   │   ├── itinerary_agent.py    # Formulates day-by-day travel plan
│   │   └── response_agent.py     # Synthesizes final formatted response
│   ├── schemas/                  # Pydantic models for API request/response
│   │   └── travel_request.py
│   ├── tools/                    # External API tool wrappers
│   │   ├── flight_tool.py        # AviationStack & IATA location resolver
│   │   └── tavily_tool.py        # Tavily search wrapper
│   ├── state.py                  # LangGraph TravelState TypedDict
│   ├── graph.py                  # LangGraph StateGraph & PostgreSQL checkpointer
│   └── app.py                    # FastAPI server & route handlers
│
├── static/                       # Frontend assets
│   ├── script.js                 # API interactions & Markdown rendering
│   └── style.css                 # Dark theme responsive styling
├── templates/
│   └── index.html                # Jinja2 frontend template
├── requirements.txt              # Project dependencies
└── .env                          # Environment variables & API keys
```

---

## 🛠️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/ranitmaity/Multi-Agent-AI-Travel-Planner.git
cd Multi-Agent-AI-Travel-Planner
```

### 2. Create and Activate a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate       # On macOS/Linux
# venv\Scripts\activate       # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
DEFAULT_ORIGIN_IATA=CCU
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require
```

> **Note**: For PostgreSQL connections (e.g. Render, Supabase, Neon), ensure `sslmode=require` is used.

---

## 🚦 Running the Application

Start the FastAPI development server:

```bash
uvicorn app.app:app --reload --port 8000
```

Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Web UI interface |
| `GET` | `/health` | API health check |
| `POST` | `/api/travel` | Generate travel plan (`message`, optional `thread_id`) |

### Example Request (`POST /api/travel`):
```json
{
  "message": "Plan a complete 7 days Japan trip from India under 2 lakhs.",
  "thread_id": null
}
```

---

## 🧰 Tech Stack

- **Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph), [LangChain](https://github.com/langchain-ai/langchain)
- **LLM Provider**: [Groq](https://groq.com/) (`openai/gpt-oss-120b`)
- **Backend API**: [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/)
- **Database / Checkpointer**: [PostgreSQL](https://www.postgresql.org/) via `psycopg` & `langgraph-checkpoint-postgres`
- **Search & Flight Tools**: [Tavily AI](https://tavily.com/), [AviationStack](https://aviationstack.com/), [airportsdata](https://pypi.org/project/airportsdata/)
- **Frontend**: HTML5, CSS3, JavaScript, Marked.js (Markdown rendering)
