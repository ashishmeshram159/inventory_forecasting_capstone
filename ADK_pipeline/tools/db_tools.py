import numpy as np
import pandas as pd
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool
from google.genai import types
from sqlalchemy import create_engine, text
from collections import Counter
from datetime import datetime



def query_inventory(product_id: str):
    """Fetch product info from local SQLite DB (simulated RDS)."""
    engine = create_engine("sqlite:///data/db_files/inventory.db", echo=False)
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM inventory WHERE [Product ID] = :pid"),
            {"pid": product_id}
        ).mappings().first()
    if not result:
        return {"error": f"No product found for {product_id}"}
    return dict(result)



# Load demand data from Excel file
# demand_data = []
# try:
#     df = pd.read_excel('cap_git_repo\inventory_forecasting_capstone\ADK_pipeline\data\op_prod_name_ref_data.xlsx')  # Assumes file is in the current directory
#     demand_data = df.to_dict('records')  # Convert DataFrame to list of dicts
#     print("Demand data loaded successfully from demand_data.xlsx")
# except FileNotFoundError:
#     print("Error: demand_data.xlsx not found. Using empty data.")
# except Exception as e:
#     print(f"Error loading demand data: {e}. Using empty data.")

# Load promotional offers from text file
# promotional_offers = []

# try:
#     with open(r"cap_git_repo/inventory_forecasting_capstone/ADK_pipeline/data/Holiday_ads.txt", 'r', encoding='utf-8') as file:
#         content = file.read()
#         # Split by double newlines or similar to separate offers
#         offers_raw = content.split('\n\n')  # Assuming offers are separated by blank lines
#         for offer in offers_raw:
#             if offer.strip():
#                 # Split by tab for title/dates and newline for description
#                 parts = offer.split('\t')
#                 if len(parts) >= 2:
#                     title_dates = parts[0].strip()
#                     description = parts[1].strip() if len(parts) > 1 else ""
#                     full_offer = f"{title_dates}\n{description}"
#                     promotional_offers.append(full_offer)
#     print("Promotional offers loaded successfully from promotional_offers.txt")
# except FileNotFoundError:
#     print("Error: promotional_offers.txt not found. Using empty offers.")
# except Exception as e:
#     print(f"Error loading promotional offers: {e}. Using empty offers.")

# def predict_demand1(product_id: str, store_id: str, date: str):
#     """
#     Predicts demand for a given product, store, and date.
#     - Looks up existing 'Demand Forecast' if available.
#     - Otherwise, calculates a simple average based on Units Sold and Units Ordered.
#     - Returns None if no data found.
#     """
#     try:
#         # Filter data for matching product_id, store_id, and date
#         matching_records = [
#             record for record in demand_data
#             if record["Product ID"] == product_id and record["Store ID"] == store_id and record["Date"] == date
#         ]
        
#         if matching_records:
#             # Use existing Demand Forecast if available
#             forecast = matching_records[0].get("Demand Forecast")
#             if forecast is not None:
#                 return forecast
#             # Fallback: Simple average of Units Sold and Units Ordered
#             units_sold = matching_records[0]["Units Sold"]
#             units_ordered = matching_records[0]["Units Ordered"]
#             return (units_sold + units_ordered) / 2
#         else:
#             # If no exact match, return a general average for the product (basic logic)
#             product_records = [r for r in demand_data if r["Product ID"] == product_id]
#             if product_records:
#                 avg_forecast = sum(r.get("Demand Forecast", 0) for r in product_records) / len(product_records)
#                 return avg_forecast
#             return None
#     except Exception as e:
#         print(f"Error predicting demand for {product_id} in {store_id} on {date}: {e}")
#         return None


# def predict_demand(product_id: str, store_id: str, date: str):
#     """
#     Predict demand for a given product, store, and date using the database.
#     - Checks if an existing Demand Forecast exists in DB.
#     - Otherwise, computes a simple average of Units Sold and Units Ordered.
#     """
#     try:
#         # connect to your local SQLite DB (RDS simulation)
#         engine = create_engine("sqlite:///data/db_files/inventory.db", echo=False)

#         with engine.connect() as conn:
#             # 1️⃣ Try exact match (Product + Store + Date)
#             query = text("""
#                 SELECT [Demand Forecast], [Units Sold], [Units Ordered]
#                 FROM inventory
#                 WHERE [Product ID] = :pid AND [Store ID] = :sid AND Date = :date
#                 LIMIT 1
#             """)
#             result = conn.execute(query, {"pid": product_id, "sid": store_id, "date": date}).mappings().first()

#             if result:
#                 forecast = result["Demand Forecast"]
#                 if forecast is not None:
#                     return forecast
#                 # fallback if forecast is null
#                 return (result["Units Sold"] + result["Units Ordered"]) / 2

#             # 2️⃣ If no exact match, compute average forecast for that product
#             avg_query = text("""
#                 SELECT AVG([Demand Forecast]) AS avg_forecast
#                 FROM inventory
#                 WHERE [Product ID] = :pid
#             """)
#             avg_result = conn.execute(avg_query, {"pid": product_id}).mappings().first()
#             if avg_result and avg_result["avg_forecast"]:
#                 return avg_result["avg_forecast"]

