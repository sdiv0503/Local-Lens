import streamlit as st
import pandas as pd
import numpy as np
import json
from prophet import Prophet
from prophet.serialize import model_from_json
import psycopg2
from db import init_connection

# --- Page Config ---
st.set_page_config(page_title="LocalLens Triage", page_icon="🏠", layout="wide")

# --- Helper Functions ---
@st.cache_resource
def load_static_data(_conn):
    """Loads products, stores, and trend map in one go."""
    products = pd.read_sql("SELECT product_id, name FROM products ORDER BY name", _conn)
    stores = pd.read_sql("SELECT store_id, name FROM stores ORDER BY name", _conn)
    trends = pd.read_sql("SELECT product_id, keyword FROM product_trend_mapping", _conn)
    trend_map = dict(zip(trends['product_id'], trends['keyword']))
    return products, stores, trend_map

@st.cache_data(show_spinner=False)
def get_current_stock(_conn, store_id):
    if store_id == "ALL_STORES":
        query = "SELECT product_id, SUM(stock_quantity) as total_stock FROM inventory GROUP BY product_id"
        params = {}
    else:
        query = "SELECT product_id, stock_quantity as total_stock FROM inventory WHERE store_id = %(store_id)s"
        params = {"store_id": store_id}
    df = pd.read_sql(query, _conn, params=params)
    return dict(zip(df['product_id'], df['total_stock']))

@st.cache_resource(show_spinner=False)
def load_prophet_model(product_id):
    try:
        # --- UPDATE: Look in the 'models/' folder ---
        with open(f"models/demand_model_product_{product_id}.json", 'r') as f:
            return model_from_json(f.read())
    except:
        return None

def generate_future_trend(future_dates, keyword):
    # (Simplified seasonality logic)
    day_of_year = future_dates['ds'].dt.dayofyear
    base = 20
    noise = np.random.normal(0, 3, len(future_dates))
    seasonality = (np.sin(2 * np.pi * (day_of_year - 90) / 365.25) + 1) * 10
    if keyword in ['Turkey Breast', 'Cranberry Sauce', 'Ground Turkey']:
        seasonality = (np.sin(2 * np.pi * (day_of_year - 320) / 365.25) + 1) * 35 
    return np.clip(base + seasonality + noise, 0, 100).astype(int)

@st.cache_data(show_spinner=False)
def run_all_forecasts(_product_list, _trend_map, _stock_map, store_id):
    """Runs forecasts and returns results AND the cache."""
    triage_results = []
    forecast_cache = {} 
    
    for _, product in _product_list.iterrows():
        pid, pname = product['product_id'], product['name']
        model = load_prophet_model(pid)
        if not model: continue

        future = model.make_future_dataframe(periods=14, freq='D')
        future['on_sale'] = 0
        if pid in _trend_map:
            future['interest'] = generate_future_trend(future, _trend_map[pid])
        
        forecast = model.predict(future)
        forecast_cache[pid] = forecast 
        
        raw_demand = int(forecast.iloc[-14:]['yhat'].sum())
        final_demand = raw_demand if store_id == "ALL_STORES" else int(raw_demand / 5)
        stock = _stock_map.get(pid, 0)
        
        triage_results.append({
            "product_id": pid,
            "product_name": pname,
            "current_stock": stock,
            "forecasted_demand": final_demand,
            "shortfall": max(0, final_demand - stock)
        })

    return pd.DataFrame(triage_results), forecast_cache

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- MAIN UI ---
st.title("🏠 My Shop Dashboard") 
conn = init_connection()

if conn:
    products, stores, trend_map = load_static_data(conn)
    
    # Sidebar
    st.sidebar.title("Global Controls")
    store_opts = {"ALL_STORES": "All Stores (Aggregated)"}
    # Using dictionary comprehension to ensure unique store names in the dropdown
    store_opts.update(dict(zip(stores['store_id'], stores['name'])))
    
    if 'selected_store_id' not in st.session_state:
        st.session_state['selected_store_id'] = "ALL_STORES"
    
    sel_store_id = st.sidebar.selectbox("Select Store:", options=store_opts.keys(), format_func=lambda x: store_opts[x], key='selected_store_id')
    
    # Run Logic
    stock_map = get_current_stock(conn, sel_store_id)
    
    if 'triage_df' not in st.session_state or st.session_state.get('last_store') != sel_store_id:
        with st.spinner(f"Running fresh forecasts for {store_opts[sel_store_id]}..."):
            triage_df, forecast_cache = run_all_forecasts(products, trend_map, stock_map, sel_store_id)
            
            st.session_state['triage_df'] = triage_df
            st.session_state['forecast_cache'] = forecast_cache
            st.session_state['products_df'] = products
            st.session_state['last_store'] = sel_store_id
    else:
        triage_df = st.session_state['triage_df']

    # Display Triage
    st.header("🔥 Priority Restock List")
    st.markdown("Items projected to sell out in the next 14 days.")
    
    if not triage_df.empty:
        restock = triage_df[triage_df['shortfall'] > 0].sort_values('shortfall', ascending=False)
        
        if restock.empty:
            st.success("✅ Stock levels look good! No immediate action needed.")
        else:
            # Purchase Order Generator
            restock['Select'] = False
            restock = restock[['Select', 'product_name', 'current_stock', 'forecasted_demand', 'shortfall']]
            
            edited_df = st.data_editor(
                restock,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "product_name": "Product",
                    "current_stock": "In Stock",
                    "forecasted_demand": "Needed (14 Days)",
                    "shortfall": st.column_config.ProgressColumn("Shortage", format="%d", min_value=0, max_value=int(restock['shortfall'].max())),
                },
                key="po_editor"
            )
            
            # Logic to generate CSV from selected items
            selected = edited_df[edited_df.Select]
            if not selected.empty:
                st.subheader("Generate Purchase Order")
                csv = convert_df_to_csv(selected)
                st.download_button("Download PO CSV", csv, "purchase_order.csv", "text/csv")
    else:
        st.warning("No forecast data generated. Check database connections.")