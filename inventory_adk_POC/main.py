from google.adk.agents import Agent
from cap_git_repo.inventory_forecasting_capstone.inventory_adk.agents.agent import inventory_lookup_agent

# Root agent delegates to the sub-agent
inventory_root_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="inventory_root_agent",
    description="Main entry for inventory queries.",
    instruction=(
        "If user asks about any Product ID, delegate to inventory_lookup_agent. "
        "Summarize the output clearly."
    ),
    sub_agents=[inventory_lookup_agent]
)

if __name__ == "__main__":
    print("💬 Inventory Agent ready. Example: 'inventory for T0002'")
    while True:
        q = input("You> ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        resp = inventory_root_agent.run(user_id="ashish", message=q)
        print("Agent>", resp["content"]["parts"][0]["text"])