#         # No data found at all
#         return None

#     except Exception as e:
#         print(f"Error predicting demand for {product_id} in {store_id} on {date}: {e}")
#         return None
    


# def get_product_context(product_id: str, store_id: str = None):
#     """
#     Retrieves the latest contextual data for a given product.
#     Handles store-specific and aggregated queries using robust date handling.
#     Automatically falls back to aggregate view if no store data found.
#     """
#     try:
#         engine = create_engine("sqlite:///data/db_files/inventory.db", echo=False)

#         with engine.connect() as conn:
#             # 1️⃣ Determine latest date available for this product (string comparison is fine since ISO format)
#             date_query = text("""
#                 SELECT MAX(Date) AS latest_date
#                 FROM inventory
#                 WHERE [Product ID] = :pid
#             """)
#             latest = conn.execute(date_query, {"pid": product_id}).mappings().first()
#             latest_date = latest["latest_date"] if latest else None

#             if not latest_date:
#                 return {"error": f"No data found for Product {product_id}"}

#             # 2️⃣ Try store-specific record first (if store_id provided)
#             if store_id:
#                 store_row = conn.execute(text("""
#                     SELECT Category, Region, [Inventory Level], [Units Sold], [Units Ordered],
#                            Price, Discount, [Weather Condition], [Competitor Pricing],
#                            Seasonality, [Product Name], [Store ID], Date
#                     FROM inventory
#                     WHERE [Product ID] = :pid AND [Store ID] = :sid
#                     ORDER BY Date DESC
#                     LIMIT 1
#                 """), {"pid": product_id, "sid": store_id}).mappings().first()

#                 if store_row:
#                     return {
#                         "Product ID": product_id,
#                         "Store ID": store_id,
#                         "Date": store_row["Date"],
#                         "Product Name": store_row["Product Name"],
#                         "Category": store_row["Category"],
#                         "Region": store_row["Region"],
#                         "Inventory Level": float(store_row["Inventory Level"]),
#                         "Units Sold": float(store_row["Units Sold"]),
#                         "Units Ordered": float(store_row["Units Ordered"]),
#                         "Price": float(store_row["Price"]),
#                         "Discount": float(store_row["Discount"]),
#                         "Competitor Pricing": float(store_row["Competitor Pricing"]),
#                         "Weather Condition": store_row["Weather Condition"],
#                         "Seasonality": store_row["Seasonality"]
#                     }

#                 # if store not found, fall back to aggregate
#                 print(f"⚠️ No recent data for store {store_id}. Falling back to aggregate view.")

#             # 3️⃣ Aggregate across all stores for latest date
#             all_rows = conn.execute(text("""
#                 SELECT Category, Region, [Inventory Level], [Units Sold], [Units Ordered],
#                        Price, Discount, [Weather Condition], [Competitor Pricing],
#                        Seasonality, [Product Name]
#                 FROM inventory
#                 WHERE [Product ID] = :pid AND Date = :date
#             """), {"pid": product_id, "date": latest_date}).mappings().all()

#             if not all_rows:
#                 return {"error": f"No data found for Product {product_id} on {latest_date}"}

#             # Aggregate numeric fields
#             total_inventory = sum(float(r["Inventory Level"]) for r in all_rows)
#             total_sold = sum(float(r["Units Sold"]) for r in all_rows)
#             total_ordered = sum(float(r["Units Ordered"]) for r in all_rows)
#             avg_price = sum(float(r["Price"]) for r in all_rows) / len(all_rows)
#             avg_discount = sum(float(r["Discount"]) for r in all_rows) / len(all_rows)
#             avg_comp_price = sum(float(r["Competitor Pricing"]) for r in all_rows) / len(all_rows)

#             # Categorical mode helper
#             def get_mode(values):
#                 vals = [v for v in values if v]
#                 return Counter(vals).most_common(1)[0][0] if vals else None

#             season_mode = get_mode([r["Seasonality"] for r in all_rows])
#             weather_mode = get_mode([r["Weather Condition"] for r in all_rows])
#             regions = sorted(set(r["Region"] for r in all_rows if r["Region"]))

#             return {
#                 "Product ID": product_id,
#                 "Date": latest_date,
#                 "Product Name": all_rows[0]["Product Name"],
#                 "Category": all_rows[0]["Category"],
#                 "Regions": regions,
#                 "Inventory Level (Total)": round(total_inventory, 2),
#                 "Units Sold (Total)": round(total_sold, 2),
#                 "Units Ordered (Total)": round(total_ordered, 2),
#                 "Average Price": round(avg_price, 2),
#                 "Average Discount": round(avg_discount, 2),
#                 "Average Competitor Pricing": round(avg_comp_price, 2),
#                 "Most Common Weather Condition": weather_mode,
#                 "Most Common Seasonality": season_mode
#             }

#     except Exception as e:
#         print(f"❌ Error fetching product context for {product_id}: {e}")
#         return {"error": str(e)}



