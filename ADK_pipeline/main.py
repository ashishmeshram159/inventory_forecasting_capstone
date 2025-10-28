from google.adk.runners import WebRunner
from inventory_agent.agent import root_agent
from google.adk.sessions import InMemorySessionService

APP_NAME = "inventory_conversation_system"
USER_ID = "dp01"
SESSION_ID = "001"

if __name__ == "__main__":
    session_service = InMemorySessionService()
    runner = WebRunner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    runner.run(host="0.0.0.0", port=8080)
