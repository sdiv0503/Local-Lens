import streamlit as st
import pandas as pd
import altair as alt
from datetime import timedelta, datetime
from app import init_connection

st.set_page_config(page_title="Deep Dive Analytics", page_icon="📈", layout="wide")

# --- 1. Safety Checks ---
if 'forecast_cache' not in st.session_state:
    st.warning("⚠️ Please go to the **🏠 Homepage** first to generate the forecasts.")
    st.stop()

# --- 2. Helper Functions ---
@st.cache_data(show_spinner=False)
def get_product_data(_conn, product_id, store_id):
    """Get price, recent history, AND specific current stock."""
    
    # 1. Get Stock & Price
    if store_id == "ALL_STORES":
        p_query = """
            SELECT AVG(price) as price, SUM(stock_quantity) as stock 
            FROM inventory WHERE product_id = %(pid)s
        """
        params = {"pid": product_id}
        h_query = "SELECT sale_date, SUM(quantity_sold) as qty FROM sales_history WHERE product_id = %(pid)s GROUP BY sale_date ORDER BY sale_date DESC LIMIT 30"
    else:
        p_query = """
            SELECT price, stock_quantity as stock 
            FROM inventory WHERE product_id = %(pid)s AND store_id = %(sid)s
        """
        params = {"pid": product_id, "sid": store_id}
        h_query = "SELECT sale_date, quantity_sold as qty FROM sales_history WHERE product_id = %(pid)s AND store_id = %(sid)s ORDER BY sale_date DESC LIMIT 30"
        
    meta_df = pd.read_sql(p_query, _conn, params=params)
    
    if meta_df.empty:
        price, stock = 0, 0
    else:
        price = meta_df.iloc[0]['price'] or 0 # Handle None price
        # --- FIX FOR TYPEERROR: Convert None to 0 ---
        stock = meta_df.iloc[0]['stock'] or 0 

    # 2. Get History
    history_df = pd.read_sql(h_query, _conn, params=params)
    history_df = history_df.sort_values('sale_date')
    
    return price, stock, history_df

def shift_dates_to_today(df, date_col):
    if df.empty: return df
    first_date = df[date_col].min()
    today = pd.Timestamp.now().normalize()
    shift = today - first_date
    df[date_col] = df[date_col] + shift
    return df

# --- 3. Load Session Data ---
forecast_cache = st.session_state['forecast_cache']
product_df = st.session_state['products_df']

# --- FIX FOR DUPLICATES: Drop duplicate names ---
product_df = product_df.drop_duplicates(subset=['name']) 

conn = init_connection()
stores_df = pd.read_sql("SELECT store_id, name FROM stores", conn)

# --- 4. Top Bar: Title & Filters ---
st.title("📈 Product Intelligence Engine")
st.markdown("Real-time demand sensing and inventory depletion analysis.")

with st.container(border=True):
    c_filter1, c_filter2 = st.columns([1, 2])
    with c_filter1:
        # Store Filter
        global_store_id = st.session_state.get('selected_store_id', "ALL_STORES")
        store_opts = {"ALL_STORES": "All Stores (Aggregated)"}
        store_opts.update(dict(zip(stores_df['store_id'], stores_df['name'])))
        
        keys = list(store_opts.keys())
        default_idx = keys.index(global_store_id) if global_store_id in keys else 0
        
        selected_store_id = st.selectbox("📍 Analysis Scope (Store):", options=keys, format_func=lambda x: store_opts[x], index=default_idx)

    with c_filter2:
        # Product Filter
        selected_product = st.selectbox("🔍 Select Product to Analyze:", product_df['name'])

# --- 5. Data Processing ---
# Use the filtered DF to get the ID
product_row = product_df[product_df['name'] == selected_product]
if product_row.empty:
    st.error("Product not found.")
    st.stop()

product_id = product_row.iloc[0]['product_id']

if product_id not in forecast_cache:
    st.error("No forecast model available for this product.")