# ----------------------------------------------------------------
# Helper Function: fetch data for given product, month, year, store
# ----------------------------------------------------------------
def _fetch_context_for_month(engine, product_id: str, store_id: str, year: int, month: int):
    """Fetch aggregated product context for given year, month, and optional store."""
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(
                "SELECT * FROM inventory WHERE [Product ID] = :pid",
                conn,
                params={"pid": product_id}
            )

        if df.empty:
            return None

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month

        # Filter by year-month
        month_df = df[(df["Year"] == year) & (df["Month"] == month)]
        if store_id:
            month_df = month_df[month_df["Store ID"] == store_id]

        if month_df.empty:
            return None

        # Aggregate numeric fields
        total_inventory = month_df["Inventory Level"].sum()
        total_sold = month_df["Units Sold"].sum()
        total_ordered = month_df["Units Ordered"].sum()
        avg_price = month_df["Price"].mean()
        avg_discount = month_df["Discount"].mean()
        avg_comp_price = month_df["Competitor Pricing"].mean()

        # Mode helpers
        def get_mode(values):
            vals = [v for v in values if pd.notna(v)]
            return Counter(vals).most_common(1)[0][0] if vals else None

        season_mode = get_mode(month_df["Seasonality"])
        weather_mode = get_mode(month_df["Weather Condition"])
        regions = sorted(month_df["Region"].dropna().unique())

        return {
            "Product ID": product_id,
            "Store ID": store_id or "All Stores",
            "Year": year,
            "Month": datetime(year, month, 1).strftime("%B"),
            "Product Name": month_df["Product Name"].iloc[0],
            "Category": month_df["Category"].iloc[0],
            "Regions": regions,
            "Inventory Level (Total)": round(total_inventory, 2),
            "Units Sold (Total)": round(total_sold, 2),
            "Units Ordered (Total)": round(total_ordered, 2),
            "Average Price": round(avg_price, 2),
            "Average Discount": round(avg_discount, 2),
            "Average Competitor Pricing": round(avg_comp_price, 2),
            "Most Common Weather Condition": weather_mode,
            "Most Common Seasonality": season_mode
        }

    except Exception as e:
        print(f"❌ Error fetching monthly context for {product_id}: {e}")
        return None


# ----------------------------------------------------------------
# Wrapper Function: supports optional month_name and store_id
# ----------------------------------------------------------------
# def get_product_context_with_month(product_id: str, month_name: str = "", store_id: str = ""):
#     """
#     Retrieves context for a product (and optional store) for a given month.
#     If month_name is omitted → use the latest month found in DB.
#     Returns both:
#         - current_month_data
#         - last_year_same_month_data
#     """

#     try:
#         engine = create_engine("sqlite:///data/db_files/inventory.db", echo=False)

#         # 1️⃣ Load all available dates for the product
#         with engine.connect() as conn:
#             df_dates = pd.read_sql_query(
#                 "SELECT [Product ID], Date FROM inventory WHERE [Product ID] = :pid",
#                 conn,
#                 params={"pid": product_id}
#             )

#         if df_dates.empty:
#             return {"error": f"No data found for Product {product_id}"}

#         df_dates["Date"] = pd.to_datetime(df_dates["Date"], errors="coerce")
#         df_dates = df_dates.dropna(subset=["Date"])
#         df_dates["Year"] = df_dates["Date"].dt.year
#         df_dates["Month"] = df_dates["Date"].dt.month

#         # 2️⃣ Determine month and year context
#         if month_name:
#             # Convert month name to number
#             month_map = {m.lower(): i for i, m in enumerate([
#                 "January", "February", "March", "April", "May", "June",
#                 "July", "August", "September", "October", "November", "December"
#             ], start=1)}
#             month_num = month_map.get(month_name.lower())
#             if not month_num:
#                 return {"error": f"Invalid month name '{month_name}'. Use full names (e.g., 'January')."}

#             latest_year = df_dates["Year"].max()
#         else:
#             # Use latest date available in DB
#             latest_row = df_dates.loc[df_dates["Date"].idxmax()]
#             latest_year = int(latest_row["Year"])
#             month_num = int(latest_row["Month"])
#             month_name = datetime(latest_year, month_num, 1).strftime("%B")

#         previous_year = latest_year - 1

#         # 3️⃣ Fetch current and previous year data
#         current_data = _fetch_context_for_month(engine, product_id, store_id, latest_year, month_num)
#         previous_data = _fetch_context_for_month(engine, product_id, store_id, previous_year, month_num)

#         # 4️⃣ Build comparative result
#         result = {
#             "Current Year Context": current_data or f"No data found for {month_name} {latest_year}.",
#             "Last Year Context": previous_data or f"No data found for {month_name} {previous_year}.",
#             "Parameters Used": {
#                 "Product ID": product_id,
#                 "Store ID": store_id or "All Stores",
#                 "Month": month_name,
#                 "Current Year": latest_year,
#                 "Comparison Year": previous_year
#             }
#         }

#         return result

#     except Exception as e:
#         print(f"❌ Error fetching product context for {product_id}: {e}")
#         return {"error": str(e)}

