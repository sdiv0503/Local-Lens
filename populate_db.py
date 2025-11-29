import pandas as pd
from faker import Faker
import random
from db import init_connection # <--- NEW IMPORT

def create_stores(cursor):
    """Creates 5 fake stores and inserts them into the 'stores' table."""
    fake = Faker()
    store_ids = []
    print("Creating stores...")
    
    for _ in range(5):
        name = fake.company() + " Foods"
        address = fake.address()
        
        sql = "INSERT INTO stores (name, address) VALUES (%s, %s) RETURNING store_id;"
        cursor.execute(sql, (name, address))
        
        store_id = cursor.fetchone()[0]
        store_ids.append(store_id)
        
    print(f"Created 5 stores with IDs: {store_ids}")
    return store_ids

def populate_products(cursor):
    """Reads products.csv and inserts them into the 'products' table."""
    try:
        df = pd.read_csv("products.csv")
    except FileNotFoundError:
        print("Error: products.csv not found. Run scrape_products.py first.")
        return None
        
    product_ids = []
    print(f"Populating {len(df)} products...")
    
    for index, row in df.iterrows():
        sql = "INSERT INTO products (name, category) VALUES (%s, %s) RETURNING product_id;"
        cursor.execute(sql, (row['name'], row['category']))
        
        product_id = cursor.fetchone()[0]
        product_ids.append(product_id)
        
    print(f"Populated {len(product_ids)} products.")
    return product_ids

def simulate_inventory(cursor, store_ids, product_ids):
    """Creates fake inventory data for every store and every product."""
    print("Simulating inventory...")
    inventory_count = 0
    
    for store_id in store_ids:
        for product_id in product_ids:
            # Generate stock between 50 (Critical) and 1200 (Plenty)
            if random.random() < 0.05:
                stock_quantity = 0
            else:
                stock_quantity = random.randint(50, 1200)
                
            price = round(random.uniform(0.99, 24.99), 2)
            
            sql = """
            INSERT INTO inventory (store_id, product_id, stock_quantity, price)
            VALUES (%s, %s, %s, %s);
            """
            cursor.execute(sql, (store_id, product_id, stock_quantity, price))
            inventory_count += 1
            
    print(f"Simulated {inventory_count} inventory records.")


def main():
    # --- UPDATED CONNECTION LOGIC ---
    conn = init_connection()
    if conn is None:
        return
        
    cursor = conn.cursor()
    
    try:
        store_ids = create_stores(cursor)
        product_ids = populate_products(cursor)
        
        if product_ids:
            simulate_inventory(cursor, store_ids, product_ids)
        
        conn.commit()
        print("All data successfully committed to the database!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()