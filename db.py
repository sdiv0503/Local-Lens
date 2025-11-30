import psycopg2
import streamlit as st

@st.cache_resource
def init_connection():
    try:
        # DEBUGGING: Print what keys exist in secrets
        print("Available Secret Keys:", st.secrets.keys())

        # Check if "postgres" section exists
        if "postgres" in st.secrets:
            print("Found [postgres] section in secrets. Connecting to Cloud...")
            return psycopg2.connect(
                dbname=st.secrets["postgres"]["dbname"],
                user=st.secrets["postgres"]["user"],
                password=st.secrets["postgres"]["password"],
                host=st.secrets["postgres"]["host"],
                port=st.secrets["postgres"]["port"]
            )
        else:
            print("⚠️ [postgres] section NOT found. Falling back to Localhost...")
            return psycopg2.connect(
                dbname="local_lens_db", 
                user="postgres", 
                password="postgre", 
                host="localhost", 
                port="5432"
            )
    except Exception as e:
        print(f"DB Connection failed: {e}")
        st.error(f"DB Connection failed: {e}")
        return None

def run_query(query, params=None):
    conn = init_connection()
    if conn:
        try:
            import pandas as pd
            return pd.read_sql(query, conn, params=params)
        except Exception as e:
            st.error(f"Query failed: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def run_transaction(query, params):
    conn = init_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            st.error(f"Transaction failed: {e}")
            return False
    return False

# --- Data Loaders ---
@st.cache_data(ttl=60)
def get_product_list():
    return run_query("SELECT product_id, name, category FROM products ORDER BY name")

@st.cache_data(ttl=60)
def get_store_list():
    return run_query("SELECT store_id, name FROM stores ORDER BY name")