def get_product_context_with_month(product_id: str, month_name: str = "", store_id: str = ""):
    """
    Retrieves context for a product (and optional store) for a given month.
    If month_name is omitted → use the latest month found in DB.
    Returns both:
        - current_month_data
        - last_year_same_month_data
    """

    def convert_numpy_types(obj):
        """Recursively convert numpy scalar types to native Python types."""
        if isinstance(obj, dict):
            return {k: convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(x) for x in obj]
        elif isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        else:
            return obj

    try:
        engine = create_engine("sqlite:///data/db_files/inventory.db", echo=False)

        # 1️⃣ Load all available dates for the product
        with engine.connect() as conn:
            df_dates = pd.read_sql_query(
                "SELECT [Product ID], Date FROM inventory WHERE [Product ID] = :pid",
                conn,
                params={"pid": product_id}
            )

        if df_dates.empty:
            return {"error": f"No data found for Product {product_id}"}

        df_dates["Date"] = pd.to_datetime(df_dates["Date"], errors="coerce")
        df_dates = df_dates.dropna(subset=["Date"])
        df_dates["Year"] = df_dates["Date"].dt.year
        df_dates["Month"] = df_dates["Date"].dt.month

        # 2️⃣ Determine month and year context
        if month_name:
            month_map = {m.lower(): i for i, m in enumerate([
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ], start=1)}
            month_num = month_map.get(month_name.lower())
            if not month_num:
                return {"error": f"Invalid month name '{month_name}'. Use full names (e.g., 'January')."}
            latest_year = int(df_dates["Year"].max())
        else:
            latest_row = df_dates.loc[df_dates["Date"].idxmax()]
            latest_year = int(latest_row["Year"])
            month_num = int(latest_row["Month"])
            month_name = datetime(latest_year, month_num, 1).strftime("%B")

        previous_year = latest_year - 1

        # 3️⃣ Fetch current and previous year data
        current_data = _fetch_context_for_month(engine, product_id, store_id, latest_year, month_num)
        previous_data = _fetch_context_for_month(engine, product_id, store_id, previous_year, month_num)

        # 4️⃣ Build comparative result
        result = {
            "Current Year Context": current_data or f"No data found for {month_name} {latest_year}.",
            "Last Year Context": previous_data or f"No data found for {month_name} {previous_year}.",
            "Parameters Used": {
                "Product ID": product_id,
                "Store ID": store_id or "All Stores",
                "Month": month_name,
                "Current Year": latest_year,
                "Comparison Year": previous_year
            }
        }

        # 5️⃣ Convert all numpy types → native Python
        result = convert_numpy_types(result)
        return result

    except Exception as e:
        print(f"❌ Error fetching product context for {product_id}: {e}")
        return {"error": str(e)}



# def get_category_context(category: str, store_id: str = None):
#     """
#     Retrieves aggregated context data for a specific category.
#     - If store_id is provided → returns category metrics for that store.
#     - If not → returns overall category metrics across all stores.
#     - Aggregates data for the *latest month* available in the dataset.
#     """

#     try:
#         engine = create_engine("sqlite:///data/db_files/inventory.db", echo=False)

#         # Load all rows for that category
#         with engine.connect() as conn:
#             df = pd.read_sql_query(
#                 "SELECT * FROM inventory WHERE Category = :cat",
#                 conn,
#                 params={"cat": category}
#             )

#         if df.empty:
#             return {"error": f"No data found for category '{category}'"}

#         # Convert Date column to datetime for month grouping
#         df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
#         df = df.dropna(subset=["Date"])

#         # Identify latest month
#         latest_month = df["Date"].dt.to_period("M").max()
#         latest_month_df = df[df["Date"].dt.to_period("M") == latest_month]

#         # If store-specific, filter by store ID
#         if store_id:
#             store_df = latest_month_df[latest_month_df["Store ID"] == store_id]
#             if store_df.empty:
#                 return {"error": f"No data for category '{category}' in store '{store_id}' for {latest_month}"}

#             # Aggregate metrics
#             return {
#                 "Category": category,
#                 "Store ID": store_id,
#                 "Month": str(latest_month),
#                 "Total Products": store_df["Product ID"].nunique(),
#                 "Average Price": round(store_df["Price"].mean(), 2),
#                 "Average Discount": round(store_df["Discount"].mean(), 2),
#                 "Total Units Sold": int(store_df["Units Sold"].sum()),
#                 "Total Units Ordered": int(store_df["Units Ordered"].sum()),
#                 "Total Inventory": int(store_df["Inventory Level"].sum()),
#                 "Average Competitor Pricing": round(store_df["Competitor Pricing"].mean(), 2),
#                 "Most Common Weather Condition": store_df["Weather Condition"].mode().iat[0]
#                     if not store_df["Weather Condition"].mode().empty else None,
#                 "Most Common Seasonality": store_df["Seasonality"].mode().iat[0]
#                     if not store_df["Seasonality"].mode().empty else None,
#                 "Distinct Regions": sorted(store_df["Region"].unique())
#             }

#         # If no store ID → aggregate across all stores for that month
#         agg_df = latest_month_df.copy()

