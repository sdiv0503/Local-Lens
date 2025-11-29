import streamlit as st
import pandas as pd
from db import init_connection, run_query, run_transaction, get_product_list, get_store_list

st.set_page_config(page_title="My Stock", page_icon="📦", layout="wide")

# --- Sidebar Store Selection ---
stores = get_store_list()
store_opts = dict(zip(stores['store_id'], stores['name']))
if 'my_store_id' not in st.session_state:
    st.session_state['my_store_id'] = stores.iloc[0]['store_id']
selected_store_id = st.sidebar.selectbox("Manage Store:", options=store_opts.keys(), format_func=lambda x: store_opts[x], key='my_store_id_stock')

st.title("📦 Stock Room")

# --- TABBED INTERFACE ---
tab_view, tab_add = st.tabs(["👁️ View Stock", "➕ Add New Shipment"])

# --- TAB 1: VIEW STOCK (The read-only view) ---
with tab_view:
    # Load data for THIS store only
    query = """
        SELECT p.name as "Product", p.category as "Category", i.stock_quantity as "Qty", i.price as "Price"
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
        WHERE i.store_id = %(sid)s
        ORDER BY i.stock_quantity ASC
    """
    df = run_query(query, {"sid": selected_store_id})
    
    # Filter
    cat_filter = st.selectbox("Filter Category:", ["All"] + list(df['Category'].unique()))
    if cat_filter != "All":
        df = df[df['Category'] == cat_filter]
        
    # Styling
    def highlight_low(val):
        return 'background-color: #ffcccc' if val < 20 else ''

    st.dataframe(
        df.style.map(highlight_low, subset=['Qty']),
        use_container_width=True,
        hide_index=True,
        column_config={"Price": st.column_config.NumberColumn(format="₹%.2f")}
    )

# --- TAB 2: ADD STOCK (The Write Feature) ---
with tab_add:
    st.header("Receive Shipment")
    st.markdown("Use this when a delivery truck arrives to add items to your shelf.")
    
    with st.form("add_stock_form"):
        products = get_product_list()
        p_opts = {row['product_id']: row['name'] for i, row in products.iterrows()}
        
        c1, c2 = st.columns(2)
        pid_to_add = c1.selectbox("Select Product Received:", options=p_opts.keys(), format_func=lambda x: p_opts[x])
        qty_to_add = c2.number_input("Quantity Received:", min_value=1, step=1)
        
        submitted = st.form_submit_button("✅ Update Inventory")
        
        if submitted:
            # Update Query
            q = "UPDATE inventory SET stock_quantity = stock_quantity + %s WHERE product_id = %s AND store_id = %s"
            success = run_transaction(q, (qty_to_add, pid_to_add, selected_store_id))
            
            if success:
                st.success(f"Added {qty_to_add} units to {p_opts[pid_to_add]}!")
                st.cache_data.clear() # Clear cache so "View Stock" updates immediately
            else:
                st.error("Update failed.")