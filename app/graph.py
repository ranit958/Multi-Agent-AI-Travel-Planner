
import os
import uuid

import psycopg
from psycopg.rows import dict_row

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import HumanMessage

from app.agents.flight_agent import flight_agent
from app.agents.hotel_agent import hotel_agent
from app.agents.itinerary_agent import itinerary_agent
from app.agents.response_agent import response_agent
from app.state import TravelState

load_dotenv()


def get_database_url():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL is missing.")

    if "sslmode=" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url += f"{separator}sslmode=require"

    return database_url


def create_graph(checkpointer):

    graph = StateGraph(TravelState)

    graph.add_node("flight_agent", flight_agent)
    graph.add_node("hotel_agent", hotel_agent)
    graph.add_node("itinerary_agent", itinerary_agent)
    graph.add_node("response_agent", response_agent)

    graph.add_edge(START, "flight_agent")
    graph.add_edge("flight_agent", "hotel_agent")
    graph.add_edge("hotel_agent", "itinerary_agent")
    graph.add_edge("itinerary_agent", "response_agent")
    graph.add_edge("response_agent", END)

    return graph.compile(checkpointer=checkpointer)


def create_travel_graph():

    conn = psycopg.connect(
        get_database_url(),
        autocommit=True,
        row_factory=dict_row
    )

    checkpointer = PostgresSaver(conn)
    checkpointer.setup()

    travel_graph = create_graph(checkpointer)

    return travel_graph, conn


def run_travel_agent(
    travel_graph,
    user_input: str,
    thread_id: str | None = None
):

    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = travel_graph.invoke(
        {
            "messages": [HumanMessage(content=user_input)],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )

    return {
        "thread_id": thread_id,
        "answer": result["messages"][-1].content,
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "itinerary": result.get("itinerary", ""),
        "llm_calls": result.get("llm_calls", 0)
    }