#         # Group by category (though here it’s single category)
#         return {
#             "Category": category,
#             "Month": str(latest_month),
#             "Total Stores": agg_df["Store ID"].nunique(),
#             "Total Products": agg_df["Product ID"].nunique(),
#             "Average Price": round(agg_df["Price"].mean(), 2),
#             "Average Discount": round(agg_df["Discount"].mean(), 2),
#             "Total Units Sold": int(agg_df["Units Sold"].sum()),
#             "Total Units Ordered": int(agg_df["Units Ordered"].sum()),
#             "Total Inventory": int(agg_df["Inventory Level"].sum()),
#             "Average Competitor Pricing": round(agg_df["Competitor Pricing"].mean(), 2),
#             "Most Common Weather Condition": agg_df["Weather Condition"].mode().iat[0]
#                 if not agg_df["Weather Condition"].mode().empty else None,
#             "Most Common Seasonality": agg_df["Seasonality"].mode().iat[0]
#                 if not agg_df["Seasonality"].mode().empty else None,
#             "Distinct Regions": sorted(agg_df["Region"].unique())
#         }

#     except Exception as e:
#         print(f"❌ Error fetching category context for {category}: {e}")
#         return {"error": str(e)}
    


# ------------------------------------------------------------
# Helper: fetch category data for a specific year & month
# ------------------------------------------------------------
def _fetch_category_context_for_month(engine, category: str, store_id: str, year: int, month: int):
    """Fetch aggregated context data for a given category, store, and year-month."""
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(
                "SELECT * FROM inventory WHERE Category = :cat",
                conn,
                params={"cat": category}
            )

        if df.empty:
            return None

        # Date normalization
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month

        month_df = df[(df["Year"] == year) & (df["Month"] == month)]
        if store_id:
            month_df = month_df[month_df["Store ID"] == store_id]

        if month_df.empty:
            return None

        # Aggregate metrics
        total_products = month_df["Product ID"].nunique()
        total_stores = month_df["Store ID"].nunique()
        total_units_sold = month_df["Units Sold"].sum()
        total_units_ordered = month_df["Units Ordered"].sum()
        total_inventory = month_df["Inventory Level"].sum()
        avg_price = month_df["Price"].mean()
        avg_discount = month_df["Discount"].mean()
        avg_comp_price = month_df["Competitor Pricing"].mean()

        # Mode helper
        def get_mode(values):
            vals = [v for v in values if pd.notna(v)]
            return Counter(vals).most_common(1)[0][0] if vals else None

        weather_mode = get_mode(month_df["Weather Condition"])
        season_mode = get_mode(month_df["Seasonality"])
        distinct_regions = sorted(month_df["Region"].dropna().unique())

        return {
            "Category": category,
            "Store ID": store_id or "All Stores",
            "Year": year,
            "Month": datetime(year, month, 1).strftime("%B"),
            "Total Stores": total_stores,
            "Total Products": total_products,
            "Average Price": round(avg_price, 2),
            "Average Discount": round(avg_discount, 2),
            "Total Units Sold": int(total_units_sold),
            "Total Units Ordered": int(total_units_ordered),
            "Total Inventory": int(total_inventory),
            "Average Competitor Pricing": round(avg_comp_price, 2),
            "Most Common Weather Condition": weather_mode,
            "Most Common Seasonality": season_mode,
            "Distinct Regions": distinct_regions
        }

    except Exception as e:
        print(f"❌ Error fetching category data for {category}, {year}-{month}: {e}")
        return None


# ------------------------------------------------------------
# Wrapper: adds date flexibility and YoY comparison
# ------------------------------------------------------------
# def get_category_context_with_month(category: str, month_name: str = "", store_id: str = ""):
#     """
#     Retrieves category-level context for a given (or latest) month and compares it
#     with the same month of the previous year.
#     - If store_id is provided → filters to that store.
#     - If month_name is omitted → uses the latest month available in DB.
#     Returns:
#         {
#           "Current Year Context": {...},
#           "Last Year Context": {...},
#           "Parameters Used": {...}
#         }
#     """

#     try:
#         engine = create_engine("sqlite:///data/db_files/inventory.db", echo=False)

#         # 1️⃣ Load all date info for the category
#         with engine.connect() as conn:
#             df_dates = pd.read_sql_query(
#                 "SELECT Category, Date FROM inventory WHERE Category = :cat",
#                 conn,
#                 params={"cat": category}
#             )

#         if df_dates.empty:
#             return {"error": f"No data found for category '{category}'."}

#         df_dates["Date"] = pd.to_datetime(df_dates["Date"], errors="coerce")
#         df_dates = df_dates.dropna(subset=["Date"])
#         df_dates["Year"] = df_dates["Date"].dt.year
#         df_dates["Month"] = df_dates["Date"].dt.month

#         # 2️⃣ Determine target month/year
#         if month_name:
#             # Convert month name to number
#             month_map = {m.lower(): i for i, m in enumerate([
#                 "January", "February", "March", "April", "May", "June",
#                 "July", "August", "September", "October", "November", "December"
#             ], start=1)}
#             month_num = month_map.get(month_name.lower())
#             if not month_num:
#                 return {"error": f"Invalid month name '{month_name}'. Use full names (e.g., 'January')."}

