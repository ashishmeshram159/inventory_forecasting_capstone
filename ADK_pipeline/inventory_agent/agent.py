import pandas as pd
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool

from google.genai import types
from prompts.prompts import *
from RAG.rag_utility import query_promotional_offers
from tools.db_tools import *
from sqlalchemy import create_engine, text
from collections import Counter
from datetime import datetime


load_dotenv()


get_product_context_tool = FunctionTool(get_product_context_with_month)

get_category_context_tool = FunctionTool(get_category_context_with_month)

get_overall_summary_tool = FunctionTool(get_overall_category_summary)

query_inventory_tool = FunctionTool(query_inventory)

rag_offer_tool = FunctionTool(query_promotional_offers)


salutation_agent = Agent(
    model="gemini-2.0-flash-001",
    name="salutation_agent",
    instruction=salutation_prompt,
    description="Handles greetings and delegates analytical questions to the demand predictor agent."
)



closing_agent = Agent(
    model="gemini-2.0-flash-001",
    name="closing_agent",
    instruction=closing_prompt,
    description="Handles conversation closure and delegations back to main agent if needed."
)


offers_agent = Agent(
    model="gemini-2.0-flash-001",
    name="offers_agent",
    instruction=holiday_offer_prompt,
    description="Provides information about any ongoing or past offers using the RAG tool.",
    tools=[rag_offer_tool]
)


demand_predictor_agent = Agent(
    model="gemini-2.0-flash-001",
    name="demand_predictor_agent",
    instruction=demand_predictor_prompt,
    description="Predicts demand using inventory context, categories, and RAG offers. Must be used only when demand of inventory, products etc is asked",
    tools=[
        query_inventory_tool,
        get_product_context_tool,
        get_category_context_tool,
        get_overall_summary_tool,
        rag_offer_tool
    ]
)



salutation_tool = AgentTool(agent=salutation_agent)
closing_tool = AgentTool(agent=closing_agent)
offers_agent_tool = AgentTool(agent=offers_agent)
demand_predictor_tool = AgentTool(agent=demand_predictor_agent)


root_agent = Agent(
    model="gemini-2.0-flash-001",
    name="root_conversation_agent",
    instruction=root_prompt,
    description="Routes user messages to the appropriate agent.",
    tools=[
        salutation_tool,
        closing_tool,
        offers_agent_tool,
        demand_predictor_tool
    ]
)

APP_NAME = "inventory_conversation_system"
USER_ID = "dp01"
SESSION_ID = "001"


session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


def chat_with_system(user_query: str):
    content = types.Content(role='user', parts=[types.Part(text=user_query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)

