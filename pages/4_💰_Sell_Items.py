import streamlit as st
import pandas as pd
from db import init_connection, run_query, run_transaction, get_product_list, get_store_list
from datetime import datetime

st.set_page_config(page_title="Digital Register", page_icon="💰", layout="wide")

# --- 1. Session State for Cart ---
if 'cart' not in st.session_state:
    st.session_state['cart'] = []

# --- 2. Sidebar: Select Store (The "Login") ---
st.sidebar.title("🏪 Shop Settings")
stores = get_store_list()
store_opts = dict(zip(stores['store_id'], stores['name']))

# Default to first store or keep selection
if 'my_store_id' not in st.session_state:
    st.session_state['my_store_id'] = stores.iloc[0]['store_id']

selected_store_id = st.sidebar.selectbox(
    "Active Store:", 
    options=store_opts.keys(), 
    format_func=lambda x: store_opts[x],
    key='my_store_id'
)

st.title("💰 Digital Register")
st.markdown(f"**Selling from:** {store_opts[selected_store_id]}")

# --- 3. The "Add to Cart" Section ---
col1, col2 = st.columns([2, 1])

with col1:
    products = get_product_list()
    # Create a nice dropdown list "Apple (Produce)"
    product_opts = {row['product_id']: f"{row['name']} ({row['category']})" for i, row in products.iterrows()}
    
    selected_product_id = st.selectbox("🔍 Search Item:", options=product_opts.keys(), format_func=lambda x: product_opts[x])

with col2:
    qty = st.number_input("Quantity:", min_value=1, value=1, step=1)

# Add Button
if st.button("➕ Add to Bill", use_container_width=True):
    # Get Price
    price_df = run_query(
        "SELECT price, stock_quantity FROM inventory WHERE product_id = %(pid)s AND store_id = %(sid)s", 
        {"pid": selected_product_id, "sid": selected_store_id}
    )
    
    if not price_df.empty:
        price = price_df.iloc[0]['price']
        current_stock = price_df.iloc[0]['stock_quantity']
        
        if current_stock >= qty:
            # Add to session state cart
            item_name = product_opts[selected_product_id].split(' (')[0]
            st.session_state['cart'].append({
                "id": selected_product_id,
                "name": item_name,
                "qty": qty,
                "price": price,
                "total": qty * price
            })
            st.success(f"Added {qty} x {item_name}")
        else:
            st.error(f"❌ Not enough stock! Only {current_stock} available.")
    else:
        st.error("Item not found in this store's inventory.")

st.divider()

# --- 4. The Cart & Checkout ---
if st.session_state['cart']:
    st.subheader("🛒 Current Bill")
    cart_df = pd.DataFrame(st.session_state['cart'])
    st.dataframe(
        cart_df[['name', 'qty', 'price', 'total']], 
        use_container_width=True,
        column_config={
            "price": st.column_config.NumberColumn("Price", format="₹%.2f"),
            "total": st.column_config.NumberColumn("Total", format="₹%.2f")
        }
    )
    
    grand_total = cart_df['total'].sum()
    st.markdown(f"### 💵 Total to Collect: **₹{grand_total:,.2f}**")
    
    # Payment Mode (Real World Feature)
    payment_mode = st.radio("Payment Mode:", ["Cash", "UPI / QR Code", "Credit (Udhaar)"], horizontal=True)
    
    col_pay, col_clear = st.columns([3, 1])
    
    with col_pay:
        if st.button("✅ Complete Sale", type="primary", use_container_width=True):
            # 1. Update DB for each item
            success = True
            for item in st.session_state['cart']:
                # Update Inventory (Subtract)
                q1 = "UPDATE inventory SET stock_quantity = stock_quantity - %s WHERE product_id = %s AND store_id = %s"
                # Add Sales History (Add)
                q2 = "INSERT INTO sales_history (sale_date, store_id, product_id, quantity_sold, on_sale) VALUES (CURRENT_DATE, %s, %s, %s, 0)"
                
                t1 = run_transaction(q1, (item['qty'], item['id'], selected_store_id))
                t2 = run_transaction(q2, (selected_store_id, item['id'], item['qty']))
                
                if not (t1 and t2):
                    success = False
            
            if success:
                st.balloons()
                st.success("Sale Recorded! Inventory Updated.")
                st.session_state['cart'] = [] # Clear cart
                st.rerun() # Refresh to update stock
            else:
                st.error("Transaction failed. Check database logs.")

    with col_clear:
        if st.button("🗑️ Clear Cart"):
            st.session_state['cart'] = []
            st.rerun()

else:
    st.info("Cart is empty. Select items above.")