#             latest_year = df_dates["Year"].max()
#         else:
#             # Auto-detect latest available month and year
#             latest_row = df_dates.loc[df_dates["Date"].idxmax()]
#             latest_year = int(latest_row["Year"])
#             month_num = int(latest_row["Month"])
#             month_name = datetime(latest_year, month_num, 1).strftime("%B")

#         previous_year = latest_year - 1

#         # 3️⃣ Fetch both current and last year contexts
#         current_data = _fetch_category_context_for_month(engine, category, store_id, latest_year, month_num)
#         previous_data = _fetch_category_context_for_month(engine, category, store_id, previous_year, month_num)

#         # 4️⃣ Build the output structure
#         result = {
#             "Current Year Context": current_data or f"No data found for {month_name} {latest_year}.",
#             "Last Year Context": previous_data or f"No data found for {month_name} {previous_year}.",
#             "Parameters Used": {
#                 "Category": category,
#                 "Store ID": store_id or "All Stores",
#                 "Month": month_name,
#                 "Current Year": latest_year,
#                 "Comparison Year": previous_year
#             }
#         }

#         return result

#     except Exception as e:
#         print(f"❌ Error fetching category context for {category}: {e}")
#         return {"error": str(e)}



def get_category_context_with_month(category: str, month_name: str = "", store_id: str = ""):
    """
    Retrieves category-level context for a given (or latest) month and compares it
    with the same month of the previous year.
    - If store_id is provided → filters to that store.
    - If month_name is omitted → uses the latest month available in DB.
    """

    def convert_numpy_types(obj):
        """Recursively convert numpy scalar types to native Python types."""
        if isinstance(obj, dict):
            return {k: convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(x) for x in obj]
        elif isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        else:
            return obj

    try:
        engine = create_engine("sqlite:///data/db_files/inventory.db", echo=False)

        # 1️⃣ Load all date info for the category
        with engine.connect() as conn:
            df_dates = pd.read_sql_query(
                "SELECT Category, Date FROM inventory WHERE Category = :cat",
                conn,
                params={"cat": category}
            )

        if df_dates.empty:
            return {"error": f"No data found for category '{category}'."}

        df_dates["Date"] = pd.to_datetime(df_dates["Date"], errors="coerce")
        df_dates = df_dates.dropna(subset=["Date"])
        df_dates["Year"] = df_dates["Date"].dt.year
        df_dates["Month"] = df_dates["Date"].dt.month

        # 2️⃣ Determine target month/year
        if month_name:
            month_map = {m.lower(): i for i, m in enumerate([
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ], start=1)}
            month_num = month_map.get(month_name.lower())
            if not month_num:
                return {"error": f"Invalid month name '{month_name}'. Use full names (e.g., 'January')."}

            latest_year = int(df_dates["Year"].max())
        else:
            latest_row = df_dates.loc[df_dates["Date"].idxmax()]
            latest_year = int(latest_row["Year"])
            month_num = int(latest_row["Month"])
            month_name = datetime(latest_year, month_num, 1).strftime("%B")

        previous_year = latest_year - 1

        # 3️⃣ Fetch both current and last year contexts
        current_data = _fetch_category_context_for_month(engine, category, store_id, latest_year, month_num)
        previous_data = _fetch_category_context_for_month(engine, category, store_id, previous_year, month_num)

        # 4️⃣ Build the output structure
        result = {
            "Current Year Context": current_data or f"No data found for {month_name} {latest_year}.",
            "Last Year Context": previous_data or f"No data found for {month_name} {previous_year}.",
            "Parameters Used": {
                "Category": category,
                "Store ID": store_id or "All Stores",
                "Month": month_name,
                "Current Year": latest_year,
                "Comparison Year": previous_year
            }
        }

        # 5️⃣ Convert all numpy types → native Python
        result = convert_numpy_types(result)
        return result

    except Exception as e:
        print(f"❌ Error fetching category context for {category}: {e}")
        return {"error": str(e)}



# def get_overall_category_summary(store_id: str = None):
#     """
#     Gathers aggregated data for all categories for the latest month available.
#     - If store_id is provided → summarizes category performance for that store.
#     - If not → summarizes all categories across all stores.
#     Returns one summary row per category with totals and averages.
#     """

#     try:
#         engine = create_engine("sqlite:///data/db_files/inventory.db", echo=False)

#         with engine.connect() as conn:
#             df = pd.read_sql_query("SELECT * FROM inventory", conn)

#         if df.empty:
#             return {"error": "Inventory data is empty or table not found."}

#         # Convert and clean Date column
#         df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
#         df = df.dropna(subset=["Date"])

#         # Determine latest month in data
#         df["MonthPeriod"] = df["Date"].dt.to_period("M")
#         latest_month = df["MonthPeriod"].max()
#         latest_df = df[df["MonthPeriod"] == latest_month]

#         # If store filter provided
#         if store_id:
#             latest_df = latest_df[latest_df["Store ID"] == store_id]
#             if latest_df.empty:
#                 return {"error": f"No data found for Store {store_id} in {latest_month}"}

