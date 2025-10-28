import pandas as pd
import os
from sqlalchemy import create_engine


# Ensure directory exists
db_dir = "data/db_files"
os.makedirs(db_dir, exist_ok=True)   # creates folder if not already there

# Define database path & engine
db_path = os.path.join(db_dir, "inventory.db")
engine = create_engine(f"sqlite:///{db_path}", echo=False)

# Load Excel and write to DB
df = pd.read_excel("data/op_prod_name_ref_data.xlsx")


# Create a local SQLite DB file:
df.to_sql("inventory", engine, index=False, if_exists="replace")

print(f"Local DB created successfully at → {db_path}")

