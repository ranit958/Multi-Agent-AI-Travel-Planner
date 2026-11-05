
from pathlib import Path
from contextlib import asynccontextmanager
import traceback

import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.graph import create_travel_graph, run_travel_agent
from app.schemas.travel_request import TravelRequest


BASE_DIR = Path(__file__).resolve().parent.parent


# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):

    travel_graph, conn = create_travel_graph()

    app.state.travel_graph = travel_graph
    app.state.db_conn = conn

    try:
        yield
    finally:
        conn.close()


# Application factory
def create_app() -> FastAPI:

    app = FastAPI(
        title="Multi Agent AI Travel Planner",
        description="LangGraph Multi-Agent Travel Planner with FastAPI Frontend",
        version="1.0.0",
        lifespan=lifespan
    )

    # Static files
    app.mount(
        "/static",
        StaticFiles(directory=str(BASE_DIR / "static")),
        name="static"
    )

    # Jinja2 templates
    app.state.templates = Jinja2Templates(
        directory=str(BASE_DIR / "templates")
    )

    return app


app = create_app()


# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return request.app.state.templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# Health check
@app.get("/health")
async def health_check():

    return {
        "status": "ok",
        "message": "AI Travel Planner API is running"
    }


# Favicon
@app.get("/favicon.ico")
async def favicon():

    return JSONResponse(content={})


# Travel planner API
@app.post("/api/travel")
def travel_planner(
    request_data: TravelRequest,
    request: Request
):

    try:
        user_message = request_data.message.strip()

        if not user_message:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Message cannot be empty."
                }
            )

        travel_graph = getattr(
            request.app.state,
            "travel_graph",
            None
        )

        if travel_graph is None:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "error": "Travel graph not initialized."
                }
            )

        result = run_travel_agent(
            travel_graph=travel_graph,
            user_input=user_message,
            thread_id=request_data.thread_id
        )

        return {
            "success": True,
            "thread_id": result["thread_id"],
            "answer": result["answer"],
            "flight_results": result["flight_results"],
            "hotel_results": result["hotel_results"],
            "itinerary": result["itinerary"],
            "llm_calls": result["llm_calls"]
        }

    except Exception:
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "An internal error occurred while planning your trip."
            }
        )


if __name__ == "__main__":

    uvicorn.run(
        "app.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
