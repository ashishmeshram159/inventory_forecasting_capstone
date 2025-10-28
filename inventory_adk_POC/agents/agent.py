# agents/agent.py
import pandas as pd
from google.adk.agents import Agent
from google.adk.tools import FunctionTool


# -------------------------------
# Sub-agent Tool: Reads Excel file
# -------------------------------
def get_inventory(product_id: str):
    """Simple tool: read Excel and return info."""
    df = pd.read_excel("data/sample_inventory.xlsx")
    row = df[df["Product ID"] == product_id]
    if row.empty:
        return {"error": f"No product found for {product_id}"}
    record = row.iloc[0].to_dict()
    return {
        "Product ID": record["Product ID"],
        "Product Name": record["Product Name"],
        "Category": record["Category"],
        "Region": record["Region"],
        "Inventory Level": int(record["Inventory Level"]),
    }


# Register as ADK tool
inventory_tool = FunctionTool(get_inventory)


# -------------------------------
# Sub-Agent
# -------------------------------
inventory_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="inventory_agent",
    description="Handles inventory lookups using Excel",
    instruction="Given a Product ID, use get_inventory tool and return its details.",
    tools=[inventory_tool],
)


# -------------------------------
# Root Agent
# -------------------------------
root_agent = Agent(
    model="gemini-2.0-flash-exp",
    name="root_agent",
    description="Root agent that routes queries to the inventory sub-agent.",
    instruction="When user asks about any product, delegate to inventory_agent.",
    sub_agents=[inventory_agent],
)