else:
    # Fetch Data
    price, current_stock, history_df = get_product_data(conn, int(product_id), selected_store_id)
    fc = forecast_cache[product_id].copy()
    
    divider = 5 if selected_store_id != "ALL_STORES" else 1
    
    future_14 = fc.iloc[-14:].copy()
    future_14 = shift_dates_to_today(future_14, 'ds')
    future_14['Daily Sales'] = (future_14['yhat'] / divider).astype(int)
    future_14['Date_Label'] = future_14['ds'].dt.strftime('%b %d')
    future_14['Day'] = future_14['ds'].dt.day_name()
    
    # Inventory Burn-Down
    future_14['Cumulative_Sales'] = future_14['Daily Sales'].cumsum()
    # This subtraction is now safe because current_stock is guaranteed to be an int/float
    future_14['Projected_Stock'] = current_stock - future_14['Cumulative_Sales']
    
    stockout_row = future_14[future_14['Projected_Stock'] < 0]
    if not stockout_row.empty:
        days_until_stockout = (stockout_row.iloc[0]['ds'] - pd.Timestamp.now()).days
        days_until_stockout = max(0, days_until_stockout)
        stock_status = "CRITICAL"
    else:
        days_until_stockout = 14
        stock_status = "HEALTHY"

    # History Data Processing
    if not history_df.empty:
        history_df['sale_date'] = pd.to_datetime(history_df['sale_date'])
        last_hist_date = history_df['sale_date'].max()
        target_hist_end = pd.Timestamp.now().normalize() - timedelta(days=1)
        hist_shift = target_hist_end - last_hist_date
        history_df['sale_date'] = history_df['sale_date'] + hist_shift
        history_df['qty'] = history_df['qty'].astype(int)

    # KPI Metrics
    total_demand = future_14['Daily Sales'].sum()
    proj_revenue = total_demand * price
    
    # --- 6. KPI Row ---
    st.markdown("### 🚦 Key Performance Indicators")
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        st.metric("14-Day Total Demand", f"{total_demand} units", help="Forecasted sales volume")
    with k2:
        st.metric("Projected Revenue", f"₹{proj_revenue:,.0f}", help="Based on current price")
    with k3:
        if stock_status == "CRITICAL":
            st.metric("Days of Stock Left", f"{days_until_stockout} Days", delta="Stockout Risk", delta_color="inverse")
        else:
            st.metric("Days of Stock Left", "14+ Days", delta="Safe", delta_color="normal")
    with k4:
        st.metric("Current Inventory", f"{current_stock} units", help="Stock currently on hand")

    # --- 7. AI Insight Section ---
    has_trend = 'interest' in fc.columns
    start_sales = future_14['Daily Sales'].iloc[0]
    end_sales = future_14['Daily Sales'].iloc[-1]
    pct_change = ((end_sales - start_sales) / start_sales) * 100 if start_sales > 0 else 0
    
    with st.container(border=True):
        st.markdown("**🧠 AI Strategic Insight**")
        
        insight_cols = st.columns([1, 4])
        with insight_cols[0]:
            if stock_status == "CRITICAL":
                st.error("Action: RESTOCK")
            elif pct_change > 5:
                st.info("Action: MONITOR")
            else:
                st.success("Action: MAINTAIN")
                
        with insight_cols[1]:
            if stock_status == "CRITICAL":
                st.markdown(f"**Critical Inventory Alert:** Based on the forecast, you will **run out of stock around {stockout_row.iloc[0]['Date_Label']}**. A purchase order is recommended immediately.")
            elif has_trend and pct_change > 5:
                st.markdown(f"**Growth Opportunity:** '{selected_product}' is trending on Google Search, and local sales are rising ({pct_change:.1f}%). Ensure shelf visibility.")
            elif pct_change < -5:
                st.markdown(f"**Slowing Demand:** Sales are projected to dip by {abs(pct_change):.1f}%. Avoid over-ordering to prevent waste.")
            else:
                st.markdown("**Steady State:** Demand is stable. Maintain current inventory levels to minimize holding costs.")

    # --- 8. Main Chart ---
    st.subheader("📉 Forecast & Inventory Simulation")
    
    base = alt.Chart(future_14).encode(x=alt.X('Date_Label', sort=None, title=None))
    
    bar = base.mark_bar(color='#A9DFBF', opacity=0.6).encode(
        y=alt.Y('Daily Sales', title='Daily Sales (Units)'),
        tooltip=['Date_Label', 'Daily Sales']
    )
    
    line = base.mark_line(color='#E74C3C', strokeWidth=3).encode(
        y=alt.Y('Projected_Stock', title='Projected Remaining Stock'),
        tooltip=['Date_Label', 'Projected_Stock']
    )
    
    rule = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='black', strokeDash=[5, 5]).encode(y='y')

    combined_chart = (bar + line + rule).resolve_scale(y='independent').properties(height=400)
    
    with st.container(border=True):
        st.altair_chart(combined_chart, use_container_width=True)
        st.caption("🟢 Green Bars: Daily Sales Forecast | 🔴 Red Line: Remaining Stock Level")

    # --- 9. Context Charts ---
    c_hist, c_week = st.columns(2)
    
    with c_hist:
        with st.container(border=True):
            st.subheader("📜 Past 30 Days History")
            if not history_df.empty:
                chart_history = alt.Chart(history_df).mark_area(
                    line={'color':'#5D6D7E'},
                    color=alt.Gradient(
                        gradient='linear',
                        stops=[alt.GradientStop(color='#5D6D7E', offset=0),
                               alt.GradientStop(color='white', offset=1)],
                        x1=1, x2=1, y1=1, y2=0
                    )
                ).encode(
                    x=alt.X('sale_date', title=None, axis=alt.Axis(format='%b %d', labelAngle=-45)),
                    y=alt.Y('qty', title="Units Sold"),
                    tooltip=[alt.Tooltip('sale_date', title='Date', format='%b %d'), 'qty']
                ).properties(height=250)
                st.altair_chart(chart_history, use_container_width=True)
            else:
                st.info("No recent sales history available.")

    with c_week:
        with st.container(border=True):
            st.subheader("🗓️ Weekly Buying Pattern")
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            weekly = future_14.groupby('Day', as_index=False)['Daily Sales'].mean()
            
            chart_weekly = alt.Chart(weekly).mark_bar().encode(
                x=alt.X('Day', sort=day_order, title=None),
                y=alt.Y('Daily Sales', title="Avg Units"),
                color=alt.value('#85C1E9'),
                tooltip=['Day', 'Daily Sales']
            ).properties(height=250)
            st.altair_chart(chart_weekly, use_container_width=True)