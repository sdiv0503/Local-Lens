import pandas as pd
import numpy as np
import psycopg2
import psycopg2.extras 
from db import init_connection # We'll re-use our connection function!
import random
from io import StringIO

print("Starting smart sales simulation...")

product_trend_map = [] 

# --- 1. Load Data ---
try:
    # Read the CSV and tell pandas the date format
    trends_df = pd.read_csv("google_trends_data.csv")
    trends_df['date'] = pd.to_datetime(trends_df['date'])
    
    trends_df = trends_df.set_index('date')
    print("Loaded google_trends_data.csv")
except FileNotFoundError:
    print("Error: 'google_trends_data.csv' not found. Run get_trends.py first.")
    exit()

# We also need our product list from the database
conn = init_connection()
if conn is None:
    print("Error: Could not connect to database.")
    exit()

print("Fetching product and store lists from database...")
products_df = pd.read_sql("SELECT product_id, name FROM products", conn)
stores_df = pd.read_sql("SELECT store_id FROM stores", conn)

# --- DEBUGGING CHECK ---
print(f"DEBUG: Found {len(products_df)} products and {len(stores_df)} stores.")

if products_df.empty or stores_df.empty:
    print("Error: Products or Stores table is empty! Did you run populate_db.py?")
    exit()
# ---------------------

# --- 2. Create Date Range ---
start_date = trends_df.index.min()
end_date = trends_df.index.max()
dates = pd.date_range(start=start_date, end=end_date, freq='D')

print(f"Generating sales data from {start_date} to {end_date}...")

all_sales_data = []

# --- 3. Run the Simulation Loop ---
for store_id in stores_df['store_id']:
    print(f"Simulating for Store ID: {store_id}")

    for index, product in products_df.iterrows():
        product_id = product['product_id']
        product_name = product['name']

        # --- This is the "Smart" Part ---

        # 1. Set a random base sale
        base_sales = random.randint(5, 50)

        # 2. Add seasonality
        days_in_year = 365.25
        day_of_year = dates.dayofyear.values
        seasonality = (np.sin(2 * np.pi * (day_of_year - 90) / days_in_year) + 1) * 10

        # 3. Add Google Trend influence
        matching_keyword = None
        for keyword in trends_df['keyword'].unique():
            if all(word.lower() in product_name.lower() for word in keyword.lower().split()):
                matching_keyword = keyword
                break

        trend_influence = 0
        if matching_keyword:
            product_trend_map.append((product_id, matching_keyword))
            
            product_trend = trends_df[trends_df['keyword'] == matching_keyword]['interest']
            daily_trend = product_trend.resample('D').ffill().reindex(dates, method='ffill')
            trend_influence = (daily_trend / 100) * base_sales * 3 

        # 4. Add "On Sale" influence
        on_sale = np.random.choice([0, 1], size=len(dates), p=[0.9, 0.1])
        promo_influence = on_sale * base_sales * 1.5 

        # 5. Add random noise
        noise = np.random.normal(0, 3, size=len(dates))

        # --- 6. Calculate Final Sales ---
        simulated_sales = base_sales + seasonality + trend_influence + promo_influence + noise
        simulated_sales[simulated_sales < 0] = 0
        simulated_sales = np.round(simulated_sales).astype(int)

        # --- 7. Format for DB ---
        sales_df = pd.DataFrame({
            'sale_date': dates,
            'store_id': store_id,
            'product_id': product_id,
            'quantity_sold': simulated_sales,
            'on_sale': on_sale 
        })

        all_sales_data.append(sales_df)

# --- 6. Combine and Save ---
if not all_sales_data:
    print("Error: No sales data generated. Loop did not run correctly.")
    exit()

final_sales_history_df = pd.concat(all_sales_data, ignore_index=True)

print("\n--- Simulation Complete ---")
print(f"Generated {len(final_sales_history_df)} total sales records.")

final_sales_history_df.to_csv("sales_history.csv", index=False)
print("Saved full history to 'sales_history.csv'")

# --- 7. Load to Database ---
print("Loading new data into PostgreSQL...")
cursor = conn.cursor()

# Create the new tables
cursor.execute("""
    DROP TABLE IF EXISTS sales_history;
    DROP TABLE IF EXISTS trend_data;
    DROP TABLE IF EXISTS product_trend_mapping;

    CREATE TABLE trend_data (
        trend_id SERIAL PRIMARY KEY,
        date DATE NOT NULL,
        interest INTEGER NOT NULL,
        keyword VARCHAR(255) NOT NULL
    );

    CREATE TABLE sales_history (
        sale_id SERIAL PRIMARY KEY,
        sale_date DATE NOT NULL,
        store_id INTEGER REFERENCES stores(store_id),
        product_id INTEGER REFERENCES products(product_id),
        quantity_sold INTEGER NOT NULL,
        on_sale INTEGER NOT NULL DEFAULT 0 
    );
    
    CREATE TABLE product_trend_mapping (
        product_id INTEGER REFERENCES products(product_id),
        keyword VARCHAR(255) NOT NULL,
        PRIMARY KEY (product_id, keyword)
    );
""")
print("Created 'trend_data', 'sales_history', and 'product_trend_mapping' tables.")

# Load mappings
if product_trend_map:
    unique_mappings = list(set(product_trend_map))
    print(f"Loading {len(unique_mappings)} unique product-trend mappings into database...")
    
    insert_query = "INSERT INTO product_trend_mapping (product_id, keyword) VALUES %s"
    psycopg2.extras.execute_values(
        cursor,
        insert_query,
        unique_mappings
    )
    print("Loaded 'product_trend_mapping' data.")
else:
    print("No product-trend mappings found to load.")


# Load trends
with open('google_trends_data.csv', 'r', encoding='utf-8') as f:
    next(f)
    trends_for_db = f.read().replace('T00:00:00.000Z', '').replace(' 00:00:00', '')
    trends_io = StringIO(trends_for_db)
    cursor.copy_from(trends_io, 'trend_data', sep=',', columns=('date', 'interest', 'keyword'))
print("Loaded 'google_trends_data.csv' into database.")

# Load sales
with open('sales_history.csv', 'r', encoding='utf-8') as f:
    next(f)
    cursor.copy_from(f, 'sales_history', sep=',', columns=('sale_date', 'store_id', 'product_id', 'quantity_sold', 'on_sale'))
print("Loaded 'sales_history.csv' into database.")

conn.commit()
cursor.close()
conn.close()

print("\n--- All Data Loaded to Database! ---")