#         # Group by Category
#         grouped = latest_df.groupby("Category").agg({
#             "Product ID": "nunique",
#             "Store ID": "nunique",
#             "Units Sold": "sum",
#             "Units Ordered": "sum",
#             "Inventory Level": "sum",
#             "Price": "mean",
#             "Discount": "mean",
#             "Competitor Pricing": "mean"
#         }).reset_index()

#         # Rename columns for clarity
#         grouped.rename(columns={
#             "Product ID": "Unique Products",
#             "Store ID": "Stores Count",
#             "Units Sold": "Total Units Sold",
#             "Units Ordered": "Total Units Ordered",
#             "Inventory Level": "Total Inventory",
#             "Price": "Average Price",
#             "Discount": "Average Discount",
#             "Competitor Pricing": "Average Competitor Pricing"
#         }, inplace=True)

#         # Add top-level summary info
#         overall_summary = {
#             "Month": str(latest_month),
#             "Scope": f"Store {store_id}" if store_id else "All Stores Combined",
#             "Total Categories": len(grouped),
#             "Total Unique Products": int(df["Product ID"].nunique()),
#             "Overall Units Sold": int(latest_df["Units Sold"].sum()),
#             "Overall Units Ordered": int(latest_df["Units Ordered"].sum()),
#             "Overall Inventory": int(latest_df["Inventory Level"].sum()),
#             "Category Details": grouped.to_dict(orient="records")
#         }

#         return overall_summary

#     except Exception as e:
#         print(f"❌ Error computing overall category summary: {e}")
#         return {"error": str(e)}



# ----------------------------------------------------------------
# Helper: fetch summary for one month/year (optionally store-specific)
# ----------------------------------------------------------------
def _fetch_overall_summary_for_month(engine, store_id: str, year: int, month: int):
    """Fetches per-category summaries for a specific year and month, rounded to 2 decimals."""
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query("SELECT * FROM inventory", conn)

        if df.empty:
            return None

        # Date preprocessing
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month

        # Filter by month/year
        month_df = df[(df["Year"] == year) & (df["Month"] == month)]
        if store_id:
            month_df = month_df[month_df["Store ID"] == store_id]

        if month_df.empty:
            return None

        # Group by category
        grouped = month_df.groupby("Category").agg({
            "Product ID": "nunique",
            "Store ID": "nunique",
            "Units Sold": "sum",
            "Units Ordered": "sum",
            "Inventory Level": "sum",
            "Price": "mean",
            "Discount": "mean",
            "Competitor Pricing": "mean"
        }).reset_index()

        # Rename columns for clarity
        grouped.rename(columns={
            "Product ID": "Unique Products",
            "Store ID": "Stores Count",
            "Units Sold": "Total Units Sold",
            "Units Ordered": "Total Units Ordered",
            "Inventory Level": "Total Inventory",
            "Price": "Average Price",
            "Discount": "Average Discount",
            "Competitor Pricing": "Average Competitor Pricing"
        }, inplace=True)

        # Round numeric columns to 2 decimals
        numeric_cols = [
            "Total Units Sold", "Total Units Ordered", "Total Inventory",
            "Average Price", "Average Discount", "Average Competitor Pricing"
        ]
        for col in numeric_cols:
            grouped[col] = grouped[col].round(2)

        # Prepare summary
        summary = {
            "Year": year,
            "Month": datetime(year, month, 1).strftime("%B"),
            "Scope": f"Store {store_id}" if store_id else "All Stores Combined",
            "Total Categories": int(len(grouped)),
            "Total Unique Products": int(month_df["Product ID"].nunique()),
            "Overall Units Sold": round(float(month_df["Units Sold"].sum()), 2),
            "Overall Units Ordered": round(float(month_df["Units Ordered"].sum()), 2),
            "Overall Inventory": round(float(month_df["Inventory Level"].sum()), 2),
            "Category Details": grouped.to_dict(orient="records")
        }

        return summary

    except Exception as e:
        print(f"❌ Error fetching overall summary for {year}-{month}: {e}")
        return None


# ----------------------------------------------------------------
# Wrapper: date-aware, flexible, and year-over-year comparative
# ----------------------------------------------------------------
# def get_overall_category_summary(month_name: str = "", store_id: str = ""):
#     """
#     Gathers aggregated per-category data for a specified (or latest) month.
#     - If month_name is not given → uses latest available month in DB.
#     - If store_id is provided → filters summary to that store.
#     Returns:
#         {
#           "Current Year Summary": {...},
#           "Last Year Summary": {...},
#           "Parameters Used": {...}
#         }
#     """
#     try:
#         engine = create_engine("sqlite:///data/db_files/inventory.db", echo=False)

#         # 1️⃣ Load date info
#         with engine.connect() as conn:
#             df_dates = pd.read_sql_query("SELECT Date FROM inventory", conn)

#         if df_dates.empty:
#             return {"error": "No inventory data found in the database."}

#         df_dates["Date"] = pd.to_datetime(df_dates["Date"], errors="coerce")
#         df_dates = df_dates.dropna(subset=["Date"])
#         df_dates["Year"] = df_dates["Date"].dt.year
#         df_dates["Month"] = df_dates["Date"].dt.month

