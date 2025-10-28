from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///data/db_files/inventory.db")

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM inventory LIMIT 5"))
    rows = result.mappings().all()

for row in rows:
    print(row)
