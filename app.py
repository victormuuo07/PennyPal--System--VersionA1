import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import numpy as np
from dateutil.relativedelta import relativedelta
import time
import uuid
from sklearn.linear_model import LinearRegression
import pandas as pd



# Auto-refresh every 30 seconds
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
if time_since_refresh > 30:
    st.session_state.last_refresh = datetime.now()
    st.rerun()

# Supabase functions
from supabase_client import (
    get_current_material_balance,
    record_restock_with_balance,
    save_sale,
    save_expense,
    save_distribution,
    get_sales_summary,
    get_expenses_summary,
    get_sales_people,
    save_sales_person,
    get_distribution_data,
    save_batch,
    get_batches,
    save_production_output,
    get_raw_materials,
    save_restock,
    get_finished_goods,
    update_raw_material_stock,
    update_finished_goods,
    save_funding,
    get_funding,
    get_total_funding,
    get_material_balance,
    record_restock_with_transaction,
    record_material_usage,
    get_inventory_transactions,
    get_material_usage_summary,
    get_all_material_usage,
     record_restock_with_balance,
    record_material_usage_with_balance,
    get_current_material_balance,
    get_material_restock_history,
    get_inventory_balance_history
)

DEBUG_MODE = False  # Set to True only when debugging

def test_distribution_connection():
    try:
        test_record = {
            "id": str(uuid.uuid4()),
            "date": str(date.today()),
            "sales_person_id": "00000000-0000-0000-0000-000000000000",
            "distributor_type": "Test",
            "location": "Test Location",
            "product": "Test Product",
            "quantity_distributed": 1,
            "unit_price": 100,
            "expected_amount": 100,
            "distribution_type": "Test",
            "status": "Test",
            "notes": "Test connection"
        }
        return True
    except Exception as e:
        return False