#         # 2️⃣ Determine month/year for current & comparison
#         if month_name:
#             month_map = {m.lower(): i for i, m in enumerate([
#                 "January", "February", "March", "April", "May", "June",
#                 "July", "August", "September", "October", "November", "December"
#             ], start=1)}
#             month_num = month_map.get(month_name.lower())
#             if not month_num:
#                 return {"error": f"Invalid month name '{month_name}'. Use full names (e.g., 'January')."}

#             latest_year = df_dates["Year"].max()
#         else:
#             latest_row = df_dates.loc[df_dates["Date"].idxmax()]
#             latest_year = int(latest_row["Year"])
#             month_num = int(latest_row["Month"])
#             month_name = datetime(latest_year, month_num, 1).strftime("%B")

#         previous_year = latest_year - 1

#         # 3️⃣ Fetch summaries
#         current_summary = _fetch_overall_summary_for_month(engine, store_id, latest_year, month_num)
#         last_year_summary = _fetch_overall_summary_for_month(engine, store_id, previous_year, month_num)

#         # 4️⃣ Return structured comparison
#         result = {
#             "Current Year Summary": current_summary or f"No data found for {month_name} {latest_year}.",
#             "Last Year Summary": last_year_summary or f"No data found for {month_name} {previous_year}.",
#             "Parameters Used": {
#                 "Month": month_name,
#                 "Current Year": latest_year,
#                 "Comparison Year": previous_year,
#                 "Store ID": store_id or "All Stores"
#             }
#         }

#         return result

#     except Exception as e:
#         print(f"❌ Error computing overall category summary: {e}")
#         return {"error": str(e)}
    

def get_overall_category_summary(month_name: str = "", store_id: str = ""):
    """
    Gathers aggregated per-category data for a specified (or latest) month.
    - If month_name is not given → uses latest available month in DB.
    - If store_id is provided → filters summary to that store.
    """

    def convert_numpy_types(obj):
        """Recursively convert numpy scalar types to native Python types."""
        if isinstance(obj, dict):
            return {k: convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(x) for x in obj]
        elif isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        else:
            return obj

    try:
        engine = create_engine("sqlite:///data/db_files/inventory.db", echo=False)

        # 1️⃣ Load date info
        with engine.connect() as conn:
            df_dates = pd.read_sql_query("SELECT Date FROM inventory", conn)

        if df_dates.empty:
            return {"error": "No inventory data found in the database."}

        df_dates["Date"] = pd.to_datetime(df_dates["Date"], errors="coerce")
        df_dates = df_dates.dropna(subset=["Date"])
        df_dates["Year"] = df_dates["Date"].dt.year
        df_dates["Month"] = df_dates["Date"].dt.month

        # 2️⃣ Determine month/year for current & comparison
        if month_name:
            month_map = {m.lower(): i for i, m in enumerate([
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ], start=1)}
            month_num = month_map.get(month_name.lower())
            if not month_num:
                return {"error": f"Invalid month name '{month_name}'. Use full names (e.g., 'January')."}

            latest_year = int(df_dates["Year"].max())
        else:
            latest_row = df_dates.loc[df_dates["Date"].idxmax()]
            latest_year = int(latest_row["Year"])
            month_num = int(latest_row["Month"])
            month_name = datetime(latest_year, month_num, 1).strftime("%B")

        previous_year = latest_year - 1

        # 3️⃣ Fetch summaries
        current_summary = _fetch_overall_summary_for_month(engine, store_id, latest_year, month_num)
        last_year_summary = _fetch_overall_summary_for_month(engine, store_id, previous_year, month_num)

        # 4️⃣ Build result
        result = {
            "Current Year Summary": current_summary or f"No data found for {month_name} {latest_year}.",
            "Last Year Summary": last_year_summary or f"No data found for {month_name} {previous_year}.",
            "Parameters Used": {
                "Month": month_name,
                "Current Year": latest_year,
                "Comparison Year": previous_year,
                "Store ID": store_id or "All Stores"
            }
        }

        # 5️⃣ Convert NumPy types → native Python
        result = convert_numpy_types(result)
        return result

    except Exception as e:
        print(f"❌ Error computing overall category summary: {e}")
        return {"error": str(e)}


# # Wrap each of your Python functions as ADK tools
# get_product_context_tool = FunctionTool(
#     func=get_product_context_with_month,
#     name="get_product_context",
#     description="Fetches contextual data for a product (optionally by month or store) and compares with previous year."
# )

# get_category_context_tool = FunctionTool(
#     func=get_category_context_with_month,
#     name="get_category_context",
#     description="Fetches aggregated category-level context for a month and compares with the same month last year."
# )

# get_overall_summary_tool = FunctionTool(
#     func=get_overall_category_summary,
#     name="get_overall_summary",
#     description="Provides overall category performance summary for a given month and compares with previous year."
# )


# query_inventory_tool = FunctionTool(
#     func=query_inventory,
#     name="query_inventory",
#     description="Fetches full inventory record for a given Product ID from the local SQLite database (simulated RDS)."
# )
    

# rag_offer_tool = FunctionTool(
#     func=query_promotional_offers,
#     name="query_promotional_offers",
#     description="Retrieves relevant promotional offers from a RAG index (Pinecone + LlamaIndex)."
# )