import pandas as pd
import numpy as np
import psycopg2
from prophet import Prophet
from prophet.serialize import model_to_json
from prophet.plot import plot_plotly, plot_components_plotly 
import plotly.io as pio
from db import init_connection
import os # <--- NEW IMPORT

# Create the models directory if it doesn't exist
if not os.path.exists('models'):
    os.makedirs('models')

def load_training_data(conn, product_id, keyword=None):
    """Loads training data (Sales + Trends)."""
    sql_sales = """
        SELECT sale_date AS ds, SUM(quantity_sold) AS y, MAX(on_sale) AS on_sale
        FROM sales_history
        WHERE product_id = %(product_id)s
        GROUP BY sale_date ORDER BY ds;
    """
    
    try:
        sales_df = pd.read_sql(sql_sales, conn, params={"product_id": product_id})
        if sales_df.empty: return None
            
        sales_df['ds'] = pd.to_datetime(sales_df['ds'])
        sales_df = sales_df.set_index('ds')

        if keyword:
            sql_trend = "SELECT date, interest FROM trend_data WHERE keyword = %(keyword)s ORDER BY date;"
            trend_df = pd.read_sql(sql_trend, conn, params={"keyword": keyword})
            if trend_df.empty: return sales_df.reset_index()

            trend_df['date'] = pd.to_datetime(trend_df['date'])
            trend_df = trend_df.set_index('date')
            daily_trend_df = trend_df.resample('D').ffill()
            train_df = sales_df.join(daily_trend_df).dropna().reset_index()
        else:
            train_df = sales_df.reset_index()
        
        return train_df if not train_df.empty else None

    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def generate_future_trend(future_dates, keyword):
    """Generates synthetic future trend."""
    day_of_year = future_dates['ds'].dt.dayofyear
    base = 20
    noise = np.random.normal(0, 3, len(future_dates))
    
    if keyword in ['Avocado', 'Oat Milk', 'Quinoa', 'Greek Yogurt', 'Sourdough Bread', 'Almond Flour']:
        trend_line = np.linspace(40, 45, len(future_dates))
        seasonality = (np.sin(2 * np.pi * (day_of_year - 90) / 365.25) + 1) * 5
        future_trend = base + trend_line + seasonality + noise
    elif keyword in ['Vanilla Ice Cream', 'Barbecue Sauce', 'Hot Sauce', 'Hamburger Buns', 'Watermelon']:
        seasonality = (np.sin(2 * np.pi * (day_of_year - 180) / 365.25) + 1) * 30
        future_trend = base + seasonality + noise
    elif keyword in ['Turkey Breast', 'Cranberry Sauce', 'Sweet Potato', 'Pumpkin Spice', 'Ground Turkey']:
        seasonality = (np.sin(2 * np.pi * (day_of_year - 320) / 365.25) + 1) * 35 
        future_trend = base + seasonality + noise
    elif keyword == 'Cocoa Powder':
        seasonality = (-np.sin(2 * np.pi * (day_of_year - 180) / 365.25) + 1) * 20
        future_trend = base + seasonality + noise
    else:
        seasonality = (np.sin(2 * np.pi * (day_of_year - 90) / 365.25) + 1) * 10
        future_trend = base + seasonality + noise
    
    return np.clip(future_trend, 0, 100).astype(int)

def main():
    conn = init_connection()
    if conn is None: return

    print("Loading product list and trend map...")
    products = pd.read_sql("SELECT product_id, name FROM products", conn)
    trend_map_df = pd.read_sql("SELECT product_id, keyword FROM product_trend_mapping", conn)
    trend_map = dict(zip(trend_map_df['product_id'], trend_map_df['keyword']))
    
    models_trained = 0
    
    for index, product in products.iterrows():
        pid, pname = product['product_id'], product['name']
        print(f"Training: {pname}...")

        keyword = trend_map.get(pid)
        train_df = load_training_data(conn, pid, keyword)

        if train_df is None: continue

        model = Prophet()
        model.add_country_holidays(country_name='IN') # Feature Engineering
        model.add_regressor('on_sale') # Feature Engineering
        if keyword: model.add_regressor('interest')
            
        try:
            model.fit(train_df)
            
            # Save to 'models/' folder
            model_filename = f"models/demand_model_product_{pid}.json" # <--- UPDATED PATH
            with open(model_filename, 'w') as f:
                f.write(model_to_json(model))
            models_trained += 1
        except Exception as e:
            print(f"Failed to train {pname}: {e}")

    conn.close()
    print(f"\n--- Complete! Trained {models_trained} models in 'models/' folder. ---")

if __name__ == "__main__":
    main()