st.set_page_config(
    page_title="🌶️ SpiseUp Finance Tracker",
    layout="wide",
    page_icon="🌶️",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem !important;
        font-weight: 700;
        background: linear-gradient(90deg, #D32F2F 0%, #F57C00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #333333;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #D32F2F;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .section-header {
        background: linear-gradient(90deg, #1565C0 0%, #1976D2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0 1rem 0;
        font-weight: 600;
        font-size: 1.2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding: 0 24px;
        font-weight: 500;
        color: #555555;
    }
    .stTabs [aria-selected="true"] {
        color: #D32F2F;
        font-weight: 700;
    }
    .stButton > button {
        background: linear-gradient(90deg, #D32F2F 0%, #F57C00 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }
    .alert-box {
        background: linear-gradient(90deg, #FFF3E0 0%, #FFECB3 100%);
        border-left: 5px solid #FF9800;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #5D4037;
        font-weight: 500;
    }
    .stMetric div[data-testid="stMetricValue"] {
        color: #333333 !important;
        font-weight: 700;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #333333 !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([1, 5])
with col1:
    st.image("spicyup.jpeg", width=80)
with col2:
    st.markdown('<h1 class="main-header">🌶️ SpiseUp Field & Finance Tracker</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Track sales, expenses, salespeople, distribution, and net profit in real-time!</p>', unsafe_allow_html=True)

st.markdown("---")

# Sidebar Filters
with st.sidebar:
    st.markdown('<div class="section-header">📅 Filter Data</div>', unsafe_allow_html=True)
    
    filter_mode = st.selectbox(
        "Select Period",
        ["All Time", "Custom Range", "Today", "Yesterday", "This Week", "Last Week", "This Month", "Last Month", "Last 7 Days", "Last 30 Days"]
    )
    
    start_date = end_date = date.today()
    
    if filter_mode == "All Time":
        start_date = date(2000, 1, 1)
        end_date = date(2099, 12, 31)
    elif filter_mode == "Custom Range":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", value=date.today())
    elif filter_mode == "Today":
        start_date = end_date = date.today()
    elif filter_mode == "Yesterday":
        start_date = end_date = date.today() - timedelta(days=1)
    elif filter_mode == "This Week":
        start_date = date.today() - timedelta(days=date.today().weekday())
        end_date = date.today()
    elif filter_mode == "Last Week":
        end_date = date.today() - timedelta(days=date.today().weekday() + 1)
        start_date = end_date - timedelta(days=6)
    elif filter_mode == "This Month":
        start_date = date.today().replace(day=1)
        end_date = date.today()
    elif filter_mode == "Last Month":
        start_date = (date.today().replace(day=1) - timedelta(days=1)).replace(day=1)
        end_date = date.today().replace(day=1) - timedelta(days=1)
    elif filter_mode == "Last 7 Days":
        start_date = date.today() - timedelta(days=6)
        end_date = date.today()
    elif filter_mode == "Last 30 Days":
        start_date = date.today() - timedelta(days=29)
        end_date = date.today()
    
    st.markdown("---")
    st.markdown('<div class="section-header">🔍 Advanced Filters</div>', unsafe_allow_html=True)
    
    sales_people = get_sales_people()
    sales_person_options = {p['full_name']: p['id'] for p in sales_people} if sales_people else {}
    
    if sales_people:
        salesperson_filter = st.multiselect(
            "Filter by Salesperson:",
            options=["All"] + list(sales_person_options.keys()),
            default=["All"]
        )
    
    payment_filter = st.multiselect(
        "Payment Status:",
        ["All", "Cash", "Credit / Pending"],
        default=["All"]
    )
    
    st.markdown("---")
    st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown(f"**Last updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Fetch & Prepare Data
@st.cache_data(ttl=300, show_spinner=False)
def fetch_raw_data():
    sales_data = get_sales_summary()
    expense_data = get_expenses_summary()
    distribution_data = get_distribution_data()
    sales_people_data = get_sales_people()
    
    sales_df = pd.DataFrame(sales_data) if sales_data else pd.DataFrame()
    expenses_df = pd.DataFrame(expense_data) if expense_data else pd.DataFrame()
    dist_df = pd.DataFrame(distribution_data) if distribution_data else pd.DataFrame()
    sp_df = pd.DataFrame(sales_people_data) if sales_people_data else pd.DataFrame()
    
    return sales_df, expenses_df, dist_df, sp_df

raw_sales_df, raw_expenses_df, raw_dist_df, raw_sp_df = fetch_raw_data()

def filter_by_date(df, date_column, start_date, end_date):
    if df.empty or date_column not in df.columns:
        return df
    try:
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        df = df.dropna(subset=[date_column])
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        mask = (df[date_column] >= start_dt) & (df[date_column] <= end_dt)
        return df[mask].copy()
    except Exception as e:
        return df

sales_df = filter_by_date(raw_sales_df.copy(), 'Date', start_date, end_date)
expenses_df = filter_by_date(raw_expenses_df.copy(), 'date', start_date, end_date)
dist_df = filter_by_date(raw_dist_df.copy(), 'date', start_date, end_date)
sp_df = raw_sp_df.copy()

if not sales_df.empty:
    for col in ['Total', 'Quantity', 'Price_per_Unit']:
        if col in sales_df.columns:
            sales_df[col] = pd.to_numeric(sales_df[col], errors='coerce').fillna(0)

if not expenses_df.empty and 'amount' in expenses_df.columns:
    expenses_df['amount'] = pd.to_numeric(expenses_df['amount'], errors='coerce').fillna(0)

def calculate_kpis(sales_df, expenses_df):
    total_sales = sales_df['Total'].sum() if not sales_df.empty else 0
    total_cash = sales_df[sales_df['Payment_Status'] == "Cash"]['Total'].sum() if not sales_df.empty else 0
    total_credit = sales_df[sales_df['Payment_Status'] != "Cash"]['Total'].sum() if not sales_df.empty else 0
    total_expenses = expenses_df['amount'].sum() if not expenses_df.empty else 0
    net_profit = total_sales - total_expenses
    running_balance = total_cash - total_expenses
    
    if not sales_df.empty:
        total_sachets = sales_df['Quantity'].sum()
        avg_sale_value = sales_df['Total'].mean() if len(sales_df) > 0 else 0
        cash_percentage = (total_cash / total_sales * 100) if total_sales > 0 else 0
        credit_percentage = (total_credit / total_sales * 100) if total_sales > 0 else 0
        sales_by_date = sales_df.groupby('Date')['Total'].sum()
        avg_daily_sales = sales_by_date.mean() if len(sales_by_date) > 0 else 0
        best_day = sales_by_date.idxmax() if len(sales_by_date) > 0 else None
        best_day_sales = sales_by_date.max() if len(sales_by_date) > 0 else 0
    else:
        total_sachets = 0
        avg_sale_value = 0
        cash_percentage = 0
        credit_percentage = 0
        avg_daily_sales = 0
        best_day = None
        best_day_sales = 0
    
    return {
        'total_sales': total_sales,
        'total_cash': total_cash,
        'total_credit': total_credit,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'running_balance': running_balance,
        'total_sachets': total_sachets,
        'avg_sale_value': avg_sale_value,
        'cash_percentage': cash_percentage,
        'credit_percentage': credit_percentage,
        'avg_daily_sales': avg_daily_sales,
        'best_day': best_day,
        'best_day_sales': best_day_sales,
        'top_expense_category': expenses_df.groupby('category')['amount'].sum().idxmax() if not expenses_df.empty and 'category' in expenses_df.columns else "None"
    }

kpis = calculate_kpis(sales_df, expenses_df)

# Create Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Dashboard", 
    "💰 Sales", 
    "💸 Expenses", 
    "👥 Salespeople", 
    "📈 Analytics",
     "🏭 Production & Inventory",
     "💰 Funding & Capital"
])

# ==================== TAB 1: DASHBOARD ====================
with tab1:
    st.markdown('<div class="section-header">📈 Financial Overview</div>', unsafe_allow_html=True)
    
    # Top Metrics Row
    col1, col2, col3, = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Sales", f"KES {kpis['total_sales']:,.0f}")
        st.caption(f"📦 {kpis['total_sachets']:,.0f} items sold")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Net Profit", f"KES {kpis['net_profit']:,.0f}")
        st.caption(f"Profit Margin: {(kpis['net_profit']/kpis['total_sales']*100 if kpis['total_sales'] > 0 else 0):.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Cash Balance", f"KES {kpis['running_balance']:,.0f}")
        cash_status = "🟢 Good" if kpis['running_balance'] > 0 else "🔴 Low"
        st.caption(f"Status: {cash_status}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Second Metrics Row
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Cash Collected", f"KES {kpis['total_cash']:,.0f}", delta=f"{kpis['cash_percentage']:.1f}% of total")
    with col5:
        st.metric("Credit Pending", f"KES {kpis['total_credit']:,.0f}", delta=f"{kpis['credit_percentage']:.1f}% of total", delta_color="inverse")
    with col6:
        st.metric("Total Expenses", f"KES {kpis['total_expenses']:,.0f}", help=f"Top category: {kpis['top_expense_category']}")
    # Add this in your metrics row (around the other metrics)
     # Third Metrics Row (3 columns) - NEW
    col7, col8, col9 = st.columns(3)
    with col7:
        st.metric("Total Funding", f"KES {get_total_funding():,.0f}")
    with col8:
        # You can add another metric here (e.g., ROI)
        if get_total_funding() > 0:
            roi = ((kpis['total_sales'] - kpis['total_expenses']) / get_total_funding()) * 100
            st.metric("ROI", f"{roi:.1f}%")
        else:
            st.metric("ROI", "N/A")
    with col9:
        # You can add another metric here
        capital_used = (kpis['total_expenses'] / get_total_funding() * 100) if get_total_funding() > 0 else 0
        st.metric("Capital Used", f"{capital_used:.1f}%")

    # Alerts
    alerts = []
    if kpis['credit_percentage'] > 30:
        alerts.append("⚠️ **High credit sales** (>30% of total). Consider following up on pending payments.")
    if kpis['net_profit'] < 0:
        alerts.append("🔴 **Negative net profit**. Review expenses and pricing strategy.")
    if kpis['running_balance'] < 10000:
        alerts.append("💰 **Low cash balance**. Monitor expenses closely.")
    
    if alerts:
        st.markdown('<div class="section-header">🚨 Alerts & Notifications</div>', unsafe_allow_html=True)
        for alert in alerts:
            st.markdown(f'<div class="alert-box">{alert}</div>', unsafe_allow_html=True)
    
    # Advanced Charts Section
    st.markdown('<div class="section-header">📊 Performance Analytics</div>', unsafe_allow_html=True)
    
    if not sales_df.empty or not expenses_df.empty:
        # Create data for charts
        sales_by_date = sales_df.groupby("Date")['Total'].sum().reset_index() if not sales_df.empty else pd.DataFrame()
        expenses_by_date = expenses_df.groupby("date")['amount'].sum().reset_index() if not expenses_df.empty else pd.DataFrame()
        
        if not sales_by_date.empty and not expenses_by_date.empty:
            combined_df = pd.merge(sales_by_date, expenses_by_date, left_on='Date', right_on='date', how='outer').fillna(0)
            combined_df['Net Profit'] = combined_df['Total'] - combined_df['amount']
        elif not sales_by_date.empty:
            combined_df = sales_by_date.copy()
            combined_df['amount'] = 0
            combined_df['Net Profit'] = combined_df['Total']
        else:
            combined_df = pd.DataFrame()
        
        # Chart 1: Sales vs Expenses vs Profit (Line + Bar)
        if not combined_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=combined_df['Date'], y=combined_df['Total'], name='Sales', marker_color='#36B37E', opacity=0.7))
            fig.add_trace(go.Bar(x=combined_df['Date'], y=combined_df['amount'], name='Expenses', marker_color='#FF4B4B', opacity=0.7))
            fig.add_trace(go.Scatter(x=combined_df['Date'], y=combined_df['Net Profit'], name='Net Profit', mode='lines+markers', line=dict(color='#FFB020', width=3), marker=dict(size=8)))
            fig.update_layout(title='Sales vs Expenses vs Net Profit Over Time', xaxis_title='Date', yaxis_title='Amount (KES)', hovermode='x unified', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        
        # Chart 2: Sales Trend with Moving Average
        if not sales_by_date.empty and len(sales_by_date) > 3:
            sales_by_date['7_Day_MA'] = sales_by_date['Total'].rolling(window=min(7, len(sales_by_date))).mean()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=sales_by_date['Date'], y=sales_by_date['Total'], name='Daily Sales', mode='lines+markers', line=dict(color='#1565C0', width=2), marker=dict(size=6)))
            fig.add_trace(go.Scatter(x=sales_by_date['Date'], y=sales_by_date['7_Day_MA'], name='7-Day Moving Average', line=dict(color='#FF9800', width=3, dash='dash')))
            fig.update_layout(title='Sales Trend with Moving Average', xaxis_title='Date', yaxis_title='Sales (KES)', hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
        
        # Chart 3: Cumulative Sales
        if not sales_by_date.empty:
            sales_by_date['Cumulative Sales'] = sales_by_date['Total'].cumsum()
            fig = px.area(sales_by_date, x='Date', y='Cumulative Sales', title='Cumulative Sales Over Time', color_discrete_sequence=['#4CAF50'])
            fig.update_layout(xaxis_title='Date', yaxis_title='Cumulative Sales (KES)')
            st.plotly_chart(fig, use_container_width=True)
    
    # Quick Stats Row
    st.markdown('<div class="section-header">📋 Quick Statistics</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info(f"**Avg Sale Value:**\nKES {kpis['avg_sale_value']:,.0f}")
    with col2:
        st.info(f"**Avg Daily Sales:**\nKES {kpis['avg_daily_sales']:,.0f}")
    with col3:
        st.info(f"**Cash vs Credit:**\n{kpis['cash_percentage']:.0f}% / {kpis['credit_percentage']:.0f}%")
    with col4:
        best_day_str = kpis['best_day'].strftime('%b %d') if kpis['best_day'] else "N/A"
        st.info(f"**Best Day:**\n{best_day_str} (KES {kpis['best_day_sales']:,.0f})")
    
    # Recent Activity
    st.markdown('<div class="section-header">🕒 Recent Activity</div>', unsafe_allow_html=True)
    if not sales_df.empty:
        recent_sales = sales_df.sort_values('Date', ascending=False).head(5)
        for _, row in recent_sales.iterrows():
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"**{row['Name']}**")
                st.caption(f"{row['Location']} • {row['Date'].strftime('%b %d')}")
            with col2:
                st.write(f"📦 {int(row['Quantity'])} items")
            with col3:
                st.write(f"💰 KES {row['Total']:,.0f}")
            st.divider()

# ==================== TAB 2: SALES ====================
with tab2:
    st.markdown('<div class="section-header">💰 Record New Sale</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown("### Customer Details")
            sale_date = st.date_input("Date", value=date.today())
            shop_name = st.text_input("Shop / Contact Name", key="shop_name")
            phone = st.text_input("Phone Number", key="phone")
            location = st.text_input("Location", key="location")
    
    with col2:
        with st.container():
            st.markdown("### Sale Details")
            
            product_main = st.radio(
                "Product Type",
                ["Sachet - Standard (5 KES)", "Sachet - Premium (30 KES)", "Bottle (100g New)", "Bottle (100g Refill)"],
                horizontal=True
            )
            
            customer_type = st.radio(
                "Customer Type",
                ["Consumer (B2C)", "Shop/Mama Mboga (B2B)", "Hotel/Restaurant"],
                horizontal=True
            )
            
            if product_main == "Sachet - Standard (5 KES)":
                if customer_type == "Consumer (B2C)":
                    price, min_qty, default_qty, unit = 5.0, 1, 1, "sachets"
                    product_name = "SpiseUp Spicy Salt Sachet (5 KES) - Consumer"
                elif customer_type == "Shop/Mama Mboga (B2B)":
                    price, min_qty, default_qty, unit = 2.9, 18, 18, "sachets"
                    product_name = "SpiseUp Spicy Salt Sachet (2.9 KES) - Wholesale"
                else:
                    price, min_qty, default_qty, unit = 2.9, 18, 200, "sachets"
                    product_name = "SpiseUp Spicy Salt Sachet (2.9 KES) - Hotel"
            elif product_main == "Sachet - Premium (30 KES)":
                price, min_qty, default_qty, unit = 30.0, 1, 5, "sachets"
                product_name = f"SpiseUp Spicy Salt Sachet (30 KES) - {customer_type}"
            elif product_main == "Bottle (100g New)":
                if customer_type == "Consumer (B2C)":
                    price, min_qty, default_qty, unit = 150.0, 1, 2, "bottles"
                    product_name = "SpiseUp Spicy Salt Bottle (100g New) - Consumer"
                elif customer_type == "Shop/Mama Mboga (B2B)":
                    price, min_qty, default_qty, unit = 130.0, 1, 10, "bottles"
                    product_name = "SpiseUp Spicy Salt Bottle (100g New) - Wholesale"
                else:
                    price, min_qty, default_qty, unit = 130.0, 1, 20, "bottles"
                    product_name = "SpiseUp Spicy Salt Bottle (100g New) - Hotel"
            else:
                price, min_qty, default_qty, unit = 120.0, 1, 5, "refills"
                product_name = f"SpiseUp Spicy Salt Bottle (100g Refill) - {customer_type}"
                st.success("🔄 **REFILL BENEFIT:** Pay KES 120 and get 100g (save KES 30, get 20% more!)")
            
            if min_qty > 1:
                st.info(f"📦 Minimum order: {min_qty} {unit}")
            
            quantity = st.number_input(f"Quantity ({unit})", min_value=min_qty, step=min_qty if min_qty > 1 else 1, value=default_qty)
            price = st.number_input("Price per unit (KES)", min_value=0.0, max_value=500.0, step=1.0, value=float(price), format="%.1f")
            total = quantity * price
            st.success(f"**Total Amount:** KES {total:,.2f}")
            
            hotel_name, mama_name = None, None
            if customer_type == "Hotel/Restaurant":
                st.markdown("---")
                st.subheader("🏨 Hotel Tracking")
                hotel_name = st.text_input("Hotel Name", placeholder="Enter hotel name", key="hotel_track")
                if hotel_name:
                    col_a, col_b = st.columns(2)
                    with col_b:
                        refill_count = st.number_input("Times refilled this month", min_value=0, value=1, key="refill_count")
                        if refill_count > 0:
                            avg_days = 30 / refill_count
                            if avg_days < 7:
                                st.success("🔥 High frequency customer!")
                            elif avg_days < 14:
                                st.info("📈 Medium frequency")
                            else:
                                st.warning("⏰ Low frequency - consider follow-up")
            
            if customer_type == "Shop/Mama Mboga (B2B)":
                st.markdown("---")
                st.subheader("🏪 Mama Mboga/Shop Tracking")
                mama_name = st.text_input("Mama Mboga/Shop Name", placeholder="Enter shop name", key="mama_track")
                if mama_name:
                    st.caption("💡 They buy at KES 2.9, sell at KES 5 - KES 2.1 profit per sachet!")
            
            payment_status = st.selectbox("Payment Status", ["Cash", "Credit / Pending"])
            
            if sales_person_options:
                sales_person_name = st.selectbox("Sales Person", ["Select..."] + list(sales_person_options.keys()))
            else:
                sales_person_name = "N/A"
                st.warning("No salespeople added yet.")
    
    with st.expander("📝 Additional Details"):
        feedback = st.text_area("Customer Feedback", placeholder="Any feedback from the customer...")
        follow_up = st.text_input("Follow-up Action", placeholder="Next steps or follow-up required...")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        submitted_sale = st.button("💾 Save Sale", type="primary", use_container_width=True)
    with col2:
        clear_form = st.button("🗑️ Clear Form", use_container_width=True)
    
    if clear_form:
        for key in ['shop_name', 'phone', 'location', 'product', 'quantity', 'price', 'payment_status', 'sales_person_name', 'feedback', 'follow_up']:
            if key in st.session_state:
                del st.session_state[key]
        st.success("✅ Form cleared!")
        st.rerun()
    
    if submitted_sale:
        if not shop_name.strip():
            st.error("Please enter a Shop/Contact Name!")
        elif sales_person_name == "Select...":
            st.error("Please select a salesperson!")
        else:
            sale_record = {
                "Date": str(sale_date),
                "Name": shop_name,
                "Phone": phone,
                "Location": location,
                "Product": product_name,
                "Product_Type": product_main,
                "Customer_Type": customer_type,
                "Unit": unit,
                "Quantity": quantity,
                "Price_per_Unit": price,
                "Total": total,
                "Payment_Status": payment_status,
                "Feedback": feedback,
                "Follow_Up": follow_up,
                "Is_Refill": "Refill" in product_main,
                "Tracking_Hotel": hotel_name if hotel_name else None,
                "Tracking_Mama": mama_name if mama_name else None
            }
            
            sale_id = save_sale(sale_record)
            
            if sale_id:
                st.success(f"✅ Sale saved successfully! Total: **KES {total:,.0f}**")
                if sales_person_name not in ["Select...", "N/A"] and sales_person_name in sales_person_options:
                    success = save_distribution(
                        sale_id=sale_id,
                        sales_person_id=sales_person_options[sales_person_name],
                        quantity=quantity,
                        sale_date=str(sale_date),
                        price=price,
                        sale_data=sale_record
                    )
                    if success:
                        st.info(f"👤 Assigned to: **{sales_person_name}**")
                        st.balloons()
            else:
                st.error("❌ Failed to save sale.")
    
    # Recent Sales Table
    st.markdown('<div class="section-header">📋 Recent Sales</div>', unsafe_allow_html=True)
    if not sales_df.empty:
        recent_sales = sales_df.sort_values('Date', ascending=False).head(20)
        display_df = recent_sales.copy()
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        display_df['Total'] = display_df['Total'].apply(lambda x: f"KES {x:,.0f}")
        st.dataframe(display_df[['Date', 'Name', 'Quantity', 'Total', 'Payment_Status', 'Location']], use_container_width=True, hide_index=True)

# ==================== TAB 3: EXPENSES ====================
with tab3:
    st.markdown('<div class="section-header">💸 Record New Expense</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        expense_date = st.date_input("Date", value=date.today(), key="expense_date")
        category = st.selectbox("Category", ["Supplies", "Transport", "Marketing", "Salaries", "Office Rent", "Utilities", "Other"])
        amount = st.number_input("Amount (KES)", min_value=0, step=100, value=1000)
        description = st.text_area("Description", placeholder="Details about this expense...")
    with col2:
        payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Mobile Money", "Credit Card"])
        paid_by = st.text_input("Paid By", placeholder="Name of person who paid")
        status = st.selectbox("Status", ["Paid", "Pending", "Reimbursed"])
        if category == "Other":
            custom_category = st.text_input("Specify Category")
            if custom_category:
                category = custom_category
    
    if st.button("💾 Save Expense", type="primary", use_container_width=True):
        if amount <= 0:
            st.error("Please enter a valid amount!")
        else:
            save_expense({
                "date": str(expense_date),
                "category": category,
                "description": description,
                "amount": amount,
                "payment_method": payment_method,
                "paid_by": paid_by,
                "receipt": "",
                "status": status
            })
            st.success(f"✅ Expense saved! Amount: **KES {amount:,.0f}**")
    
    # Expense Analysis Charts
    st.markdown('<div class="section-header">📊 Expense Analysis</div>', unsafe_allow_html=True)
    if not expenses_df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Expenses", f"KES {expenses_df['amount'].sum():,.0f}")
        with col2:
            st.metric("Average Expense", f"KES {expenses_df['amount'].mean():,.0f}")
        with col3:
            st.metric("Number of Expenses", len(expenses_df))
        
        col1, col2 = st.columns(2)
        with col1:
            category_summary = expenses_df.groupby("category")['amount'].sum().reset_index()
            fig = px.pie(category_summary, values='amount', names='category', title='Expenses by Category', color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            expenses_by_date = expenses_df.groupby('date')['amount'].sum().reset_index()
            fig = px.line(expenses_by_date, x='date', y='amount', title='Expense Trend Over Time', markers=True, line_shape='spline')
            fig.update_traces(line=dict(color='#FF4B4B', width=3))
            st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 4: SALESPEOPLE ====================
with tab4:
    st.markdown('<div class="section-header">👥 Manage Sales Team</div>', unsafe_allow_html=True)
    
    with st.expander("➕ Add New Salesperson", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name", key="sp_name")
            phone = st.text_input("Phone Number", key="sp_phone")
            role = st.selectbox("Role", ["Sales Rep", "Manager", "Distributor", "Team Lead"], key="sp_role")
        with col2:
            location = st.text_input("Location", key="sp_location")
            status = st.selectbox("Status", ["Active", "Inactive", "On Leave"], key="sp_status")
            commission_rate = st.number_input("Commission Rate (%)", min_value=0.0, max_value=100.0, step=0.5, value=5.0, key="sp_commission")
        notes = st.text_area("Notes", key="sp_notes")
        
        if st.button("➕ Add Salesperson", type="primary"):
            if not full_name.strip() or not phone.strip():
                st.warning("Please fill in all required fields!")
            else:
                sp_id = save_sales_person(full_name=full_name, phone=phone, role=role, location=location, status=status, commission_rate=commission_rate, notes=notes)
                if sp_id:
                    st.success(f"✅ Salesperson '{full_name}' added successfully!")
                    st.rerun()
    
    if sales_people:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Team Members", len(sales_people))
        with col2:
            active_count = len([p for p in sales_people if p.get('status') == 'Active'])
            st.metric("Active Members", active_count)
        
        for person in sales_people:
            if person.get('status') == 'Active':
                with st.container():
                    st.write(f"**{person['full_name']}** - {person['role']} ({person['location']})")
                    st.caption(f"📱 {person['phone']} | 💰 {person.get('commission_rate', 0)}% commission")
                    st.divider()

# ==================== TAB 5: ADVANCED ANALYTICS ====================
with tab5:
    st.markdown('<div class="section-header">📈 Advanced Analytics</div>', unsafe_allow_html=True)
    
    analytics_tab1, analytics_tab2, analytics_tab3, analytics_tab4, analytics_tab5 = st.tabs([
        "🏆 Performance Leaderboards", 
        "📊 Distribution Insights", 
        "🏨 Hotel & Mama Mboga", 
        "📁 Data Management",
        "🦈 Shark Tank Analytics"
    ])
    
    with analytics_tab1:
        # Salespeople Leaderboard
        if not dist_df.empty and not sp_df.empty:
            st.markdown("### 🏆 Salespeople Performance Leaderboard")
            
            dist_merged = dist_df.merge(sp_df, left_on="sales_person_id", right_on="id")
            dist_merged['Total_Value'] = dist_merged['quantity_distributed'] * dist_merged['unit_price']
            
            sp_summary = dist_merged.groupby("full_name").agg({'Total_Value': 'sum', 'quantity_distributed': 'sum', 'sales_person_id': 'count'}).reset_index()
            sp_summary.columns = ['Salesperson', 'Revenue (KES)', 'Quantity', 'Number of Sales']
            sp_summary = sp_summary.sort_values('Revenue (KES)', ascending=False)
            sp_summary['Rank'] = range(1, len(sp_summary) + 1)
            
            st.dataframe(sp_summary[['Rank', 'Salesperson', 'Revenue (KES)', 'Quantity', 'Number of Sales']].head(10), use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(sp_summary.head(10), x='Salesperson', y='Revenue (KES)', title='Top 10 Salespeople by Revenue', color='Revenue (KES)', color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = px.bar(sp_summary.head(10), x='Salesperson', y='Quantity', title='Top 10 Salespeople by Quantity', color='Quantity', color_continuous_scale='Plasma')
                st.plotly_chart(fig, use_container_width=True)
        
        # Shop Performance
        if not dist_df.empty and not sales_df.empty:
            st.markdown("### 🏪 Shop Performance Analysis")
            
            merged_shop = dist_df.merge(sales_df, left_on="sale_id", right_on="id")
            
            if not merged_shop.empty:
                shop_summary = merged_shop.groupby("Name").agg(
                    total_quantity=pd.NamedAgg(column="quantity_distributed", aggfunc="sum"),
                    total_value=pd.NamedAgg(column="unit_price", aggfunc=lambda x: (merged_shop.loc[x.index, 'quantity_distributed'] * x).sum()),
                    num_visits=pd.NamedAgg(column="sale_id", aggfunc="nunique"),
                    avg_order_value=pd.NamedAgg(column="Total", aggfunc="mean")
                ).reset_index()
                
                shop_summary.columns = ['Shop Name', 'Total Quantity', 'Total Revenue', 'Number of Visits', 'Average Order Value']
                shop_summary = shop_summary.sort_values('Total Revenue', ascending=False)
                
                st.dataframe(shop_summary.head(10), use_container_width=True, hide_index=True)
                
                fig = px.scatter(shop_summary.head(20), x='Number of Visits', y='Total Revenue', size='Average Order Value', color='Total Quantity', hover_name='Shop Name', title='Shop Performance: Visits vs Revenue')
                st.plotly_chart(fig, use_container_width=True)
    
    with analytics_tab2:
        st.markdown("### 📊 Distribution Insights")
        
        if not dist_df.empty and not sp_df.empty:
            dist_merged = dist_df.merge(sp_df, left_on="sales_person_id", right_on="id")
            
            # Productivity
            productivity = dist_merged.groupby('full_name').agg({'quantity_distributed': 'sum', 'sales_person_id': 'count'}).reset_index()
            productivity.columns = ['Salesperson', 'Total Quantity', 'Number of Sales']
            productivity = productivity.sort_values('Total Quantity', ascending=False)
            st.dataframe(productivity, use_container_width=True, hide_index=True)
            
            # Time-based analysis
            if 'date' in dist_df.columns:
                st.markdown("### 📅 Time-Based Analysis")
                
                dist_time = dist_df.copy()
                dist_time['day_of_week'] = dist_time['date'].dt.day_name()
                dist_time['month'] = dist_time['date'].dt.month_name()
                dist_time['week'] = dist_time['date'].dt.isocalendar().week
                
                col1, col2 = st.columns(2)
                with col1:
                    daily = dist_time.groupby('day_of_week')['quantity_distributed'].sum().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).reset_index()
                    daily.columns = ['Day', 'Quantity']
                    fig = px.bar(daily, x='Day', y='Quantity', title='Sales by Day of Week', color='Quantity', color_continuous_scale='Viridis')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    monthly = dist_time.groupby(dist_time['date'].dt.strftime('%Y-%m'))['quantity_distributed'].sum().reset_index()
                    monthly.columns = ['Month', 'Quantity']
                    fig = px.line(monthly, x='Month', y='Quantity', title='Monthly Sales Trend', markers=True)
                    st.plotly_chart(fig, use_container_width=True)
    
    with analytics_tab3:
        # Hotel Refill Tracking Dashboard
        st.markdown("### 🏨 Hotel Refill Performance")
        
        if not sales_df.empty:
            hotel_sales = sales_df[sales_df['Customer_Type'] == 'Hotel/Restaurant'] if 'Customer_Type' in sales_df.columns else pd.DataFrame()
            if not hotel_sales.empty:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Hotels", hotel_sales['Name'].nunique())
                with col2:
                    refill_count = len(hotel_sales[hotel_sales['Is_Refill'] == True]) if 'Is_Refill' in hotel_sales.columns else 0
                    st.metric("Refill Orders", refill_count)
                with col3:
                    st.metric("Hotel Revenue", f"KES {hotel_sales['Total'].sum():,.0f}")
                
                hotel_summary = hotel_sales.groupby('Name').agg({'Total': 'sum', 'Date': 'count', 'Quantity': 'sum'}).reset_index()
                hotel_summary.columns = ['Hotel', 'Revenue', 'Orders', 'Quantity']
                hotel_summary = hotel_summary.sort_values('Orders', ascending=False).head(10)
                
                st.dataframe(hotel_summary, use_container_width=True, hide_index=True)
                
                fig = px.bar(hotel_summary, x='Hotel', y='Orders', title='Fastest Refilling Hotels', color='Revenue', text='Orders')
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hotel sales recorded yet")
        
        st.markdown("---")
        st.markdown("### 🏪 Mama Mboga Performance")
        
        if not sales_df.empty:
            mama_sales = sales_df[sales_df['Customer_Type'] == 'Shop/Mama Mboga (B2B)'] if 'Customer_Type' in sales_df.columns else pd.DataFrame()
            if not mama_sales.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Shops", mama_sales['Name'].nunique())
                with col2:
                    st.metric("Total Revenue", f"KES {mama_sales['Total'].sum():,.0f}")
                
                mama_summary = mama_sales.groupby('Name').agg({'Total': 'sum', 'Quantity': 'sum', 'Date': 'count'}).reset_index()
                mama_summary.columns = ['Shop', 'Revenue', 'Quantity', 'Orders']
                mama_summary = mama_summary.sort_values('Revenue', ascending=False).head(10)
                
                st.dataframe(mama_summary, use_container_width=True, hide_index=True)
                
                # Profit potential
                mama_summary['Potential Profit'] = mama_summary['Quantity'] * 2.1
                st.caption("💡 Reseller profit potential: Buy at 2.9, sell at 5 = 2.1 profit per sachet")
                
                fig = px.bar(mama_summary, x='Shop', y='Potential Profit', title='Top Shops by Reseller Profit Potential', color='Revenue', text='Potential Profit')
                fig.update_traces(texttemplate='KES %{text:,.0f}', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No Mama Mboga sales recorded yet")
        
        # Product Mix Analysis
        st.markdown("---")
        st.markdown("### 📦 Product Mix Analysis")
        
        if not sales_df.empty:
            col1, col2 = st.columns(2)
            with col1:
                product_summary = sales_df.groupby('Product_Type')['Total'].sum().reset_index() if 'Product_Type' in sales_df.columns else sales_df.groupby('Product')['Total'].sum().reset_index()
                product_summary.columns = ['Product', 'Revenue']
                fig = px.pie(product_summary, values='Revenue', names='Product', title='Revenue by Product Type', color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'Price_per_Unit' in sales_df.columns:
                    price_analysis = sales_df.groupby('Price_per_Unit')['Quantity'].sum().reset_index()
                    price_analysis.columns = ['Price (KES)', 'Quantity Sold']
                    fig = px.bar(price_analysis, x='Price (KES)', y='Quantity Sold', title='Sales Volume by Price Point', color='Quantity Sold', color_continuous_scale='Viridis')
                    st.plotly_chart(fig, use_container_width=True)
    
    with analytics_tab4:
        st.markdown("### 📁 Data Export & Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Export Sales Data", use_container_width=True, type="primary"):
                if not sales_df.empty:
                    csv = sales_df.to_csv(index=False)
                    st.download_button("Download CSV", csv, f"sales_data_{date.today()}.csv", "text/csv")
                else:
                    st.warning("No sales data to export")
        
        with col2:
            if st.button("📥 Export Expenses Data", use_container_width=True, type="primary"):
                if not expenses_df.empty:
                    csv = expenses_df.to_csv(index=False)
                    st.download_button("Download CSV", csv, f"expenses_data_{date.today()}.csv", "text/csv")
                else:
                    st.warning("No expenses data to export")
        
        with col3:
            if st.button("📊 Generate Summary Report", use_container_width=True, type="primary"):
                report = f"""
                # SpiseUp Finance Report
                ## Period: {start_date} to {end_date}
                
                ### Summary
                - Total Sales: KES {kpis['total_sales']:,.0f}
                - Total Expenses: KES {kpis['total_expenses']:,.0f}
                - Net Profit: KES {kpis['net_profit']:,.0f}
                - Cash Balance: KES {kpis['running_balance']:,.0f}
                
                ### Sales Details
                - Cash Collected: KES {kpis['total_cash']:,.0f} ({kpis['cash_percentage']:.1f}%)
                - Credit Pending: KES {kpis['total_credit']:,.0f} ({kpis['credit_percentage']:.1f}%)
                - Total Items Sold: {kpis['total_sachets']:,.0f}
                - Average Sale Value: KES {kpis['avg_sale_value']:,.0f}
                
                Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """
                st.download_button("Download Report", report, f"spiseup_report_{date.today()}.txt", "text/plain")
        
        with st.expander("Data Quality Check"):
            if not sales_df.empty:
                missing_data = sales_df.isnull().sum()
                if missing_data.sum() > 0:
                    st.warning(f"Found {missing_data.sum()} missing values in sales data")
                else:
                    st.success("✅ Sales data quality check passed!")
                    
    with analytics_tab5:
        st.markdown("### 🦈 Shark Tank-Style Business Intelligence")
    
        if not sales_df.empty:
        
        # ============================================
        # 1. COHORT ANALYSIS - Customer Retention
        # ============================================
            st.markdown("#### 📊 Customer Cohort Analysis")
        
        # Create cohort data - FIXED Period serialization issue
            sales_df_copy = sales_df.copy()
            sales_df_copy['CohortMonth'] = sales_df_copy.groupby('Name')['Date'].transform('min').dt.strftime('%Y-%m')
            sales_df_copy['OrderMonth'] = sales_df_copy['Date'].dt.strftime('%Y-%m')
        
        # Calculate months difference
            def get_month_diff(order_month, cohort_month):
                y1, m1 = map(int, order_month.split('-'))
                y2, m2 = map(int, cohort_month.split('-'))
                return (y1 - y2) * 12 + (m1 - m2)
        
            sales_df_copy['CohortIndex'] = sales_df_copy.apply(
            lambda x: get_month_diff(x['OrderMonth'], x['CohortMonth']), axis=1
        )
        
            cohort_data = sales_df_copy.groupby(['CohortMonth', 'CohortIndex']).agg(
            unique_customers=pd.NamedAgg(column='Name', aggfunc='nunique'),
            total_revenue=pd.NamedAgg(column='Total', aggfunc='sum')
        ).reset_index()
        
            cohort_pivot = cohort_data.pivot(index='CohortMonth', columns='CohortIndex', values='unique_customers')
        
            if not cohort_pivot.empty:
            # Convert to string for display
                cohort_pivot_display = cohort_pivot.copy()
                cohort_pivot_display.index = cohort_pivot_display.index.astype(str)
                cohort_pivot_display.columns = cohort_pivot_display.columns.astype(str)
            
                fig = px.imshow(cohort_pivot_display.values, 
                           title='Customer Retention Heatmap (Cohort Analysis)',
                           labels=dict(x="Months since first purchase", y="Cohort Month", color="Customers"),
                           color_continuous_scale='RdBu',
                           x=cohort_pivot_display.columns.astype(str),
                           y=cohort_pivot_display.index.astype(str))
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                st.caption("💡 **Insight:** Shows how many customers return month after month")
        
        # ============================================
        # 2. CUSTOMER LIFETIME VALUE (LTV)
        # ============================================
            st.markdown("#### 💰 Customer Lifetime Value (LTV)")
        
            customer_ltv = sales_df.groupby('Name').agg(
            total_spent=pd.NamedAgg(column='Total', aggfunc='sum'),
            order_count=pd.NamedAgg(column='Total', aggfunc='count'),
            avg_order_value=pd.NamedAgg(column='Total', aggfunc='mean'),
            first_purchase=pd.NamedAgg(column='Date', aggfunc='min'),
            last_purchase=pd.NamedAgg(column='Date', aggfunc='max')
        ).reset_index()
        
            customer_ltv['days_active'] = (customer_ltv['last_purchase'] - customer_ltv['first_purchase']).dt.days
            customer_ltv['purchase_frequency'] = customer_ltv['order_count'] / ((customer_ltv['days_active'] + 1) / 30)
        
        # Segment customers
            customer_ltv['Segment'] = pd.cut(customer_ltv['total_spent'], 
                                         bins=[0, 1000, 5000, 20000, float('inf')],
                                         labels=['Bronze (<1K)', 'Silver (1-5K)', 'Gold (5-20K)', 'Platinum (>20K)'])
        
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Customer LTV", f"KES {customer_ltv['total_spent'].mean():,.0f}")
            with col2:
                st.metric("Best Customer", f"KES {customer_ltv['total_spent'].max():,.0f}")
            with col3:
                st.metric("Avg Orders/Customer", f"{customer_ltv['order_count'].mean():.1f}")
            with col4:
                st.metric("Customer Segments", len(customer_ltv['Segment'].unique()))
        
        # LTV Distribution
            fig = px.histogram(customer_ltv, x='total_spent', nbins=30, 
                          title='Customer Lifetime Value Distribution',
                          labels={'total_spent': 'Total Spent (KES)', 'count': 'Number of Customers'},
                          color_discrete_sequence=['#36B37E'])
            fig.update_layout(bargap=0.1, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # ============================================
        # 3. RFM ANALYSIS (Recency, Frequency, Monetary)
        # ============================================
            st.markdown("#### 🎯 RFM Analysis (Best Customers)")
        
            current_date = sales_df['Date'].max()
            rfm = sales_df.groupby('Name').agg({
            'Date': lambda x: (current_date - x.max()).days,
            'Total': ['count', 'sum']
        })
            rfm.columns = ['Recency', 'Frequency', 'Monetary']
            rfm = rfm.reset_index()
        
        # Top customers by Monetary
            st.subheader("🏆 Top 10 Customers (By Total Spend)")
            top_customers = rfm.nlargest(10, 'Monetary')[['Name', 'Recency', 'Frequency', 'Monetary']]
            top_customers['Monetary'] = top_customers['Monetary'].apply(lambda x: f"KES {x:,.0f}")
            top_customers['Recency'] = top_customers['Recency'].apply(lambda x: f"{x} days ago")
            st.dataframe(top_customers, use_container_width=True, hide_index=True)
        
        # ============================================
        # 4. PRODUCT PERFORMANCE & MARGIN ANALYSIS
        # ============================================
            st.markdown("#### 📦 Product Performance & Margin Analysis")
        
        # Get product costs (you can adjust these)
            product_costs = {
            'Sachet - Standard (5 KES)': 1.5,
            'Sachet - Premium (30 KES)': 8.0,
            'Bottle (100g New)': 60.0,
            'Bottle (120g Refill)': 50.0
        }
        
            if 'Product_Type' in sales_df.columns:
                sales_df['Cost'] = sales_df['Product_Type'].map(product_costs).fillna(sales_df['Price_per_Unit'] * 0.3)
                sales_df['Margin'] = sales_df['Total'] - (sales_df['Quantity'] * sales_df['Cost'])
                sales_df['Margin_Percentage'] = (sales_df['Margin'] / sales_df['Total']) * 100
            
                product_margin = sales_df.groupby('Product_Type').agg({
                'Total': 'sum',
                'Margin': 'sum',
                'Quantity': 'sum'
            }).reset_index()
            
                product_margin['Margin_Percentage'] = (product_margin['Margin'] / product_margin['Total']) * 100
            
                col1, col2 = st.columns(2)
            
                with col1:
                    fig = px.bar(product_margin, x='Product_Type', y='Total', 
                            title='Revenue by Product',
                            color='Margin_Percentage',
                            color_continuous_scale='RdYlGn',
                            text='Total')
                    fig.update_traces(texttemplate='KES %{text:,.0f}', textposition='outside')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
                with col2:
                    fig = px.bar(product_margin, x='Product_Type', y='Margin_Percentage',
                            title='Gross Margin % by Product',
                            color='Margin_Percentage',
                            color_continuous_scale='RdYlGn',
                            range_y=[0, 100])
                    fig.add_hline(y=50, line_dash="dash", line_color="red", 
                            annotation_text="Target 50%", annotation_position="bottom right")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
        
        # ============================================
        # 5. SEASONALITY & FORECASTING
        # ============================================
            st.markdown("#### 📅 Seasonality & Forecasting")
        
            sales_df['Week'] = sales_df['Date'].dt.isocalendar().week
            sales_df['Month'] = sales_df['Date'].dt.month_name()
            sales_df['Quarter'] = sales_df['Date'].dt.quarter
        
            col1, col2 = st.columns(2)
        
            with col1:
                monthly_sales = sales_df.groupby('Month')['Total'].sum().reindex(
                ['January', 'February', 'March', 'April', 'May', 'June', 
                 'July', 'August', 'September', 'October', 'November', 'December']
            ).reset_index()
                fig = px.bar(monthly_sales, x='Month', y='Total', 
                        title='Seasonal Pattern - Monthly Sales',
                        color='Total', color_continuous_scale='Viridis')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
            with col2:
                quarterly_sales = sales_df.groupby('Quarter')['Total'].sum().reset_index()
                fig = px.line(quarterly_sales, x='Quarter', y='Total', 
                         title='Quarterly Growth Trend',
                         markers=True, line_shape='spline')
                fig.update_traces(line=dict(color='#FF9800', width=3))
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Simple forecast (without sklearn to avoid dependency issues)
            if len(sales_df) > 30:
                from sklearn.linear_model import LinearRegression
            try:
                    daily_sales = sales_df.groupby('Date')['Total'].sum().reset_index()
                    daily_sales['Days'] = (daily_sales['Date'] - daily_sales['Date'].min()).dt.days
                
                    X = daily_sales['Days'].values.reshape(-1, 1)
                    y = daily_sales['Total'].values
                
                    model = LinearRegression()
                    model.fit(X, y)
                
                    future_days = np.array(range(X[-1][0] + 1, X[-1][0] + 31)).reshape(-1, 1)
                    predictions = model.predict(future_days)
                
                    st.subheader("🔮 30-Day Sales Forecast")
                    st.metric("Projected Next 30 Days", f"KES {predictions.sum():,.0f}")
                
                    forecast_df = pd.DataFrame({
                    'Date': pd.date_range(start=daily_sales['Date'].max() + timedelta(days=1), periods=30),
                    'Forecast': predictions
                })
                
                    fig = px.line(forecast_df, x='Date', y='Forecast', 
                             title='Sales Forecast - Next 30 Days',
                             markers=True)
                    fig.update_traces(line=dict(color='#4CAF50', width=3))
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                    st.info(f"Forecast not available: {str(e)}")
        
        # ============================================
        # 6. EXECUTIVE SUMMARY (Shark Tank Style)
        # ============================================
            st.markdown("---")
            st.markdown("## 🎯 Executive Summary")
        
            col1, col2 = st.columns(2)
        
            with col1:
                st.markdown("### 📈 Growth Metrics")
            # Calculate revenue growth
                daily_sales_ordered = sales_df.sort_values('Date')
                if len(daily_sales_ordered) > 1:
                    recent_avg = daily_sales_ordered.tail(7)['Total'].mean() if len(daily_sales_ordered) >= 7 else daily_sales_ordered['Total'].mean()
                    previous_avg = daily_sales_ordered.head(7)['Total'].mean() if len(daily_sales_ordered) >= 7 else daily_sales_ordered['Total'].mean()
                    growth = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0
                    st.write(f"• **Revenue Growth:** {growth:.1f}% (last 7 days vs first 7 days)")
                else:
                    st.write(f"• **Revenue Growth:** N/A (need more data)")
            
                repeat_customers = len(customer_ltv[customer_ltv['order_count'] > 1]) if len(customer_ltv) > 0 else 0
                st.write(f"• **Customer Retention:** {(repeat_customers / len(customer_ltv) * 100):.1f}% repeat rate" if len(customer_ltv) > 0 else "• **Customer Retention:** N/A")
                st.write(f"• **Average Order Value:** KES {kpis['avg_sale_value']:,.0f}")
            
                if 'product_margin' in locals() and not product_margin.empty:
                    best_product = product_margin.loc[product_margin['Total'].idxmax(), 'Product_Type']
                    st.write(f"• **Best Performing Product:** {best_product}")
        
            with col2:
                st.markdown("### 💎 Key Insights")
            
            # Generate insights
                insights = []
                if kpis['cash_percentage'] < 50:
                    insights.append("🔴 Too much credit - tighten payment terms")
                if len(customer_ltv[customer_ltv['order_count'] == 1]) / len(customer_ltv) > 0.6 if len(customer_ltv) > 0 else False:
                    insights.append("🟡 Low customer retention - implement loyalty program")
                if 'Margin_Percentage' in locals() and not product_margin.empty and product_margin['Margin_Percentage'].min() < 20:
                    insights.append("🟠 Low margin on some products - review pricing")
            
                if len(customer_ltv) > 0:
                    best_segment = customer_ltv['Segment'].mode().iloc[0] if not customer_ltv.empty else 'N/A'
                    insights.append(f"🟢 Most valuable segment: {best_segment} customers")
            
                if kpis['total_sales'] > 0:
                    insights.append(f"💰 Total revenue: KES {kpis['total_sales']:,.0f}")
                    insights.append(f"📈 Net profit margin: {(kpis['net_profit']/kpis['total_sales']*100):.1f}%" if kpis['total_sales'] > 0 else "📈 Net profit margin: N/A")
            
                for insight in insights[:4]:
                    st.write(f"• {insight}")
    
        else:
            st.info("Not enough sales data for advanced analytics. Add some sales to see insights!")

# ==================== TAB 6: PRODUCTION & INVENTORY ====================
with tab6:
    st.markdown('<div class="section-header">🏭 Production & Inventory Management</div>', unsafe_allow_html=True)
    
    # Sub-tabs for Production and Inventory
    prod_tab1, prod_tab2, prod_tab3, prod_tab4, prod_tab5 = st.tabs([
        "📦 New Production Batch", 
        "📊 Batch History", 
        "📦 Raw Materials", 
        "📦 Finished Goods",
        "📈 Inventory Reports"  # NEW TAB
    ])
    
    # ========== TAB 1: NEW PRODUCTION BATCH ==========
    with prod_tab1:
        st.markdown("### 📦 Create New Production Batch")
        
        # Check material availability first
        st.subheader("🔍 Material Availability Check")
        materials = get_raw_materials()
        if materials:
            df_check = pd.DataFrame(materials)
            df_check = df_check[['material_name', 'current_stock_kg', 'reorder_level']]
            df_check.columns = ['Material', 'Current Stock (KG)', 'Reorder Level']
            st.dataframe(df_check, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            batch_number = st.text_input("Batch Number", placeholder="e.g., BATCH-001", key="batch_num")
            production_date = st.date_input("Production Date", value=date.today(), key="prod_date")
            total_kg = st.number_input("Total KG Produced", min_value=0.5, step=0.5, value=2.0, key="total_kg")
        
        with col2:
            st.markdown("### 📊 Recipe Formula")
            st.info("""
            **Standard Recipe (per batch):**
            - Salt: 50%
            - African Birds Eye: 30%
            - Cayenne Pepper: 15%
            - Onion Powder: 2%
            - Garlic Powder: 2%
            - Paprika: 1%
            """)
        
        # Calculate ingredient quantities
        salt_kg = total_kg * 0.50
        birds_eye_kg = total_kg * 0.30
        cayenne_kg = total_kg * 0.15
        onion_kg = total_kg * 0.02
        garlic_kg = total_kg * 0.02
        paprika_kg = total_kg * 0.01
        
        # Check if enough stock is available
        st.markdown("### 📊 Material Requirements & Availability")
        
        materials_needed = {
            'Salt': salt_kg,
            'African Birds Eye': birds_eye_kg,
            'Cayenne Pepper': cayenne_kg,
            'Onion Powder': onion_kg,
            'Garlic Powder': garlic_kg,
            'Paprika': paprika_kg
        }
        
        sufficient_stock = True
        for mat_name, needed in materials_needed.items():
            mat_data = next((m for m in materials if m['material_name'] == mat_name), None)
            if mat_data:
                current = mat_data['current_stock_kg']
                status = "✅" if current >= needed else "❌"
                if current < needed:
                    sufficient_stock = False
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"{status} **{mat_name}:**")
                with col2:
                    st.write(f"Needed: {needed:.2f} kg")
                with col3:
                    st.write(f"Available: {current:.2f} kg")
        
        if not sufficient_stock:
            st.error("⚠️ **Insufficient materials!** Please restock before producing this batch.")
        
        st.markdown("### 🏭 Finished Goods Production")
        st.write("How many units did this batch produce?")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            sachet_5_qty = st.number_input("5 KES Sachets", min_value=0, step=50, value=0, key="sachet_5")
        with col2:
            sachet_30_qty = st.number_input("30 KES Sachets", min_value=0, step=20, value=0, key="sachet_30")
        with col3:
            bottle_100g_qty = st.number_input("100g Bottles (KES 150)", min_value=0, step=10, value=0, key="bottle_100")
        with col4:
            refill_120g_qty = st.number_input("120g Refills (KES 120)", min_value=0, step=10, value=0, key="refill_120")
        
        total_units = sachet_5_qty + sachet_30_qty + bottle_100g_qty + refill_120g_qty
        st.info(f"📦 **Total Units Produced:** {total_units:,}")
        
        notes = st.text_area("Production Notes", placeholder="Any issues or observations?", key="prod_notes")
        
        if st.button("✅ Save Production Batch", type="primary", use_container_width=True):
            if not batch_number:
                st.error("Please enter a batch number!")
            elif total_units == 0:
                st.warning("Please enter at least one finished good quantity!")
            else:
                # Save batch
                materials_needed = {
            'Salt': total_kg * 0.50,
            'African Birds Eye': total_kg * 0.30,
            'Cayenne Pepper': total_kg * 0.15,
            'Onion Powder': total_kg * 0.02,
            'Garlic Powder': total_kg * 0.02,
            'Paprika': total_kg * 0.01
        }
            sufficient = True
            for mat_name, needed in materials_needed.items():
                current = get_current_material_balance(mat_name)
                if current < needed:
                    st.error(f"Insufficient {mat_name}. Need {needed:.2f}kg, have {current:.2f}kg")
                    sufficient = False
            if sufficient:
            # Save batch
                batch_data = {
                "batch_number": batch_number,
                "production_date": str(production_date),
                "total_kg_produced": total_kg,
                "salt_kg": salt_kg,
                "african_birds_eye_kg": birds_eye_kg,
                "cayenne_kg": cayenne_kg,
                "onion_powder_kg": onion_kg,
                "garlic_powder_kg": garlic_kg,
                "paprika_kg": paprika_kg,
                "status": "Completed",
                "notes": notes
            }
                
                
                    
            batch_id = save_batch(batch_data)
            
            if batch_id:
                # Record material usage for each ingredient
                for mat_name, needed in materials_needed.items():
                    record_material_usage_with_balance(batch_id, mat_name, needed, production_date)
                
                # Save production outputs
                outputs = [
                    ("Sachet 5", sachet_5_qty, 5),
                    ("Sachet 30", sachet_30_qty, 30),
                    ("Bottle 100g", bottle_100g_qty, 150),
                    ("Refill 120g", refill_120g_qty, 120)
                ]
                
                for product_type, qty, price in outputs:
                    if qty > 0:
                        save_production_output({
                            "batch_id": batch_id,
                            "product_type": product_type,
                            "quantity_produced": qty,
                            "unit_price": price
                        })
                
                st.success(f"✅ Batch {batch_number} saved successfully!")
                st.balloons()
                st.rerun()
            else:
                st.error("Failed to save batch!")
    
    # ========== TAB 2: BATCH HISTORY ==========
    with prod_tab2:
        st.markdown("### 📊 Batch History")
        
        batches = get_batches()
        if batches:
            df_batches = pd.DataFrame(batches)
            df_batches['production_date'] = pd.to_datetime(df_batches['production_date']).dt.strftime('%Y-%m-%d')
            st.dataframe(df_batches[['batch_number', 'production_date', 'total_kg_produced', 'status']], use_container_width=True, hide_index=True)
            
            # Batch detail view with material usage
            st.markdown("### 🔍 Batch Details with Material Usage")
            selected_batch = st.selectbox("Select Batch", [b['batch_number'] for b in batches], key="select_batch")
            batch_detail = next((b for b in batches if b['batch_number'] == selected_batch), None)
            
            if batch_detail:
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Batch Number:** {batch_detail['batch_number']}")
                    st.write(f"**Production Date:** {batch_detail['production_date']}")
                    st.write(f"**Total KG:** {batch_detail['total_kg_produced']} kg")
                with col2:
                    st.write(f"**Status:** {batch_detail['status']}")
                    st.write(f"**Notes:** {batch_detail.get('notes', 'N/A')}")
                
                # Show material usage for this batch
                usage_summary = get_material_usage_summary(batch_detail['id'])
                try:
                    usage_summary = get_material_usage_summary(batch_detail['id'])
                    if not usage_summary.empty:
                        st.write("**Materials Used in this Batch:**")
                        st.dataframe(usage_summary, use_container_width=True, hide_index=True)
                except Exception as e:
                    st.write("No material usage data available for this batch")
                
                st.write("**Ingredients Used:**")
                ing_data = {
                    'Ingredient': ['Salt', 'African Birds Eye', 'Cayenne Pepper', 'Onion Powder', 'Garlic Powder', 'Paprika'],
                    'KG Used': [
                        batch_detail.get('salt_kg', 0),
                        batch_detail.get('african_birds_eye_kg', 0),
                        batch_detail.get('cayenne_kg', 0),
                        batch_detail.get('onion_powder_kg', 0),
                        batch_detail.get('garlic_powder_kg', 0),
                        batch_detail.get('paprika_kg', 0)
                    ]
                }
                st.dataframe(pd.DataFrame(ing_data), use_container_width=True, hide_index=True)
        else:
            st.info("No batches recorded yet. Create your first production batch!")
    
    # ========== TAB 3: RAW MATERIALS INVENTORY ==========
    with prod_tab3:
        st.markdown("### 📦 Raw Materials Inventory")
        
        # Restock section with date tracking
        with st.expander("➕ Restock Raw Materials", expanded=True):
            materials = get_raw_materials()
            material_list = [m['material_name'] for m in materials] if materials else []
    
            col1, col2, col3 = st.columns(3)
            with col1:
                restock_material = st.selectbox("Material", material_list, key="restock_material")
            with col2:
                restock_qty = st.number_input("Quantity (KG)", min_value=0.5, step=0.5, value=5.0, key="restock_qty")
            with col3:
                restock_cost = st.number_input("Cost per KG (KES)", min_value=0, step=10, value=100, key="restock_cost")
    
            col1, col2 = st.columns(2)
            with col1:
                restock_date = st.date_input("Restock Date", value=date.today(), key="restock_date")
                supplier = st.text_input("Supplier Name", key="supplier")
            with col2:
                delivery_note = st.text_input("Reference / Invoice #", key="delivery_note")
    
            restock_notes = st.text_area("Notes", key="restock_notes")
    
            if st.button("💾 Record Restock", type="primary", key="record_restock"):
                if restock_material and restock_qty > 0:
                    success = record_restock_with_balance(
                restock_material, 
                restock_qty, 
                restock_cost, 
                supplier if supplier else "Unknown", 
                restock_date, 
                restock_notes
            )
                if success:
                    st.rerun()
            else:
                st.error("Please fill in all required fields")
        
        # Current inventory display with more details
        materials = get_raw_materials()
        if materials:
            df_materials = pd.DataFrame(materials)
            df_materials['current_stock_kg'] = df_materials['current_stock_kg'].round(2)
            df_materials['unit_cost'] = df_materials['unit_cost'].apply(lambda x: f"KES {x:,.0f}")
            
            st.dataframe(df_materials[['material_name', 'current_stock_kg', 'unit_cost', 'reorder_level', 'last_restock_date']], 
                        use_container_width=True, hide_index=True)
            
            # Stock alerts
            low_stock = df_materials[df_materials['current_stock_kg'] < df_materials['reorder_level']]
            if not low_stock.empty:
                st.warning("⚠️ **Low Stock Alert!** The following materials need restocking:")
                for _, item in low_stock.iterrows():
                    st.write(f"- {item['material_name']}: {item['current_stock_kg']:.1f} KG (Reorder at {item['reorder_level']} KG)")
            
            # Stock usage chart
            st.markdown("### 📊 Material Stock Levels")
            fig = px.bar(df_materials, x='material_name', y='current_stock_kg', 
                        title='Current Raw Materials Stock',
                        color='current_stock_kg', color_continuous_scale='RdYlGn',
                        text='current_stock_kg')
            fig.add_hline(y=10, line_dash="dash", line_color="red", annotation_text="Reorder Alert (10 KG)")
            fig.update_traces(texttemplate='%{text:.1f} KG', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No raw materials data")
    
    # ========== TAB 4: FINISHED GOODS ==========
    with prod_tab4:
        st.markdown("### 📦 Finished Goods Inventory")
        
        finished_goods = get_finished_goods()
        if finished_goods:
            df_finished = pd.DataFrame(finished_goods)
            st.dataframe(df_finished[['product_type', 'current_stock', 'unit_price', 'reorder_level']], use_container_width=True, hide_index=True)
            
            # Stock alerts for finished goods
            low_stock_fg = df_finished[df_finished['current_stock'] < df_finished['reorder_level']]
            if not low_stock_fg.empty:
                st.warning("⚠️ **Low Stock Alert!** The following products need production:")
                for _, item in low_stock_fg.iterrows():
                    st.write(f"- {item['product_type']}: {item['current_stock']} units (Reorder at {item['reorder_level']} units)")
            
            # Inventory chart
            fig = px.bar(df_finished, x='product_type', y='current_stock', 
                        title='Current Finished Goods Inventory',
                        color='current_stock', color_continuous_scale='Viridis',
                        text='current_stock')
            fig.update_traces(texttemplate='%{text} units', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
    
    # ========== TAB 5: INVENTORY REPORTS ==========
    with prod_tab5:
        st.markdown("### 📈 Inventory Movement Reports")
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            report_start = st.date_input("Start Date", value=date.today() - timedelta(days=30), key="report_start")
        with col2:
            report_end = st.date_input("End Date", value=date.today(), key="report_end")
        
        # Material filter
        materials = get_raw_materials()
        material_names = [m['material_name'] for m in materials] if materials else []
        selected_material = st.selectbox("Select Material (or All)", ["All"] + material_names, key="report_material")
        
        # Get transactions
        material_filter = None if selected_material == "All" else selected_material
        transactions = get_inventory_transactions(material_filter, report_start, report_end)
        
        if transactions:
            df_trans = pd.DataFrame(transactions)
            df_trans['transaction_date'] = pd.to_datetime(df_trans['transaction_date']).dt.strftime('%Y-%m-%d')
            
            st.dataframe(df_trans[['transaction_date', 'transaction_type', 'material_name', 'quantity_kg', 'cost_per_kg', 'total_value', 'notes']], 
                        use_container_width=True, hide_index=True)
            
            # Summary statistics
            st.markdown("### 📊 Inventory Summary")
            
            restock_total = sum([t['quantity_kg'] for t in transactions if t['transaction_type'] == 'RESTOCK'])
            usage_total = sum([abs(t['quantity_kg']) for t in transactions if t['transaction_type'] == 'USAGE'])
            net_change = restock_total - usage_total
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Restocked", f"{restock_total:.1f} KG")
            with col2:
                st.metric("Total Used", f"{usage_total:.1f} KG")
            with col3:
                st.metric("Net Change", f"{net_change:.1f} KG", delta=f"{net_change:.1f}" if net_change != 0 else None)
            
            # Chart: Stock movement over time
            if len(transactions) > 0:
                # Calculate running balance
                df_trans_sorted = sorted(transactions, key=lambda x: x['transaction_date'])
                balance = 0
                dates = []
                balances = []
                for trans in df_trans_sorted:
                    if trans['transaction_type'] == 'RESTOCK':
                        balance += trans['quantity_kg']
                    else:
                        balance -= trans['quantity_kg']
                    dates.append(trans['transaction_date'])
                    balances.append(balance)
                
                balance_df = pd.DataFrame({'Date': dates, 'Balance (KG)': balances})
                fig = px.line(balance_df, x='Date', y='Balance (KG)', 
                             title=f'Stock Level Over Time - {selected_material if selected_material != "All" else "All Materials"}',
                             markers=True)
                fig.update_traces(line=dict(color='#4CAF50', width=3))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No inventory transactions in selected period")
# ==================== TAB 7: FUNDING & CAPITAL ====================
with tab7:
    st.markdown('<div class="section-header">💰 Funding & Capital Management</div>', unsafe_allow_html=True)
    
    # Display total funding
    total_funding = get_total_funding()
    total_sales = kpis['total_sales']
    net_capital = total_funding + total_sales - kpis['total_expenses']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Funding Received", f"KES {total_funding:,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Sales Revenue", f"KES {total_sales:,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Net Capital Position", f"KES {net_capital:,.0f}")
        st.caption("Funding + Sales - Expenses")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Add new funding section
    with st.expander("➕ Add New Funding / Investment", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            funding_date = st.date_input("Funding Date", value=date.today(), key="funding_date")
            funding_source = st.text_input("Source", placeholder="e.g., Grandma, Bank, Investor", key="funding_source")
            funding_amount = st.number_input("Amount (KES)", min_value=0, step=1000, value=0, key="funding_amount")
        
        with col2:
            funding_type = st.selectbox("Funding Type", ["Investment", "Loan", "Grant", "Personal Capital"], key="funding_type")
            funding_status = st.selectbox("Status", ["Received", "Pending", "Expected"], key="funding_status")
            funding_description = st.text_area("Description", placeholder="Purpose of funding...", key="funding_description")
        
        if st.button("💾 Record Funding", type="primary", use_container_width=True):
            if funding_source and funding_amount > 0:
                funding_data = {
                    "funding_date": str(funding_date),
                    "source": funding_source,
                    "amount": funding_amount,
                    "funding_type": funding_type,
                    "description": funding_description,
                    "status": funding_status
                }
                funding_id = save_funding(funding_data)
                if funding_id:
                    st.success(f"✅ Recorded {funding_type} of KES {funding_amount:,.0f} from {funding_source}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to record funding")
            else:
                st.warning("Please enter source and amount")
    
    # Display funding history
    st.markdown("### 📋 Funding History")
    funding_records = get_funding()
    
    if funding_records:
        df_funding = pd.DataFrame(funding_records)
        df_funding['funding_date'] = pd.to_datetime(df_funding['funding_date']).dt.strftime('%Y-%m-%d')
        df_funding['amount'] = df_funding['amount'].apply(lambda x: f"KES {x:,.0f}")
        
        st.dataframe(df_funding[['funding_date', 'source', 'amount', 'funding_type', 'description', 'status']], 
                    use_container_width=True, hide_index=True)
        
        # Funding chart
        fig = px.bar(df_funding, x='source', y=df_funding['amount'].str.replace('KES ', '').str.replace(',', '').astype(float),
                    title='Funding by Source',
                    color='funding_type',
                    text='amount')
        fig.update_traces(textposition='outside')
        fig.update_layout(yaxis_title='Amount (KES)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No funding records yet. Add your first funding source above!")
    
    # Capital position chart
    st.markdown("### 📊 Capital Position")
    
    capital_data = pd.DataFrame({
        'Category': ['Total Funding', 'Total Sales', 'Total Expenses', 'Net Capital'],
        'Amount': [total_funding, total_sales, kpis['total_expenses'], net_capital]
    })
    
    fig = px.bar(capital_data, x='Category', y='Amount', 
                title='Business Capital Position',
                color='Category',
                text='Amount')
    fig.update_traces(texttemplate='KES %{text:,.0f}', textposition='outside')
    fig.update_layout(yaxis_title='Amount (KES)')
    st.plotly_chart(fig, use_container_width=True)
    
    # Business Health Summary
    st.markdown("### 📈 Business Health Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if total_funding > 0:
            roi = ((total_sales - kpis['total_expenses']) / total_funding) * 100
            st.metric("Return on Investment (ROI)", f"{roi:.1f}%")
        
        if total_funding > 0:
            capital_used = kpis['total_expenses'] / total_funding * 100
            st.metric("Capital Used", f"{capital_used:.1f}%")
    
    with col2:
        if total_sales > 0:
            profit_margin = (kpis['net_profit'] / total_sales) * 100
            st.metric("Profit Margin", f"{profit_margin:.1f}%")
        
        st.metric("Cash Balance vs Funding", f"{(kpis['running_balance'] / total_funding * 100):.1f}%" if total_funding > 0 else "N/A")

# Footer
st.markdown("---")
st.caption(f"🌶️ SpiseUp Finance Tracker • Data range: {start_date} to {end_date} • {len(sales_df)} sales • {len(expenses_df)} expenses")