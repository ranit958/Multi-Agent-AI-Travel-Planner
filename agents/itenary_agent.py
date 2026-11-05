from app.state import TravelState
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY :
    raise ValueError("GROQ_API_KEY is missing. Please add it to your .env file.")


ininery_agent_llm = ChatGroq(
    model="meta-llama/llama-prompt-guard-2-86m",
    api_key=GROQ_API_KEY
)



def itinerary_agent(state: TravelState):
    prompt = f"""
Create a complete travel itinerary.

User Query:
{state['user_query']}

Flight Results:
{state['flight_results']}

Hotel Results:
{state['hotel_results']}

Make the itinerary practical, budget-aware, and easy to follow.
"""

    response = ininery_agent_llm.invoke([
        SystemMessage(content="You are an expert travel planner."),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }