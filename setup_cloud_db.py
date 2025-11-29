import psycopg2
from db import init_connection

def create_tables():
    print("Connecting to Cloud Database...")
    conn = init_connection()
    
    if conn is None:
        print("Failed to connect.")
        return

    cursor = conn.cursor()
    
    print("Creating tables...")
    
    # This SQL matches your original schema.sql
    schema_sql = """
    DROP TABLE IF EXISTS inventory CASCADE;
    DROP TABLE IF EXISTS products CASCADE;
    DROP TABLE IF EXISTS stores CASCADE;
    
    CREATE TABLE stores (
        store_id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        address VARCHAR(255)
    );
    
    CREATE TABLE products (
        product_id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        category VARCHAR(100)
    );
    
    CREATE TABLE inventory (
        inventory_id SERIAL PRIMARY KEY,
        store_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        stock_quantity INTEGER DEFAULT 0,
        price DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(store_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        UNIQUE(store_id, product_id)
    );
    """
    
    try:
        cursor.execute(schema_sql)
        conn.commit()
        print("✅ Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_tables()