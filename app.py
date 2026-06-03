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
    get_all_hotels,
    get_all_mama_mbogas,
    get_current_material_balance,
    get_hotel_refills,
    record_restock_with_balance,
    save_hotel,
    save_hotel_refill,
    save_mama_mboga,
    save_mama_purchase,
    save_mama_purchase,
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
    get_inventory_balance_history,
    update_finished_goods_production,
    update_finished_goods_sale,
    save_asset,
    get_assets,
    delete_asset,
    update_asset,
     save_daily_stock_reconciliation,
    get_daily_stock_reconciliation,
    get_daily_summary,
    save_hotel,
    get_all_hotels,
    save_hotel_refill,
    get_hotel_refills,
    save_mama_mboga,
    get_all_mama_mbogas,
    save_mama_purchase,
    get_mama_purchases
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

PRODUCT_LIST = [
    "SpiseUp Spicy Salt Sachet (5 KES) - Consumer",
    "SpiseUp Spicy Salt Sachet (2.9 KES) - Wholesale",
    "SpiseUp Spicy Salt Sachet (30 KES)",
    "SpiseUp Spicy Salt Bottle (100g New)",
    "SpiseUp Spicy Salt Bottle (100g Refill)",
    "SpiseUp Hot Sauce"
]

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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14  = st.tabs([
    "📊 Dashboard", 
    "💰 Sales", 
    "💸 Expenses", 
    "👥 Salespeople", 
    "📈 Analytics",
     "🏭 Production & Inventory",
     "💰 Funding & Capital",
     "🏭 Assets & Equipment",
     "📝 Daily Sales Entry",
     "📊 Stock Reconciliation",
     "💰 Profit Calculator",
     "🏥 Business Health",
     "INVOICE SYSTEM ",
     "🎁 Free Items & Giveaways"
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
            st.plotly_chart(fig, width='stretch')
        
        # Chart 2: Sales Trend with Moving Average
        if not sales_by_date.empty and len(sales_by_date) > 3:
            sales_by_date['7_Day_MA'] = sales_by_date['Total'].rolling(window=min(7, len(sales_by_date))).mean()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=sales_by_date['Date'], y=sales_by_date['Total'], name='Daily Sales', mode='lines+markers', line=dict(color='#1565C0', width=2), marker=dict(size=6)))
            fig.add_trace(go.Scatter(x=sales_by_date['Date'], y=sales_by_date['7_Day_MA'], name='7-Day Moving Average', line=dict(color='#FF9800', width=3, dash='dash')))
            fig.update_layout(title='Sales Trend with Moving Average', xaxis_title='Date', yaxis_title='Sales (KES)', hovermode='x unified')
            st.plotly_chart(fig, width='stretch')
        
        # Chart 3: Cumulative Sales
        if not sales_by_date.empty:
            sales_by_date['Cumulative Sales'] = sales_by_date['Total'].cumsum()
            fig = px.area(sales_by_date, x='Date', y='Cumulative Sales', title='Cumulative Sales Over Time', color_discrete_sequence=['#4CAF50'])
            fig.update_layout(xaxis_title='Date', yaxis_title='Cumulative Sales (KES)')
            st.plotly_chart(fig, width='stretch')
    
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
            
            # Pricing logic based on selections
            if product_main == "Sachet - Standard (5 KES)":
                if customer_type == "Consumer (B2C)":
                    price, min_qty, default_qty, unit = 5.0, 1, 1, "sachets"
                    product_name = "SpiseUp Spicy Salt Sachet (5 KES) - Consumer"
                elif customer_type == "Shop/Mama Mboga (B2B)":
                    price, min_qty, default_qty, unit = 2.9, 18, 18, "sachets"
                    product_name = "SpiseUp Spicy Salt Sachet (2.9 KES) - Wholesale"
                else:
                    price, min_qty, default_qty, unit = 2.9, 18, 18, "sachets"
                    product_name = "SpiseUp Spicy Salt Sachet (2.9 KES) - Hotel"
            elif product_main == "Sachet - Premium (30 KES)":
                price, min_qty, default_qty, unit = 30.0, 1, 1, "sachets"
                product_name = f"SpiseUp Spicy Salt Sachet (30 KES) - {customer_type}"
            elif product_main == "Bottle (100g New)":
                if customer_type == "Consumer (B2C)":
                    price, min_qty, default_qty, unit = 150.0, 1, 1, "bottles"
                    product_name = "SpiseUp Spicy Salt Bottle (100g New) - Consumer"
                elif customer_type == "Shop/Mama Mboga (B2B)":
                    price, min_qty, default_qty, unit = 150.0, 1, 1, "bottles"
                    product_name = "SpiseUp Spicy Salt Bottle (100g New) - Wholesale"
                else:
                    price, min_qty, default_qty, unit = 150.0, 1, 1, "bottles"
                    product_name = "SpiseUp Spicy Salt Bottle (100g New) - Hotel"
            else:
                price, min_qty, default_qty, unit = 120.0, 1, 1, "refills"
                product_name = f"SpiseUp Spicy Salt Bottle (100g Refill) - {customer_type}"
                st.success("🔄 **REFILL BENEFIT:** Pay KES 120 and get 100g (save KES 30!)")
            
            if min_qty > 1:
                st.info(f"📦 Minimum order: {min_qty} {unit}")
            
            quantity = st.number_input(f"Quantity ({unit})", min_value=min_qty, step=min_qty if min_qty > 1 else 1, value=default_qty)
            price = st.number_input("Price per unit (KES)", min_value=0.0, max_value=500.0, step=1.0, value=float(price), format="%.1f")
            total = quantity * price
            st.success(f"**Total Amount:** KES {total:,.2f}")
            
            # Hotel Tracking
            hotel_name = None
            if customer_type == "Hotel/Restaurant":
                st.markdown("---")
                st.subheader("🏨 Hotel Tracking")
                hotel_name = st.text_input("Hotel Name", placeholder="Enter hotel name", key="hotel_track")
                if hotel_name:
                    refill_count = st.number_input("Times refilled this month", min_value=0, value=1, key="refill_count")
                    if refill_count > 0:
                        avg_days = 30 / refill_count
                        if avg_days < 7:
                            st.success("🔥 High frequency customer!")
                        elif avg_days < 14:
                            st.info("📈 Medium frequency")
                        else:
                            st.warning("⏰ Low frequency - consider follow-up")
            
            # Mama Mboga Tracking
            mama_name = None
            if customer_type == "Shop/Mama Mboga (B2B)":
                st.markdown("---")
                st.subheader("🏪 Mama Mboga/Shop Tracking")
                mama_name = st.text_input("Mama Mboga/Shop Name", placeholder="Enter shop name", key="mama_track")
                if mama_name:
                    st.caption("💡 They buy at KES 2.9, sell at KES 5 - KES 2.1 profit per sachet")
            
            # Payment Status
            payment_status = st.selectbox("Payment Status", ["Cash", "Credit / Pending"])
            
            # Sales Person selection
            if sales_person_options:
                sales_person_name = st.selectbox("Sales Person", ["Select..."] + list(sales_person_options.keys()))
            else:
                sales_person_name = "N/A"
                st.warning("No salespeople added yet.")
            
            # Additional Details - NOW INSIDE the same block
            st.markdown("---")
            st.markdown("### 📝 Additional Details")
            feedback = st.text_area("Customer Feedback", placeholder="Any feedback from the customer...", key="feedback")
            follow_up = st.text_input("Follow-up Action", placeholder="Next steps or follow-up required...", key="follow_up")
            
            # Buttons
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                submitted_sale = st.button("💾 Save Sale", type="primary", use_container_width=True)
            with col_btn2:
                clear_form = st.button("🗑️ Clear Form", use_container_width=True)
    
    # Clear form logic (outside columns but using session state)
    if clear_form:
        for key in ['shop_name', 'phone', 'location', 'quantity', 'price', 'payment_status', 'sales_person_name', 'feedback', 'follow_up']:
            if key in st.session_state:
                del st.session_state[key]
        st.success("✅ Form cleared!")
        st.rerun()
    
    # Save sale logic
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
                
                # Map product for inventory
                product_mapping = {
                    "SpiseUp Spicy Salt Sachet (5 KES) - Consumer": "Sachet 5",
                    "SpiseUp Spicy Salt Sachet (5 KES) - Wholesale": "Sachet 5",
                    "SpiseUp Spicy Salt Sachet (5 KES) - Hotel": "Sachet 5",
                    "SpiseUp Spicy Salt Sachet (30 KES)": "Sachet 30",
                    "SpiseUp Spicy Salt Bottle (100g New) - Consumer": "Bottle 100g",
                    "SpiseUp Spicy Salt Bottle (100g New) - Wholesale": "Bottle 100g",
                    "SpiseUp Spicy Salt Bottle (100g New) - Hotel": "Bottle 100g",
                    "SpiseUp Spicy Salt Bottle (100g Refill)": "Refill 100g"
                }
                
                base_product = product_name.split(' - ')[0] if ' - ' in product_name else product_name
                mapped_product = product_mapping.get(base_product, None)
                
                if mapped_product:
                    update_finished_goods_sale(mapped_product, quantity)
                    st.caption(f"📦 Updated inventory: -{quantity} {mapped_product}(s)")
                
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
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            expenses_by_date = expenses_df.groupby('date')['amount'].sum().reset_index()
            fig = px.line(expenses_by_date, x='date', y='amount', title='Expense Trend Over Time', markers=True, line_shape='spline')
            fig.update_traces(line=dict(color='#FF4B4B', width=3))
            st.plotly_chart(fig, width='stretch')

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
    # ========== ENHANCED SALES TREND DASHBOARD ==========
    st.markdown("### 📊 Sales Performance Dashboard")

    if not sales_df.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            period = st.radio(
            "Select Time Period",
            ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"],
            horizontal=True
        )
        with col2:
            show_numbers = st.checkbox("Show exact numbers on charts", value=True)
    
    # Make sure Date is datetime
        sales_df['Date'] = pd.to_datetime(sales_df['Date'])
    
    # Calculate metrics based on selected period
        if period == "Daily":
        # Group by date
            sales_trend = sales_df.groupby('Date')['Total'].sum().reset_index()
            sales_trend.columns = ['Date', 'Sales']
            sales_trend['Day'] = sales_trend['Date'].dt.day_name()
        
            if len(sales_trend) == 0:
                st.warning("No daily sales data available")
            else:
            # Calculate daily average
                avg_daily = sales_trend['Sales'].mean()
                total_period = sales_trend['Sales'].sum()
                best_day = sales_trend.loc[sales_trend['Sales'].idxmax()]
                worst_day = sales_trend.loc[sales_trend['Sales'].idxmin()]
            
            # Create daily chart
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=sales_trend['Date'], 
                    y=sales_trend['Sales'], 
                    name='Daily Sales', 
                    marker_color='#36B37E',
                    text=sales_trend['Sales'].apply(lambda x: f'KES {x:,.0f}') if show_numbers else None,
                    textposition='outside'
            ))
                fig.add_hline(y=avg_daily, line_dash="dash", line_color="red", 
                         annotation_text=f"Avg: KES {avg_daily:,.0f}")
                fig.update_layout(
                title='Daily Sales Performance',
                xaxis_title='Date',
                yaxis_title='Sales (KES)',
                hovermode='x unified',
                height=450
            )
                st.plotly_chart(fig, width='stretch')
            
            # Show daily metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Avg Daily Sales", f"KES {avg_daily:,.0f}")
                with col2:
                    st.metric("🏆 Best Day", f"KES {best_day['Sales']:,.0f}")
                    st.caption(f"{best_day['Date'].strftime('%A, %b %d')}")
                with col3:
                    st.metric("📉 Worst Day", f"KES {worst_day['Sales']:,.0f}")
                    st.caption(f"{worst_day['Date'].strftime('%A, %b %d')}")
                with col4:
                    st.metric("💰 Total Period", f"KES {total_period:,.0f}")
    
        elif period == "Weekly":
        # Create week groupings
            sales_df['Year'] = sales_df['Date'].dt.year
            sales_df['Week_Number'] = sales_df['Date'].dt.isocalendar().week
            sales_df['Week_Label'] = sales_df.apply(lambda x: f"W{x['Week_Number']} ({x['Year']})", axis=1)
        
        # Group by week
            weekly_sales = sales_df.groupby(['Year', 'Week_Number', 'Week_Label'])['Total'].sum().reset_index()
            weekly_sales = weekly_sales.sort_values(['Year', 'Week_Number'])
        
            if len(weekly_sales) == 0:
                st.warning("No weekly sales data available")
            else:
            # Calculate weekly average
                avg_weekly = weekly_sales['Total'].mean()
                total_period = weekly_sales['Total'].sum()
                best_week = weekly_sales.loc[weekly_sales['Total'].idxmax()]
            
            # Weekly trend chart
                fig = go.Figure()
                fig.add_trace(go.Bar(
                x=weekly_sales['Week_Label'], 
                y=weekly_sales['Total'], 
                name='Weekly Sales',
                marker_color='#2196F3',
                text=weekly_sales['Total'].apply(lambda x: f'KES {x:,.0f}') if show_numbers else None,
                textposition='outside'
            ))
                fig.add_hline(y=avg_weekly, line_dash="dash", line_color="red",
                         annotation_text=f"Avg: KES {avg_weekly:,.0f}")
                fig.update_layout(
                title='Weekly Sales Performance',
                xaxis_title='Week',
                yaxis_title='Sales (KES)',
                height=450,
                xaxis_tickangle=-45
            )
                st.plotly_chart(fig, width='stretch')
            
            # Weekly metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Avg Weekly Sales", f"KES {avg_weekly:,.0f}")
                with col2:
                    st.metric("🏆 Best Week", f"KES {best_week['Total']:,.0f}")
                    st.caption(f"{best_week['Week_Label']}")
                with col3:
                    st.metric("💰 Total Period", f"KES {total_period:,.0f}")
            
            # Week-over-week growth
                if len(weekly_sales) >= 2:
                    weekly_sales['Growth'] = weekly_sales['Total'].pct_change() * 100
                    growth_df = weekly_sales.tail(8)[['Week_Label', 'Growth']].dropna()
                    if not growth_df.empty:
                        fig = px.bar(growth_df, x='Week_Label', y='Growth',
                                title='Week-over-Week Growth %',
                                color='Growth', color_continuous_scale='RdYlGn',
                                text='Growth')
                        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                        st.plotly_chart(fig, width='stretch')
    
        elif period == "Monthly":
        # Create month groupings
            sales_df['Year_Month'] = sales_df['Date'].dt.strftime('%Y-%m')
            sales_df['Month_Label'] = sales_df['Date'].dt.strftime('%B %Y')
        
        # Group by month
            monthly_sales = sales_df.groupby(['Year_Month', 'Month_Label'])['Total'].sum().reset_index()
            monthly_sales = monthly_sales.sort_values('Year_Month')
        
            if len(monthly_sales) == 0:
                st.warning("No monthly sales data available")
            else:
            # Calculate monthly average
                avg_monthly = monthly_sales['Total'].mean()
                total_period = monthly_sales['Total'].sum()
                best_month = monthly_sales.loc[monthly_sales['Total'].idxmax()]
            
            # Monthly chart
                fig = go.Figure()
                fig.add_trace(go.Bar(
                x=monthly_sales['Month_Label'], 
                y=monthly_sales['Total'], 
                name='Monthly Sales',
                marker_color='#4CAF50',
                text=monthly_sales['Total'].apply(lambda x: f'KES {x:,.0f}') if show_numbers else None,
                textposition='outside'
            ))
                fig.add_hline(y=avg_monthly, line_dash="dash", line_color="red",
                         annotation_text=f"Avg: KES {avg_monthly:,.0f}")
                fig.update_layout(
                title='Monthly Sales Performance',
                xaxis_title='Month',
                yaxis_title='Sales (KES)',
                height=450,
                xaxis_tickangle=-45
            )
                st.plotly_chart(fig, width='stretch')
            
            # Monthly metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Avg Monthly Sales", f"KES {avg_monthly:,.0f}")
                with col2:
                    st.metric("🏆 Best Month", f"KES {best_month['Total']:,.0f}")
                    st.caption(f"{best_month['Month_Label']}")
                with col3:
                    st.metric("💰 Total Period", f"KES {total_period:,.0f}")
            
            # Month-over-month growth
                if len(monthly_sales) >= 2:
                    monthly_sales['Growth'] = monthly_sales['Total'].pct_change() * 100
                    fig = px.line(monthly_sales, x='Month_Label', y='Growth',
                             title='Month-over-Month Growth Trend',
                             markers=True, line_shape='spline')
                    fig.add_hline(y=0, line_dash="dash", line_color="gray")
                    fig.update_traces(line=dict(color='#FF9800', width=3))
                    st.plotly_chart(fig, width='stretch')
    
        elif period == "Quarterly":
        # Create quarter groupings
            sales_df['Year_Quarter'] = sales_df['Date'].dt.to_period('Q').astype(str)
            sales_df['Quarter_Label'] = sales_df['Date'].dt.to_period('Q').astype(str)
        
        # Group by quarter
            quarterly_sales = sales_df.groupby(['Year_Quarter', 'Quarter_Label'])['Total'].sum().reset_index()
            quarterly_sales = quarterly_sales.sort_values('Year_Quarter')
        
            if len(quarterly_sales) == 0:
                st.warning("No quarterly sales data available")
            else:
                avg_quarterly = quarterly_sales['Total'].mean()
                total_period = quarterly_sales['Total'].sum()
            
                fig = px.bar(quarterly_sales, x='Quarter_Label', y='Total',
                        title='Quarterly Sales Performance',
                        color='Total', color_continuous_scale='Purples',
                        text='Total')
                fig.update_traces(texttemplate='KES %{text:,.0f}', textposition='outside')
                fig.add_hline(y=avg_quarterly, line_dash="dash", line_color="red",
                         annotation_text=f"Avg: KES {avg_quarterly:,.0f}")
                st.plotly_chart(fig, width='stretch')
            
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📊 Avg Quarterly Sales", f"KES {avg_quarterly:,.0f}")
                with col2:
                    st.metric("💰 Total Period", f"KES {total_period:,.0f}")
    
        else:  # Yearly
            sales_df['Year'] = sales_df['Date'].dt.year
            yearly_sales = sales_df.groupby('Year')['Total'].sum().reset_index()
        
            if len(yearly_sales) == 0:
                st.warning("No yearly sales data available")
            else:
                fig = px.bar(yearly_sales, x='Year', y='Total',
                        title='Yearly Sales Performance',
                        color='Total', color_continuous_scale='Reds',
                        text='Total')
                fig.update_traces(texttemplate='KES %{text:,.0f}', textposition='outside')
                st.plotly_chart(fig, width='stretch')
            
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("💰 Total Sales", f"KES {yearly_sales['Total'].sum():,.0f}")
                with col2:
                    if len(yearly_sales) >= 2:
                        growth = ((yearly_sales['Total'].iloc[-1] - yearly_sales['Total'].iloc[-2]) / yearly_sales['Total'].iloc[-2]) * 100
                        st.metric("📈 Year-over-Year Growth", f"{growth:.1f}%")
    
    # ========== CUMULATIVE SALES TRACKER ==========
        st.markdown("---")
        st.markdown("### 📈 Cumulative Sales Tracker")
    
        cumulative_sales = sales_df.sort_values('Date')
        cumulative_sales['Cumulative'] = cumulative_sales['Total'].cumsum()
    
        fig = go.Figure()
        fig.add_trace(go.Scatter(
        x=cumulative_sales['Date'], 
        y=cumulative_sales['Cumulative'],
        mode='lines',
        name='Total Sales',
        fill='tozeroy',
        line=dict(color='#4CAF50', width=3),
        hovertemplate='Date: %{x|%Y-%m-%d}<br>Total: KES %{y:,.0f}<extra></extra>'
    ))
        fig.update_layout(
        title='Cumulative Sales Over Time',
        xaxis_title='Date',
        yaxis_title='Cumulative Sales (KES)',
        height=400,
        hovermode='x unified'
    )
        st.plotly_chart(fig, width='stretch')
    
    # ========== SALES SPEEDOMETER ==========
        st.markdown("---")
        st.markdown("### 🎯 Daily Sales Target Tracker")
    
        daily_target = st.number_input("Set Daily Sales Target (KES)", min_value=0, step=5000, value=10000, key="daily_target")
    
    # Get today's sales
        today = date.today()
        today_sales = sales_df[sales_df['Date'].dt.date == pd.Timestamp(today).date()]['Total'].sum() if not sales_df.empty else 0
    
    # Calculate progress
        progress = min((today_sales / daily_target) * 100, 100) if daily_target > 0 else 0
    
        st.progress(progress / 100)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Today's Sales", f"KES {today_sales:,.0f}")
        with col2:
            st.metric("Daily Target", f"KES {daily_target:,.0f}")
            st.caption(f"Progress: {progress:.1f}%")
    
        if today_sales >= daily_target:
            st.success("🎉 Congratulations! You've reached your daily sales goal! 🎉")
        elif progress >= 75:
            st.info("📈 Almost there! Keep going!")
        elif progress <= 25 and datetime.now().hour > 15:
            st.warning("⚠️ Sales are behind target. Consider promotions or follow-ups.")
    
    # ========== SALES INSIGHTS ==========
        st.markdown("---")
        st.markdown("### 💡 Sales Insights & Recommendations")
    
        insights = []
    
    # Best selling day of week
        day_sales = sales_df.groupby(sales_df['Date'].dt.day_name())['Total'].sum().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    )
        if not day_sales.empty:
            best_day = day_sales.idxmax()
            best_day_value = day_sales.max()
            insights.append(f"📌 **Best selling day:** {best_day} with KES {best_day_value:,.0f} in sales")
        
            worst_day = day_sales.idxmin()
            worst_day_value = day_sales.min()
            insights.append(f"📌 **Slowest day:** {worst_day} with KES {worst_day_value:,.0f}")
    
    # Trend analysis
        if len(sales_df) >= 7:
            last_week = sales_df.tail(7)['Total'].sum()
            previous_week = sales_df.head(7)['Total'].sum() if len(sales_df) > 14 else 0
            if previous_week > 0:
                weekly_growth = ((last_week - previous_week) / previous_week) * 100
                if weekly_growth > 10:
                    insights.append(f"📈 **Sales are growing!** +{weekly_growth:.1f}% compared to previous week")
                elif weekly_growth < -10:
                    insights.append(f"📉 **Sales are declining.** {weekly_growth:.1f}% drop from previous week")
    
    # Average order value
        avg_order = sales_df['Total'].mean()
        insights.append(f"💰 **Average order value:** KES {avg_order:,.0f}")
    
    # Top product
        if 'Product' in sales_df.columns:
            top_product = sales_df.groupby('Product')['Total'].sum().idxmax()
            top_product_value = sales_df.groupby('Product')['Total'].sum().max()
            insights.append(f"🏆 **Best selling product:** {top_product} with KES {top_product_value:,.0f}")
    
        for insight in insights:
            st.info(insight)
    
    else:
        st.info("No sales data available. Start recording sales to see trends!")

                # ========== EXPENSE ANALYSIS & BURN RATE DASHBOARD ==========
    st.markdown("---")
    st.markdown("### 💸 Expense Analysis & Burn Rate")
    
    if not expenses_df.empty:
        
        # Make sure date is datetime
        expenses_df['date'] = pd.to_datetime(expenses_df['date'])
        
        # ========== EXPENSE PERIOD SELECTOR ==========
        expense_period = st.radio(
            "Select Expense View",
            ["Daily", "Weekly", "Monthly", "Quarterly"],
            horizontal=True,
            key="expense_period"
        )
        
        # ========== BURN RATE CALCULATION ==========
        st.markdown("#### 🔥 Burn Rate Analysis")
        
        current_date = datetime.now()
        current_cash = kpis['running_balance']  # <-- MOVED THIS HERE FIRST
        
        # Initialize burn variables
        daily_burn = 0
        weekly_burn = 0
        monthly_burn = 0
        quarterly_burn = 0
        burn_rate = 0
        period_name = ""
        runway_days = 0
        
        # Calculate burn rate based on selected period
        if expense_period == "Daily":
            # Last 30 days average daily burn
            last_30_days = expenses_df[expenses_df['date'] >= current_date - timedelta(days=30)]
            daily_burn = last_30_days['amount'].sum() / 30 if len(last_30_days) > 0 else 0
            period_name = "Daily"
            burn_rate = daily_burn
            runway_days = current_cash / burn_rate if burn_rate > 0 else 0
            
        elif expense_period == "Weekly":
            # Last 4 weeks average weekly burn
            last_4_weeks = expenses_df[expenses_df['date'] >= current_date - timedelta(days=28)]
            weekly_burn = last_4_weeks['amount'].sum() / 4 if len(last_4_weeks) > 0 else 0
            period_name = "Weekly"
            burn_rate = weekly_burn
            runway_days = (current_cash / burn_rate) * 7 if burn_rate > 0 else 0
            
        elif expense_period == "Monthly":
            # Last 3 months average monthly burn
            last_3_months = expenses_df[expenses_df['date'] >= current_date - timedelta(days=90)]
            monthly_burn = last_3_months['amount'].sum() / 3 if len(last_3_months) > 0 else 0
            period_name = "Monthly"
            burn_rate = monthly_burn
            runway_days = (current_cash / burn_rate) * 30 if burn_rate > 0 else 0
            
        else:  # Quarterly
            # Last 2 quarters average quarterly burn
            last_2_quarters = expenses_df[expenses_df['date'] >= current_date - timedelta(days=180)]
            quarterly_burn = last_2_quarters['amount'].sum() / 2 if len(last_2_quarters) > 0 else 0
            period_name = "Quarterly"
            burn_rate = quarterly_burn
            runway_days = (current_cash / burn_rate) * 90 if burn_rate > 0 else 0
        
        # Calculate monthly revenue for burn ratio (using the monthly_burn we calculated)
        monthly_revenue = sales_df[sales_df['Date'] >= current_date - timedelta(days=30)]['Total'].sum() if not sales_df.empty else 0
        burn_to_revenue = (monthly_burn / monthly_revenue * 100) if monthly_burn > 0 and monthly_revenue > 0 else 0
        
        # Display burn rate metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(f"🔥 {period_name} Burn Rate", f"KES {burn_rate:,.0f}")
        with col2:
            st.metric("💰 Current Cash Balance", f"KES {current_cash:,.0f}")
        with col3:
            st.metric("📊 Runway", f"{runway_days:.0f} days" if runway_days > 0 else "N/A")
            st.caption(f"At current burn rate")
        with col4:
            st.metric("📉 Burn/Revenue Ratio", f"{burn_to_revenue:.1f}%" if burn_to_revenue > 0 else "N/A")
            if burn_to_revenue > 100:
                st.caption("⚠️ Spending more than earning!")
            elif burn_to_revenue > 70:
                st.caption("⚠️ High expense ratio")
            elif burn_to_revenue > 0:
                st.caption("✅ Healthy ratio")
        
        # ========== EXPENSE TRENDS ==========
        st.markdown("#### 📈 Expense Trends Over Time")
        
        # Group expenses by period
        if expense_period == "Daily":
            expense_trend = expenses_df.groupby('date')['amount'].sum().reset_index()
            expense_trend.columns = ['Date', 'Amount']
            fig = px.line(expense_trend, x='Date', y='Amount', 
                         title='Daily Expense Trend',
                         markers=True, line_shape='spline')
            fig.update_traces(line=dict(color='#FF4B4B', width=3))
            
        elif expense_period == "Weekly":
            expenses_df['Week'] = expenses_df['date'].dt.isocalendar().week
            expenses_df['Year'] = expenses_df['date'].dt.year
            expenses_df['WeekLabel'] = expenses_df.apply(lambda x: f"W{x['Week']}", axis=1)
            expense_trend = expenses_df.groupby(['Year', 'Week', 'WeekLabel'])['amount'].sum().reset_index()
            expense_trend = expense_trend.sort_values(['Year', 'Week'])
            fig = px.bar(expense_trend, x='WeekLabel', y='amount', 
                        title='Weekly Expense Trend',
                        color='amount', color_continuous_scale='Reds')
            
        elif expense_period == "Monthly":
            expenses_df['Month'] = expenses_df['date'].dt.strftime('%Y-%m')
            expenses_df['MonthLabel'] = expenses_df['date'].dt.strftime('%B %Y')
            expense_trend = expenses_df.groupby(['Month', 'MonthLabel'])['amount'].sum().reset_index()
            expense_trend = expense_trend.sort_values('Month')
            fig = px.line(expense_trend, x='MonthLabel', y='amount', 
                         title='Monthly Expense Trend',
                         markers=True, line_shape='spline')
            fig.update_traces(line=dict(color='#FF4B4B', width=3))
            
        else:  # Quarterly
            expenses_df['Quarter'] = expenses_df['date'].dt.to_period('Q').astype(str)
            expense_trend = expenses_df.groupby('Quarter')['amount'].sum().reset_index()
            fig = px.bar(expense_trend, x='Quarter', y='amount', 
                        title='Quarterly Expense Trend',
                        color='amount', color_continuous_scale='Reds')
        
        if 'fig' in locals():
            fig.update_layout(height=400)
            st.plotly_chart(fig, width='stretch')
        
        # ========== EXPENSE CATEGORY BREAKDOWN ==========
        st.markdown("#### 📂 Expense Categories")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart of expenses by category
            category_summary = expenses_df.groupby('category')['amount'].sum().reset_index()
            category_summary = category_summary.sort_values('amount', ascending=False)
            
            if not category_summary.empty:
                fig = px.pie(category_summary, values='amount', names='category', 
                            title='Expenses by Category',
                            color_discrete_sequence=px.colors.qualitative.Set3,
                            hole=0.3)
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("No category data available")
        
        with col2:
            # Top 5 expense categories bar chart
            if not category_summary.empty:
                top_5 = category_summary.head(5)
                fig = px.bar(top_5, x='category', y='amount', 
                            title='Top 5 Expense Categories',
                            color='amount', color_continuous_scale='Reds',
                            text='amount')
                fig.update_traces(texttemplate='KES %{text:,.0f}', textposition='outside')
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("No category data available")
        
        # ========== EXPENSE CLASSIFICATION ==========
        st.markdown("#### 🏷️ Expense Classification")
        
        # Classify expenses as Fixed vs Variable
        fixed_categories = ['Salaries', 'Office Rent', 'Insurance', 'Software', 'Utilities']
        variable_categories = ['Supplies', 'Transport', 'Marketing', 'Equipment', 'Other']
        
        expenses_df['Classification'] = expenses_df['category'].apply(
            lambda x: 'Fixed' if x in fixed_categories else 'Variable' if x in variable_categories else 'Other'
        )
        
        classification_summary = expenses_df.groupby('Classification')['amount'].sum().reset_index()
        
        if not classification_summary.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(classification_summary, values='amount', names='Classification',
                            title='Fixed vs Variable Expenses',
                            color='Classification',
                            color_discrete_map={'Fixed': '#2196F3', 'Variable': '#FF9800', 'Other': '#9E9E9E'})
                st.plotly_chart(fig, width='stretch')
                
                # Show classification insights
                fixed_total = classification_summary[classification_summary['Classification'] == 'Fixed']['amount'].sum() if len(classification_summary) > 0 else 0
                variable_total = classification_summary[classification_summary['Classification'] == 'Variable']['amount'].sum() if len(classification_summary) > 0 else 0
                
                if fixed_total > variable_total:
                    st.info("💡 **Insight:** Most expenses are fixed. Consider negotiating fixed costs to improve profitability.")
                else:
                    st.info("💡 **Insight:** Most expenses are variable. Focus on volume-based cost reduction.")
            
            with col2:
                # Monthly fixed vs variable trend
                expenses_df['Month'] = expenses_df['date'].dt.strftime('%Y-%m')
                monthly_class = expenses_df.groupby(['Month', 'Classification'])['amount'].sum().reset_index()
                
                if not monthly_class.empty:
                    fig = px.line(monthly_class, x='Month', y='amount', color='Classification',
                                 title='Monthly Fixed vs Variable Trend',
                                 markers=True)
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, width='stretch')
        
        # ========== EXPENSE ALERTS & INSIGHTS ==========
        st.markdown("#### ⚠️ Expense Alerts & Insights")
        
        total_expenses_value = kpis['total_expenses']
        
        alerts = []
        
        # Check for unusually high expense days/weeks/months
        if expense_period == "Monthly" and 'expense_trend' in locals() and len(expense_trend) >= 3:
            avg_expense = expense_trend['amount'].mean()
            current_expense = expense_trend['amount'].iloc[-1] if len(expense_trend) > 0 else 0
            if current_expense > avg_expense * 1.3:
                alerts.append(f"📈 **High expense alert:** Current {expense_period.lower()} expenses are {((current_expense/avg_expense)-1)*100:.0f}% above average")
        
        # Check burn rate against revenue
        if monthly_burn > monthly_revenue and monthly_revenue > 0:
            alerts.append(f"⚠️ **Burn rate warning:** You're spending KES {monthly_burn - monthly_revenue:,.0f} more than you earn each month")
        
        # Check cash runway
        if runway_days < 30 and runway_days > 0:
            alerts.append(f"🚨 **Critical runway:** Only {runway_days:.0f} days of cash left at current burn rate")
        elif runway_days < 90 and runway_days > 0:
            alerts.append(f"⚠️ **Low runway:** {runway_days:.0f} days of cash remaining")
        
        # Category spikes
        if 'category_summary' in locals() and not category_summary.empty:
            for cat in category_summary.head(3)['category'].values:
                cat_total = category_summary[category_summary['category'] == cat]['amount'].values[0]
                if cat_total > total_expenses_value * 0.4:
                    alerts.append(f"💰 **Category concentration:** {cat} represents {((cat_total/total_expenses_value)*100):.0f}% of total expenses")
        
        if alerts:
            for alert in alerts:
                if "🚨" in alert or "Critical" in alert:
                    st.error(alert)
                elif "⚠️" in alert or "warning" in alert:
                    st.warning(alert)
                else:
                    st.info(alert)
        else:
            st.success("✅ No unusual expense patterns detected. Spending is under control.")
        
        # ========== EXPENSE TO REVENUE RATIO ==========
        st.markdown("#### 📊 Expense to Revenue Ratio")
        
        # Calculate monthly expense/revenue ratio
        monthly_data = []
        for month in sales_df['Date'].dt.to_period('M').unique():
            month_sales = sales_df[sales_df['Date'].dt.to_period('M') == month]['Total'].sum()
            month_expenses = expenses_df[expenses_df['date'].dt.to_period('M') == month]['amount'].sum()
            ratio = (month_expenses / month_sales * 100) if month_sales > 0 else 0
            monthly_data.append({
                'Month': str(month),
                'Revenue': month_sales,
                'Expenses': month_expenses,
                'Ratio': ratio
            })
        
        if monthly_data:
            df_ratio = pd.DataFrame(monthly_data)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_ratio['Month'], y=df_ratio['Revenue'], name='Revenue', marker_color='#36B37E'))
            fig.add_trace(go.Bar(x=df_ratio['Month'], y=df_ratio['Expenses'], name='Expenses', marker_color='#FF4B4B'))
            fig.add_trace(go.Scatter(x=df_ratio['Month'], y=df_ratio['Ratio'], name='Expense/Revenue %', 
                                    yaxis='y2', mode='lines+markers', line=dict(color='#FF9800', width=3)))
            fig.update_layout(
                title='Revenue vs Expenses with Ratio',
                xaxis_title='Month',
                yaxis_title='Amount (KES)',
                yaxis2=dict(title='Ratio %', overlaying='y', side='right'),
                barmode='group',
                height=450
            )
            st.plotly_chart(fig, width='stretch')
            
            # Average ratio insight
            avg_ratio = df_ratio['Ratio'].mean()
            if avg_ratio > 70:
                st.warning(f"📊 **Average expense ratio: {avg_ratio:.0f}%** - High expenses relative to revenue")
            elif avg_ratio > 50:
                st.info(f"📊 **Average expense ratio: {avg_ratio:.0f}%** - Moderate, room for improvement")
            else:
                st.success(f"📊 **Average expense ratio: {avg_ratio:.0f}%** - Excellent cost control")
        
    else:
        st.info("No expense data available. Start recording expenses to see burn rate analysis!")

        
            # ========== PROFIT TREND ANALYSIS ==========
    st.markdown("---")
    st.markdown("### 📈 Profit Trend Analysis")
    
    if not sales_df.empty and not expenses_df.empty:
        
        # Prepare daily data
        sales_df['Date'] = pd.to_datetime(sales_df['Date'])
        expenses_df['date'] = pd.to_datetime(expenses_df['date'])
        
        # Get date range
        all_dates = pd.date_range(
            start=min(sales_df['Date'].min(), expenses_df['date'].min()),
            end=max(sales_df['Date'].max(), expenses_df['date'].max()),
            freq='D'
        )
        
        # Daily sales
        daily_sales = sales_df.groupby('Date')['Total'].sum().reset_index()
        daily_sales.columns = ['Date', 'Sales']
        
        # Daily expenses
        daily_expenses = expenses_df.groupby('date')['amount'].sum().reset_index()
        daily_expenses.columns = ['Date', 'Expenses']
        
        # Merge and fill missing days with 0
        profit_df = pd.merge(daily_sales, daily_expenses, on='Date', how='outer').fillna(0)
        profit_df = profit_df.sort_values('Date')
        
        # Calculate daily profit
        profit_df['Daily Profit'] = profit_df['Sales'] - profit_df['Expenses']
        
        # Calculate cumulative profit
        profit_df['Cumulative Sales'] = profit_df['Sales'].cumsum()
        profit_df['Cumulative Expenses'] = profit_df['Expenses'].cumsum()
        profit_df['Cumulative Profit'] = profit_df['Cumulative Sales'] - profit_df['Cumulative Expenses']
        
        # Calculate 7-day moving average of profit
        profit_df['Profit_MA7'] = profit_df['Daily Profit'].rolling(window=7, min_periods=1).mean()
        
        # ========== PROFIT METRICS ==========
        st.markdown("#### 💰 Profit Metrics")
        
        total_profit = profit_df['Daily Profit'].sum()
        avg_daily_profit = profit_df['Daily Profit'].mean()
        best_profit_day = profit_df.loc[profit_df['Daily Profit'].idxmax()]
        worst_profit_day = profit_df.loc[profit_df['Daily Profit'].idxmin()]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Total Profit", f"KES {total_profit:,.0f}")
        with col2:
            st.metric("📊 Avg Daily Profit", f"KES {avg_daily_profit:,.0f}")
        with col3:
            st.metric("🏆 Best Day", f"KES {best_profit_day['Daily Profit']:,.0f}")
            st.caption(f"{best_profit_day['Date'].strftime('%b %d')}")
        with col4:
            st.metric("📉 Worst Day", f"KES {worst_profit_day['Daily Profit']:,.0f}")
            st.caption(f"{worst_profit_day['Date'].strftime('%b %d')}")
        
        # ========== DAILY PROFIT CHART ==========
        st.markdown("#### 📊 Daily Profit Trend")
        
        fig = go.Figure()
        
        # Add bars for profit (green for positive, red for negative)
        colors = ['#4CAF50' if x >= 0 else '#FF4B4B' for x in profit_df['Daily Profit']]
        
        fig.add_trace(go.Bar(
            x=profit_df['Date'], 
            y=profit_df['Daily Profit'],
            name='Daily Profit',
            marker_color=colors,
            text=profit_df['Daily Profit'].apply(lambda x: f'KES {x:,.0f}'),
            textposition='outside',
            hovertemplate='Date: %{x}<br>Profit: KES %{y:,.0f}<extra></extra>'
        ))
        
        # Add moving average line
        fig.add_trace(go.Scatter(
            x=profit_df['Date'],
            y=profit_df['Profit_MA7'],
            name='7-Day Avg Profit',
            line=dict(color='#FF9800', width=3),
            mode='lines'
        ))
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Break-even")
        
        fig.update_layout(
            title='Daily Profit with 7-Day Moving Average',
            xaxis_title='Date',
            yaxis_title='Profit (KES)',
            height=450,
            hovermode='x unified'
        )
        st.plotly_chart(fig, width='stretch')
        
        # ========== CUMULATIVE PROFIT CHART ==========
        st.markdown("#### 📈 Cumulative Profit Over Time")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=profit_df['Date'],
            y=profit_df['Cumulative Sales'],
            name='Cumulative Sales',
            mode='lines',
            line=dict(color='#36B37E', width=3),
            fill=None,
            hovertemplate='Date: %{x}<br>Sales: KES %{y:,.0f}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=profit_df['Date'],
            y=profit_df['Cumulative Expenses'],
            name='Cumulative Expenses',
            mode='lines',
            line=dict(color='#FF4B4B', width=3),
            fill=None,
            hovertemplate='Date: %{x}<br>Expenses: KES %{y:,.0f}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=profit_df['Date'],
            y=profit_df['Cumulative Profit'],
            name='Cumulative Profit',
            mode='lines',
            line=dict(color='#4CAF50', width=4, dash='dash'),
            fill='tozeroy',
            hovertemplate='Date: %{x}<br>Profit: KES %{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Cumulative Sales, Expenses, and Profit',
            xaxis_title='Date',
            yaxis_title='Amount (KES)',
            height=500,
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        st.plotly_chart(fig, width='stretch')
        
        # ========== PROFIT MARGIN ==========
        st.markdown("#### 📊 Profit Margin Analysis")
        
        # Calculate profit margin by day
        profit_df['Profit Margin %'] = (profit_df['Daily Profit'] / profit_df['Sales'] * 100).fillna(0)
        profit_df['Profit Margin %'] = profit_df['Profit Margin %'].clip(lower=-100, upper=100)
        
        # Remove infinite values
        profit_df['Profit Margin %'] = profit_df['Profit Margin %'].replace([np.inf, -np.inf], 0)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=profit_df['Date'],
            y=profit_df['Profit Margin %'],
            name='Profit Margin',
            marker_color=profit_df['Profit Margin %'],
            marker_colorscale='RdYlGn',
            text=profit_df['Profit Margin %'].apply(lambda x: f'{x:.1f}%'),
            textposition='outside',
            hovertemplate='Date: %{x}<br>Margin: %{y:.1f}%<extra></extra>'
        ))
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.add_hline(y=20, line_dash="dash", line_color="green", annotation_text="Target 20%", annotation_position="bottom right")
        
        fig.update_layout(
            title='Daily Profit Margin %',
            xaxis_title='Date',
            yaxis_title='Profit Margin (%)',
            height=400,
            yaxis_range=[-100, 100]
        )
        st.plotly_chart(fig, width='stretch')
        
        # ========== SALES vs EXPENSES GROWTH ==========
        st.markdown("#### 📈 Sales vs Expenses Growth Rate")
        
        # Calculate weekly totals
        profit_df['Week'] = profit_df['Date'].dt.isocalendar().week
        profit_df['Year'] = profit_df['Date'].dt.year
        
        weekly_summary = profit_df.groupby(['Year', 'Week']).agg({
            'Sales': 'sum',
            'Expenses': 'sum',
            'Daily Profit': 'sum'
        }).reset_index()
        
        weekly_summary['WeekLabel'] = weekly_summary.apply(lambda x: f"W{x['Week']}", axis=1)
        
        if len(weekly_summary) >= 2:
            # Calculate week-over-week growth
            weekly_summary['Sales Growth %'] = weekly_summary['Sales'].pct_change() * 100
            weekly_summary['Expense Growth %'] = weekly_summary['Expenses'].pct_change() * 100
            weekly_summary['Profit Growth %'] = weekly_summary['Daily Profit'].pct_change() * 100
            
            growth_df = weekly_summary.tail(8)[['WeekLabel', 'Sales Growth %', 'Expense Growth %', 'Profit Growth %']].dropna()
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=growth_df['WeekLabel'], y=growth_df['Sales Growth %'], name='Sales Growth', marker_color='#36B37E'))
            fig.add_trace(go.Bar(x=growth_df['WeekLabel'], y=growth_df['Expense Growth %'], name='Expense Growth', marker_color='#FF4B4B'))
            fig.add_trace(go.Scatter(x=growth_df['WeekLabel'], y=growth_df['Profit Growth %'], name='Profit Growth', 
                                    mode='lines+markers', line=dict(color='#FF9800', width=3)))
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.update_layout(
                title='Week-over-Week Growth Rates',
                xaxis_title='Week',
                yaxis_title='Growth %',
                height=450,
                barmode='group'
            )
            st.plotly_chart(fig, width='stretch')
            
            # Summary insight
            latest_sales_growth = growth_df['Sales Growth %'].iloc[-1] if not growth_df.empty else 0
            latest_expense_growth = growth_df['Expense Growth %'].iloc[-1] if not growth_df.empty else 0
            
            if latest_sales_growth > latest_expense_growth:
                st.success(f"✅ **Great!** Sales are growing faster ({latest_sales_growth:.1f}%) than expenses ({latest_expense_growth:.1f}%)")
            elif latest_sales_growth < latest_expense_growth:
                st.warning(f"⚠️ **Warning:** Expenses are growing faster ({latest_expense_growth:.1f}%) than sales ({latest_sales_growth:.1f}%)")
            else:
                st.info(f"📊 Sales and expenses are growing at similar rates")
        
        # ========== PROFIT INSIGHTS ==========
        st.markdown("#### 💡 Profit Insights")
        
        insights = []
        
        # Overall profit health
        if total_profit > 0:
            insights.append(f"✅ **Overall Profitability:** Your business has generated KES {total_profit:,.0f} in total profit")
        else:
            insights.append(f"⚠️ **Overall Profitability:** Your business has a total loss of KES {abs(total_profit):,.0f}")
        
        # Profit margin average
        avg_margin = profit_df['Profit Margin %'].mean()
        if avg_margin > 20:
            insights.append(f"✅ **Average Profit Margin:** {avg_margin:.1f}% - Excellent!")
        elif avg_margin > 10:
            insights.append(f"📈 **Average Profit Margin:** {avg_margin:.1f}% - Good, room for improvement")
        elif avg_margin > 0:
            insights.append(f"⚠️ **Average Profit Margin:** {avg_margin:.1f}% - Low, consider cost reduction")
        else:
            insights.append(f"🔴 **Average Profit Margin:** {avg_margin:.1f}% - Negative, need urgent action")
        
        # Best performing period
        if len(weekly_summary) >= 2:
            best_week = weekly_summary.loc[weekly_summary['Daily Profit'].idxmax()]
            insights.append(f"🏆 **Best Week:** {best_week['WeekLabel']} with KES {best_week['Daily Profit']:,.0f} profit")
        
        # Sales vs expenses ratio
        total_sales_all = profit_df['Sales'].sum()
        total_expenses_all = profit_df['Expenses'].sum()
        if total_expenses_all > 0:
            expense_ratio = (total_expenses_all / total_sales_all) * 100
            insights.append(f"📊 **Expense Ratio:** {expense_ratio:.1f}% of revenue goes to expenses")
        
        for insight in insights:
            st.info(insight)
        
        # ========== BREAK-EVEN ANALYSIS ==========
        st.markdown("#### 🎯 Break-even Analysis")
        
        # Calculate average daily fixed costs (from fixed categories)
        fixed_categories_list = ['Salaries', 'Office Rent', 'Insurance', 'Software', 'Utilities']
        fixed_expenses = expenses_df[expenses_df['category'].isin(fixed_categories_list)]['amount'].sum()
        avg_daily_fixed = fixed_expenses / len(profit_df) if len(profit_df) > 0 else 0
        
        # Average variable cost per unit (estimate)
        avg_variable_cost = 0.34 * 10  # Approximate for 10g product
        
        # Average selling price
        avg_selling_price = profit_df['Sales'].sum() / profit_df['Sales'].count() if profit_df['Sales'].sum() > 0 else 0
        
        if avg_selling_price > avg_variable_cost:
            contribution_margin = avg_selling_price - avg_variable_cost
            break_even_units = avg_daily_fixed / contribution_margin if contribution_margin > 0 else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📊 Daily Fixed Costs", f"KES {avg_daily_fixed:,.0f}")
                st.metric("💵 Contribution Margin", f"KES {contribution_margin:.0f} per unit")
            with col2:
                st.metric("🎯 Break-even Units", f"{break_even_units:.0f} units/day")
                st.caption("Units needed to cover daily costs")
        
    else:
        st.info("Need both sales and expense data to show profit analysis")

        # Key Metrics Cards
        st.markdown("### 📈 Key Performance Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate metrics based on period
        if period == "Daily":
            avg_sales = sales_trend['Sales'].mean()
            best_day = sales_trend.loc[sales_trend['Sales'].idxmax()]
            worst_day = sales_trend.loc[sales_trend['Sales'].idxmin()]
            total_period = sales_trend['Sales'].sum()
            
            with col1:
                st.metric("📊 Avg Daily Sales", f"KES {avg_sales:,.0f}")
            with col2:
                st.metric("🏆 Best Day", f"KES {best_day['Sales']:,.0f}")
                st.caption(f"{best_day['Period']}")
            with col3:
                st.metric("📉 Worst Day", f"KES {worst_day['Sales']:,.0f}")
                st.caption(f"{worst_day['Period']}")
            with col4:
                st.metric("💰 Total Period", f"KES {total_period:,.0f}")
                
        elif period == "Weekly":
            avg_sales = sales_trend['Total'].mean()
            best_week = sales_trend.loc[sales_trend['Total'].idxmax()]
            total_period = sales_trend['Total'].sum()
            
            with col1:
                st.metric("📊 Avg Weekly Sales", f"KES {avg_sales:,.0f}")
            with col2:
                st.metric("🏆 Best Week", f"KES {best_week['Total']:,.0f}")
                st.caption(f"{best_week['Period']}")
            with col3:
                # Calculate week-over-week growth
                if len(sales_trend) >= 2:
                    recent = sales_trend.iloc[-1]['Total']
                    previous = sales_trend.iloc[-2]['Total']
                    growth = ((recent - previous) / previous * 100) if previous > 0 else 0
                    st.metric("📈 Week-over-Week", f"{growth:.1f}%", delta=f"{growth:.1f}%" if growth != 0 else None)
                else:
                    st.metric("📈 Week-over-Week", "N/A")
            with col4:
                st.metric("💰 Total Period", f"KES {total_period:,.0f}")
                
        else:  # Monthly/Quarterly
            avg_sales = sales_trend['Sales'].mean()
            best_period = sales_trend.loc[sales_trend['Sales'].idxmax()]
            total_period = sales_trend['Sales'].sum()
            
            with col1:
                st.metric(f"📊 Avg {period} Sales", f"KES {avg_sales:,.0f}")
            with col2:
                st.metric(f"🏆 Best {period}", f"KES {best_period['Sales']:,.0f}")
                st.caption(f"{best_period['Period']}")
            with col3:
                # Calculate growth
                if len(sales_trend) >= 2:
                    recent = sales_trend.iloc[-1]['Sales']
                    previous = sales_trend.iloc[-2]['Sales']
                    growth = ((recent - previous) / previous * 100) if previous > 0 else 0
                    st.metric(f"📈 {period} Growth", f"{growth:.1f}%", delta=f"{growth:.1f}%" if growth != 0 else None)
                else:
                    st.metric(f"📈 {period} Growth", "N/A")
            with col4:
                st.metric("💰 Total Period", f"KES {total_period:,.0f}")
        
        # Sales Insights
        st.markdown("### 💡 Sales Insights & Recommendations")
        
        # Generate insights based on data
        insights = []
        
        # Best selling day of week
        sales_df['DayName'] = sales_df['Date'].dt.day_name()
        day_sales = sales_df.groupby('DayName')['Total'].sum().reindex(
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        )
        best_day = day_sales.idxmax()
        best_day_value = day_sales.max()
        
        insights.append(f"📌 **Best selling day:** {best_day} with KES {best_day_value:,.0f} in sales")
        
        # Sales trend direction
        if len(sales_trend) >= 3:
            recent_avg = sales_trend.tail(3)['Sales' if period != "Weekly" else 'Total'].mean()
            previous_avg = sales_trend.head(3)['Sales' if period != "Weekly" else 'Total'].mean()
            if recent_avg > previous_avg:
                insights.append(f"📈 **Sales are growing!** +{((recent_avg - previous_avg) / previous_avg * 100):.1f}% compared to previous period")
            else:
                insights.append(f"📉 **Sales are declining.** Consider promotional offers or reaching out to existing customers")
        
        # Average order value insight
        avg_order = sales_df['Total'].mean()
        if avg_order < 500:
            insights.append(f"💡 **Average order is KES {avg_order:,.0f}** - Consider bundle offers to increase order value")
        
        # Top customer insight
        top_customer = sales_df.groupby('Name')['Total'].sum().idxmax()
        top_customer_value = sales_df.groupby('Name')['Total'].sum().max()
        insights.append(f"🏆 **Your best customer is {top_customer}** with KES {top_customer_value:,.0f} in total purchases")
        
        # Display insights
        for insight in insights:
            st.info(insight)
        
        # Weekly Sales Calendar View
        st.markdown("### 📅 Weekly Sales Calendar")
        
        # Create a heatmap of sales by day of week and hour
        sales_df['Hour'] = sales_df['Date'].dt.hour
        sales_df['DayOfWeek'] = sales_df['Date'].dt.day_name()
        
        # Pivot table for heatmap
        heatmap_data = sales_df.pivot_table(
            values='Total', 
            index='DayOfWeek', 
            columns='Hour', 
            aggfunc='sum', 
            fill_value=0
        ).reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        
        if not heatmap_data.empty:
            fig = px.imshow(heatmap_data, 
                           title='Sales Heatmap by Day and Hour',
                           labels=dict(x="Hour of Day", y="Day of Week", color="Sales (KES)"),
                           color_continuous_scale='Viridis',
                           aspect='auto')
            fig.update_layout(height=400)
            st.plotly_chart(fig, width='stretch')
            st.caption("💡 **When to focus sales efforts:** Darker colors show when sales happen most")
        
        # Cumulative Sales Goal Tracker
        st.markdown("### 🎯 Sales Goal Tracker")
        
        # Set monthly goal (adjustable)
        monthly_goal = st.number_input("Set Monthly Sales Goal (KES)", min_value=0, step=10000, value=100000, key="sales_goal")
        
        # Calculate current month sales
        current_month = date.today().month
        current_year = date.today().year
        month_sales = sales_df[(sales_df['Date'].dt.month == current_month) & 
                                (sales_df['Date'].dt.year == current_year)]['Total'].sum()
        
        progress = (month_sales / monthly_goal * 100) if monthly_goal > 0 else 0
        
        st.progress(min(progress / 100, 1.0))
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Month Sales", f"KES {month_sales:,.0f}")
        with col2:
            st.metric("Monthly Goal", f"KES {monthly_goal:,.0f}")
            st.caption(f"Progress: {progress:.1f}%")
        
        if month_sales >= monthly_goal:
            st.success("🎉 **Congratulations! You've reached your monthly sales goal!** 🎉")
        elif progress >= 75:
            st.info("📈 **Almost there!** Keep pushing to reach your goal!")
        elif progress <= 25 and (date.today().day > 15):
            st.warning("⚠️ **Sales are behind target.** Consider running a promotion or reaching out to customers.")
            
        else:
            st.info("No sales data available. Start recording sales to see trends!")
    
    analytics_tab1, analytics_tab2, analytics_tab3, analytics_tab4, analytics_tab5, analytics_tab6 = st.tabs([
        "🏆 Performance Leaderboards", 
        "📊 Distribution Insights", 
        "🏨 Hotel & Mama Mboga", 
        "📁 Data Management",
        "🦈 Shark Tank Analytics",
        "BUSINESS INTELLIGENCE REPORT"
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
                st.plotly_chart(fig, width='stretch')
            with col2:
                fig = px.bar(sp_summary.head(10), x='Salesperson', y='Quantity', title='Top 10 Salespeople by Quantity', color='Quantity', color_continuous_scale='Plasma')
                st.plotly_chart(fig, width='stretch')
        
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
                st.plotly_chart(fig, width='stretch')
    
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
                    st.plotly_chart(fig, width='stretch')
                
                with col2:
                    monthly = dist_time.groupby(dist_time['date'].dt.strftime('%Y-%m'))['quantity_distributed'].sum().reset_index()
                    monthly.columns = ['Month', 'Quantity']
                    fig = px.line(monthly, x='Month', y='Quantity', title='Monthly Sales Trend', markers=True)
                    st.plotly_chart(fig, width='stretch')

    with analytics_tab3:
        st.markdown("### 🏨 Hotel Refill Performance")
    
    # ========== HOTEL MANAGEMENT ==========
        with st.expander("➕ Add New Hotel", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                new_hotel = st.text_input("Hotel Name", key="new_hotel_name")
                hotel_location = st.text_input("Location", key="hotel_location")
            with col2:
                hotel_contact = st.text_input("Contact Phone", key="hotel_contact")
                hotel_person = st.text_input("Contact Person", key="hotel_person")
        
            if st.button("💾 Save Hotel", key="save_hotel"):
                if new_hotel:
                    hotel_data = {
                    "hotel_name": new_hotel,
                    "location": hotel_location,
                    "contact_phone": hotel_contact,
                    "contact_person": hotel_person,
                    "joined_date": str(date.today()),
                    "status": "Active"
                }
                    save_hotel(hotel_data)
                    st.success(f"✅ Hotel '{new_hotel}' added!")
                    st.rerun()
    
    # ========== RECORD REFILL ==========
        with st.expander("🔄 Record Hotel Refill", expanded=True):
            hotels = get_all_hotels()
            hotel_options = {h['hotel_name']: h['id'] for h in hotels} if hotels else {}
        
            col1, col2 = st.columns(2)
            with col1:
                selected_hotel = st.selectbox("Select Hotel", list(hotel_options.keys()) if hotel_options else ["No hotels"], key="refill_hotel")
                refill_date = st.date_input("Refill Date", value=date.today(), key="refill_date")
                refill_product = st.selectbox("Product", ["100g Bottle", "100g Refill", "Sachet 5", "Sachet 10", "Sachet 20", "Sachet 30", "Sachet 40"], key="refill_product")
            with col2:
                refill_quantity = st.number_input("Quantity", min_value=1, step=1, value=1, key="refill_quantity")
                refill_amount = st.number_input("Amount Paid (KES)", min_value=0, step=100, value=0, key="refill_amount")
                refill_notes = st.text_area("Notes", key="refill_notes")
        
            if st.button("💾 Record Refill", key="record_refill"):
                if selected_hotel != "No hotels" and refill_quantity > 0:
                    hotel_id = hotel_options[selected_hotel]
                    refill_data = {
                    "hotel_id": hotel_id,
                    "refill_date": str(refill_date),
                    "product_type": refill_product,
                    "quantity": refill_quantity,
                    "amount_paid": refill_amount if refill_amount > 0 else refill_quantity * (120 if "Refill" in refill_product else 150),
                    "payment_status": "Paid",
                    "notes": refill_notes
                }
                    save_hotel_refill(refill_data)
                    st.success(f"✅ Refill recorded for {selected_hotel}!")
                    st.rerun()
    
    # ========== HOTEL PERFORMANCE DASHBOARD ==========
        st.markdown("---")
        st.markdown("### 📊 Hotel Performance Dashboard")
    
        hotels = get_all_hotels()
        if hotels:
        # Display all hotels with stats
            hotel_stats = []
            for hotel in hotels:
                refills = get_hotel_refills(hotel['id'])
                total_refills = len(refills)
                total_quantity = sum(r['quantity'] for r in refills)
                total_revenue = sum(r['amount_paid'] for r in refills)
            
            # Calculate average days between refills
                if len(refills) >= 2:
    # Convert string dates to datetime objects
                    from datetime import datetime
                    dates = sorted([datetime.strptime(r['refill_date'], '%Y-%m-%d') if isinstance(r['refill_date'], str) else r['refill_date'] for r in refills])
                    avg_days = sum((dates[i+1] - dates[i]).days for i in range(len(dates)-1)) / (len(dates)-1)
                    frequency = f"Every {avg_days:.0f} days"
                elif total_refills == 1:
                    frequency = "First refill"
                else:
                    frequency = "No refills yet"
            
                hotel_stats.append({
                "Hotel": hotel['hotel_name'],
                "Location": hotel.get('location', 'N/A'),
                "Refills": total_refills,
                "Total Quantity": total_quantity,
                "Total Revenue": total_revenue,
                "Frequency": frequency
            })
        
            df_hotels = pd.DataFrame(hotel_stats)
            df_hotels['Total Revenue'] = df_hotels['Total Revenue'].apply(lambda x: f"KES {x:,.0f}")
        
            st.dataframe(df_hotels, use_container_width=True, hide_index=True)
        
        # Fastest refilling hotels chart
            refill_counts = [(h['Hotel'], h['Refills']) for h in hotel_stats if h['Refills'] > 0]
            if refill_counts:
                df_refills = pd.DataFrame(refill_counts, columns=['Hotel', 'Number of Refills'])
                df_refills = df_refills.sort_values('Number of Refills', ascending=False).head(10)
                fig = px.bar(df_refills, x='Hotel', y='Number of Refills', 
                        title='Hotels with Most Refills',
                        color='Number of Refills', color_continuous_scale='Viridis',
                        text='Number of Refills')
                st.plotly_chart(fig, width='stretch')
        else:
            st.info("No hotels added yet. Add your first hotel above!")
    
    # ========== MAMA MBOGAS SECTION ==========
        st.markdown("---")
        st.markdown("### 🏪 Mama Mboga Performance")
    
    # Add new Mama Mboga
        with st.expander("➕ Add New Mama Mboga/Shop", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                new_mama = st.text_input("Shop Name", key="new_mama_name")
                mama_location = st.text_input("Location", key="mama_location")
            with col2:
                mama_contact = st.text_input("Contact Phone", key="mama_contact")
                mama_volume = st.selectbox("Sales Volume", ["Low", "Medium", "High"], key="mama_volume")
        
            if st.button("💾 Save Mama Mboga", key="save_mama"):
                if new_mama:
                    mama_data = {
                    "shop_name": new_mama,
                    "location": mama_location,
                    "contact_phone": mama_contact,
                    "sales_volume": mama_volume,
                    "joined_date": str(date.today()),
                    "status": "Active"
                }
                    save_mama_mboga(mama_data)
                    st.success(f"✅ Shop '{new_mama}' added!")
                    st.rerun()
    
    # Record purchase
        with st.expander("💰 Record Mama Mboga Purchase", expanded=True):
            mamas = get_all_mama_mbogas()
            mama_options = {m['shop_name']: m['id'] for m in mamas} if mamas else {}
        
            col1, col2 = st.columns(2)
            with col1:
                selected_mama = st.selectbox("Select Shop", list(mama_options.keys()) if mama_options else ["No shops"], key="purchase_mama")
                purchase_date = st.date_input("Purchase Date", value=date.today(), key="purchase_date")
                purchase_product = st.selectbox("Product", ["Sachet 5", "Sachet 10", "Sachet 20", "Sachet 30", "Sachet 40", "100g Bottle"], key="purchase_product")
            with col2:
                purchase_quantity = st.number_input("Quantity", min_value=1, step=1, value=1, key="purchase_quantity")
                unit_price = st.number_input("Unit Price (KES)", min_value=0, step=1, value=5, key="unit_price")
                total_amount = purchase_quantity * unit_price
                st.info(f"Total: KES {total_amount:,.0f}")
        
            if st.button("💾 Record Purchase", key="record_purchase"):
                if selected_mama != "No shops" and purchase_quantity > 0:
                    mama_id = mama_options[selected_mama]
                    purchase_data = {
                    "mama_id": mama_id,
                    "purchase_date": str(purchase_date),
                    "product_type": purchase_product,
                    "quantity": purchase_quantity,
                    "unit_price": unit_price,
                    "total_amount": total_amount,
                    "payment_status": "Paid"
                }
                save_mama_purchase(purchase_data)
                st.success(f"✅ Purchase recorded for {selected_mama}!")
                st.rerun()
    
    # Mama Mboga Performance Dashboard
        st.markdown("---")
        st.markdown("### 📊 Mama Mboga Performance Dashboard")
    
        mamas = get_all_mama_mbogas()
        if mamas:
            mama_stats = []
            for mama in mamas:
                purchases = get_mama_purchases(mama['id'])
                total_purchases = len(purchases)
                total_quantity = sum(p['quantity'] for p in purchases)
                total_revenue = sum(p['total_amount'] for p in purchases)
            
            # Calculate profit for mama (they sell at higher price)
                estimated_profit = total_quantity * 2.1 if "Sachet" in str(purchases) else 0
            
                mama_stats.append({
                "Shop": mama['shop_name'],
                "Location": mama.get('location', 'N/A'),
                "Purchases": total_purchases,
                "Total Quantity": total_quantity,
                "Total Revenue": total_revenue,
                "Est. Profit": estimated_profit,
                "Volume": mama.get('sales_volume', 'N/A')
            })
        
            df_mamas = pd.DataFrame(mama_stats)
            df_mamas['Total Revenue'] = df_mamas['Total Revenue'].apply(lambda x: f"KES {x:,.0f}")
            df_mamas['Est. Profit'] = df_mamas['Est. Profit'].apply(lambda x: f"KES {x:,.0f}")
        
            st.dataframe(df_mamas, use_container_width=True, hide_index=True)
        
        # Top performing shops chart
            top_mamas = [(m['Shop'], m['Total Quantity']) for m in mama_stats if m['Total Quantity'] > 0]
            if top_mamas:
                df_top = pd.DataFrame(top_mamas, columns=['Shop', 'Quantity Purchased'])
                df_top = df_top.sort_values('Quantity Purchased', ascending=False).head(10)
                fig = px.bar(df_top, x='Shop', y='Quantity Purchased', 
                        title='Top Performing Mama Mbogas',
                        color='Quantity Purchased', color_continuous_scale='Plasma',
                        text='Quantity Purchased')
                st.plotly_chart(fig, width='stretch')
        else:
            st.info("No Mama Mboga shops added yet. Add your first shop above!")
        
        # Product Mix Analysis
        st.markdown("---")
        st.markdown("### 📦 Product Mix Analysis")
        
        if not sales_df.empty:
            col1, col2 = st.columns(2)
            with col1:
                product_summary = sales_df.groupby('Product_Type')['Total'].sum().reset_index() if 'Product_Type' in sales_df.columns else sales_df.groupby('Product')['Total'].sum().reset_index()
                product_summary.columns = ['Product', 'Revenue']
                fig = px.pie(product_summary, values='Revenue', names='Product', title='Revenue by Product Type', color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                if 'Price_per_Unit' in sales_df.columns:
                    price_analysis = sales_df.groupby('Price_per_Unit')['Quantity'].sum().reset_index()
                    price_analysis.columns = ['Price (KES)', 'Quantity Sold']
                    fig = px.bar(price_analysis, x='Price (KES)', y='Quantity Sold', title='Sales Volume by Price Point', color='Quantity Sold', color_continuous_scale='Viridis')
                    st.plotly_chart(fig, width='stretch')

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
                st.plotly_chart(fig, width='stretch')
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
            st.plotly_chart(fig, width='stretch')
        
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
                    st.plotly_chart(fig, width='stretch')
            
                with col2:
                    fig = px.bar(product_margin, x='Product_Type', y='Margin_Percentage',
                            title='Gross Margin % by Product',
                            color='Margin_Percentage',
                            color_continuous_scale='RdYlGn',
                            range_y=[0, 100])
                    fig.add_hline(y=50, line_dash="dash", line_color="red", 
                            annotation_text="Target 50%", annotation_position="bottom right")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, width='stretch')
        
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
                st.plotly_chart(fig, width='stretch')
        
            with col2:
                quarterly_sales = sales_df.groupby('Quarter')['Total'].sum().reset_index()
                fig = px.line(quarterly_sales, x='Quarter', y='Total', 
                         title='Quarterly Growth Trend',
                         markers=True, line_shape='spline')
                fig.update_traces(line=dict(color='#FF9800', width=3))
                fig.update_layout(height=400)
                st.plotly_chart(fig, width='stretch')
        
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
                    st.plotly_chart(fig, width='stretch')
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
        
            # Replace the insights section with this corrected version

            with col2:
                st.markdown("### 💎 Key Insights")
    
                # Generate insights based on actual revenue contribution
                insights = []
    
    # Calculate revenue by segment (not customer count)
                if len(customer_ltv) > 0:
                    segment_revenue = customer_ltv.groupby('Segment')['total_spent'].sum().reset_index()
                    if not segment_revenue.empty:
            # Find segment with highest total revenue
                        top_segment = segment_revenue.loc[segment_revenue['total_spent'].idxmax()]
                        insights.append(f"💰 **Highest revenue segment:** {top_segment['Segment']} customers contributing KES {top_segment['total_spent']:,.0f}")
                    else:
                        insights.append("💰 **Highest revenue segment:** Not enough data")
    
    # Other insights
                if kpis['cash_percentage'] < 50:
                    insights.append("🔴 Too much credit - tighten payment terms")
    
                repeat_rate = len(customer_ltv[customer_ltv['order_count'] > 1]) / len(customer_ltv) * 100 if len(customer_ltv) > 0 else 0
                if repeat_rate < 20:
                    insights.append("🟡 Low customer retention - implement loyalty program")
                elif repeat_rate > 50:
                    insights.append(f"🟢 Great retention! {repeat_rate:.0f}% of customers return")
    
                if 'Margin_Percentage' in locals() and not product_margin.empty and product_margin['Margin_Percentage'].min() < 20:
                    insights.append("🟠 Low margin on some products - review pricing")
    
                if kpis['total_sales'] > 0:
                    insights.append(f"💰 Total revenue: KES {kpis['total_sales']:,.0f}")
                    profit_margin = (kpis['net_profit']/kpis['total_sales']*100) if kpis['total_sales'] > 0 else 0
                    insights.append(f"📈 Net profit margin: {profit_margin:.1f}%")
    
    # Top customer insight
                if len(customer_ltv) > 0:
                    top_customer = customer_ltv.loc[customer_ltv['total_spent'].idxmax()]
                    insights.append(f"🏆 Best customer: {top_customer['Name']} spent KES {top_customer['total_spent']:,.0f}")
    
                for insight in insights[:5]:
                    st.write(f"• {insight}")
    
    # ========== BUSINESS INTELLIGENCE REPORT ==========
with analytics_tab6:  # Add as a new tab or section
    st.markdown("### 📊 Executive Business Intelligence Report")
    st.info("AI-Powered Analysis of Your Business Performance")
    
    if not sales_df.empty:
        
        # Get metrics from kpis dictionary
        total_sales_value = kpis['total_sales']
        total_expenses_value = kpis['total_expenses']
        net_profit_value = kpis['net_profit']
        
        # ========== EXECUTIVE SUMMARY ==========
        st.markdown("## 📈 Executive Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Total Revenue", f"KES {total_sales_value:,.0f}")
        with col2:
            total_units = int(sales_df['Quantity'].sum()) if 'Quantity' in sales_df.columns else 0
            st.metric("📦 Total Units Sold", f"{total_units:,}")
        with col3:
            st.metric("📝 Total Transactions", len(sales_df))
        with col4:
            avg_transaction = total_sales_value / len(sales_df) if len(sales_df) > 0 else 0
            st.metric("💵 Avg Transaction", f"KES {avg_transaction:,.0f}")
        
        # ========== PRODUCT PERFORMANCE ==========
        st.markdown("---")
        st.markdown("## 📦 Product Performance")
        
        if 'Product' in sales_df.columns:
            product_performance = sales_df.groupby('Product').agg({
                'Total': 'sum',
                'Quantity': 'sum' if 'Quantity' in sales_df.columns else 'count',
                'Product': 'count'
            }).rename(columns={'Product': 'Transactions'}).reset_index()
            product_performance = product_performance.sort_values('Total', ascending=False)
            
            st.dataframe(
                product_performance.head(10),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Product": "Product",
                    "Total": st.column_config.NumberColumn("Revenue", format="KES %d"),
                    "Quantity": "Units Sold",
                    "Transactions": "Transactions"
                }
            )
            
            # Top product insight
            if not product_performance.empty:
                top_product = product_performance.iloc[0]['Product']
                top_revenue = product_performance.iloc[0]['Total']
                st.success(f"💡 **Key Insight:** Your **{top_product}** is your strongest revenue generator at KES {top_revenue:,.0f}")
            
            # Sachet vs Bottle analysis
            sachet_revenue = product_performance[product_performance['Product'].str.contains('Sachet', case=False)]['Total'].sum() if not product_performance.empty else 0
            bottle_revenue = product_performance[product_performance['Product'].str.contains('Bottle', case=False)]['Total'].sum() if not product_performance.empty else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📦 Sachet Revenue", f"KES {sachet_revenue:,.0f}")
            with col2:
                st.metric("🍾 Bottle Revenue", f"KES {bottle_revenue:,.0f}")
        
        # ========== MONTHLY PERFORMANCE ==========
        st.markdown("---")
        st.markdown("## 📅 Monthly Performance")
        
        sales_df['Month'] = sales_df['Date'].dt.strftime('%B %Y')
        monthly_performance = sales_df.groupby('Month')['Total'].sum().reset_index()
        
        fig = px.bar(monthly_performance, x='Month', y='Total', 
                    title='Monthly Revenue Trend',
                    color='Total', color_continuous_scale='Viridis',
                    text='Total')
        fig.update_traces(texttemplate='KES %{text:,.0f}', textposition='outside')
        st.plotly_chart(fig, width='stretch')
        
        # Best month insight
        if not monthly_performance.empty:
            best_month = monthly_performance.iloc[monthly_performance['Total'].idxmax()]
            best_month_pct = (best_month['Total'] / total_sales_value * 100) if total_sales_value > 0 else 0
            st.success(f"💡 **Insight:** {best_month['Month']} accounted for {best_month_pct:.1f}% of all revenue. Investigate what worked and replicate it!")
        
        # ========== LOCATION PERFORMANCE ==========
        st.markdown("---")
        st.markdown("## 📍 Best Performing Locations")
        
        if 'Location' in sales_df.columns:
            # Clean location data
            sales_df['CleanLocation'] = sales_df['Location'].str.split(',').str[0].str.strip()
            location_performance = sales_df.groupby('CleanLocation')['Total'].sum().reset_index()
            location_performance = location_performance.sort_values('Total', ascending=False).head(10)
            
            if not location_performance.empty:
                fig = px.bar(location_performance, x='CleanLocation', y='Total',
                            title='Revenue by Location',
                            color='Total', color_continuous_scale='Blues',
                            text='Total')
                fig.update_traces(texttemplate='KES %{text:,.0f}', textposition='outside')
                st.plotly_chart(fig, width='stretch')
        
        # ========== TOP CUSTOMERS ==========
        st.markdown("---")
        st.markdown("## 🏆 Top Customers")
        
        if 'Name' in sales_df.columns:
            top_customers = sales_df.groupby('Name')['Total'].sum().reset_index()
            top_customers = top_customers.sort_values('Total', ascending=False).head(10)
            
            st.dataframe(top_customers, use_container_width=True, hide_index=True,
                        column_config={"Name": "Customer", "Total": st.column_config.NumberColumn("Revenue", format="KES %d")})
        
        # ========== SWOT ANALYSIS ==========
        st.markdown("---")
        st.markdown("## 🎯 Strategic Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💪 Strengths")
            strengths = []
            if bottle_revenue > sachet_revenue:
                strengths.append("✅ Premium product (bottles) driving revenue")
            if len(sales_df) > 100:
                strengths.append("✅ Strong sales volume (100+ transactions)")
            if len(monthly_performance) >= 2:
                growth = (monthly_performance['Total'].iloc[-1] - monthly_performance['Total'].iloc[-2]) / monthly_performance['Total'].iloc[-2] * 100 if monthly_performance['Total'].iloc[-2] > 0 else 0
                if growth > 0:
                    strengths.append(f"✅ Month-over-month growth ({growth:.0f}%)")
            if len(strengths) == 0:
                strengths.append("📌 Building customer base")
            
            for s in strengths:
                st.write(s)
            
            st.markdown("#### 📈 Opportunities")
            opportunities = [
                "🎯 Upsell sachet customers to bottles",
                "🎯 Develop hotel refill program",
                "🎯 Standardize location data for better tracking"
            ]
            for o in opportunities:
                st.write(o)
        
        with col2:
            st.markdown("#### ⚠️ Weaknesses")
            weaknesses = []
            feedback_count = sales_df['Feedback'].notna().sum() if 'Feedback' in sales_df.columns else 0
            if feedback_count < len(sales_df) * 0.3:
                weaknesses.append("❌ Low feedback collection (<30%)")
            repeat_rate = sales_df['Name'].duplicated().sum() / len(sales_df) if 'Name' in sales_df.columns and len(sales_df) > 0 else 0
            if repeat_rate < 0.3:
                weaknesses.append("❌ Low repeat purchase rate")
            if len(weaknesses) == 0:
                weaknesses.append("📌 Track repeat purchases better")
            
            for w in weaknesses:
                st.write(w)
            
            st.markdown("#### 🚨 Threats")
            threats = [
                "⚠️ Competition in spice market",
                "⚠️ Raw material price volatility"
            ]
            for t in threats:
                st.write(t)
        
        # ========== RECOMMENDATIONS ==========
        st.markdown("---")
        st.markdown("## 🚀 Growth Recommendations")
        
        recommendations = []
        
        if not product_performance.empty:
            top_product_name = product_performance.iloc[0]['Product'].split('-')[0] if '-' in product_performance.iloc[0]['Product'] else product_performance.iloc[0]['Product']
            recommendations.append(f"1. **Push the {top_product_name} aggressively** - It's your highest revenue product")
        
        recommendations.extend([
            "2. **Use sachets as sampling tools** - Always upsell: 'The bottle gives much better value'",
            "3. **Build a hotel channel** - Create hotel starter packs and refill programs",
            "4. **Track repeat customers** - Add 'First Purchase' and 'Repeat Purchase' flags",
            "5. **Standardize location names** - Use dropdown instead of free text"
        ])
        
        for rec in recommendations:
            st.info(rec)
        
        # ========== REVENUE MIX ==========
        st.markdown("---")
        st.markdown("## 📊 Revenue Mix")
        
        # Categorize products
        def categorize_product(product):
            if 'Bottle' in str(product):
                return 'Bottles'
            elif 'Sachet' in str(product):
                return 'Sachets'
            elif 'Refill' in str(product):
                return 'Refills'
            elif 'Hot Sauce' in str(product):
                return 'Hot Sauce'
            else:
                return 'Other'
        
        if 'Product' in sales_df.columns:
            sales_df['Category'] = sales_df['Product'].apply(categorize_product)
            category_mix = sales_df.groupby('Category')['Total'].sum().reset_index()
            
            if not category_mix.empty:
                fig = px.pie(category_mix, values='Total', names='Category',
                            title='Revenue by Product Category',
                            color_discrete_sequence=px.colors.qualitative.Set2,
                            hole=0.3)
                st.plotly_chart(fig, width='stretch')
        
        # ========== BUSINESS HEALTH VERDICT ==========
        st.markdown("---")
        st.markdown("## 🩺 Founder's Verdict")
        
        if total_sales_value > 10000:
            verdict = "✅ **HEALTHY** - Your business is generating meaningful revenue. Focus on repeat customers and upselling."
        elif total_sales_value > 5000:
            verdict = "📈 **GROWING** - You're building momentum. Double down on what worked in your best month."
        else:
            verdict = "🌱 **EARLY STAGE** - Focus on customer acquisition and product awareness."
        
        st.info(verdict)
        
    else:
        st.info("No sales data available. Add sales to generate business intelligence report.")

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
            total_kg = st.number_input("Total KG Produced", min_value=0.1, step=0.1, value=2.0, key="total_kg")
        
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
            refill_100g_qty = st.number_input("100g Refills (KES 120)", min_value=0, step=10, value=0, key="refill_100")
        
        total_units = sachet_5_qty + sachet_30_qty + bottle_100g_qty + refill_100g_qty
        st.info(f"📦 **Total Units Produced:** {total_units:,}")
        
        notes = st.text_area("Production Notes", placeholder="Any issues or observations?", key="prod_notes")
        
        

        if st.button("✅ Save Production Batch", type="primary", use_container_width=True):
            if not batch_number:
                st.error("Please enter a batch number!")
            elif total_units == 0:
                st.warning("Please enter at least one finished good quantity!")
            else:
        # Calculate materials needed based on recipe
             materials_needed = {
            'Salt': total_kg * 0.50,
            'African Birds Eye': total_kg * 0.30,
            'Cayenne Pepper': total_kg * 0.15,
            'Onion Powder': total_kg * 0.02,
            'Garlic Powder': total_kg * 0.02,
            'Paprika': total_kg * 0.01
        }
        
        # Check if enough stock is available for ALL materials
            sufficient = True
            insufficient_materials = []
        
            for mat_name, needed in materials_needed.items():
                current = get_current_material_balance(mat_name)
                st.write(f"DEBUG: {mat_name} - Need: {needed:.2f}kg, Have: {current:.2f}kg")  # Debug line
                if current < needed:
                    sufficient = False
                    insufficient_materials.append(f"{mat_name} (need {needed:.2f}kg, have {current:.2f}kg)")
        
            if not sufficient:
                st.error("❌ Cannot create batch due to insufficient materials:")
                for msg in insufficient_materials:
                    st.write(f"  - {msg}")
            else:
            # Save batch to BATCHES table
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
                st.write(f"✅ Batch saved with ID: {batch_id}")
                
                # Record material usage for each ingredient
                usage_success = True
                for mat_name, needed in materials_needed.items():
                    st.write(f"Recording usage: {mat_name} - {needed}kg")
                    cost_per_kg = 100
                    success = record_material_usage_with_balance(batch_id, mat_name, needed, production_date)
                    if not success:
                        usage_success = False
                        st.error(f"Failed to record usage for {mat_name}")
                
                if usage_success:
                    # Save production outputs (finished goods)
                    outputs = [
                        ("Sachet 5", sachet_5_qty, 5),
                        ("Sachet 30", sachet_30_qty, 30),
                        ("Bottle 100g", bottle_100g_qty, 150),
                        ("Refill 100g", refill_100g_qty, 120)
                    ]
                    
                    for product_type, qty, price in outputs:
                        if qty > 0:
                            save_production_output({
                                "batch_id": batch_id,
                                "product_type": product_type,
                                "quantity_produced": qty,
                                "unit_price": price
                            })

                            update_finished_goods_production(product_type, qty)
                    
                    st.success(f"✅ Batch {batch_number} saved successfully!")
                    st.balloons()
                    
                    # Show what was deducted
                    st.info("📦 Materials deducted from inventory:")
                    for mat_name, needed in materials_needed.items():
                        st.write(f"  - {mat_name}: {needed:.2f}kg")
                    
                    st.rerun()
                else:
                    st.error("❌ Batch saved but inventory update failed!")
            else:
                st.error("❌ Failed to save batch!")
    
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
                restock_qty = st.number_input("Quantity (KG)", min_value=0.1, step=0.1, value=5.0, key="restock_qty")
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
    
    # ========== FINISHED GOODS TAB ==========
with prod_tab4:
    st.markdown("### 📦 Finished Goods Inventory")
    
    finished_goods = get_finished_goods()
    if finished_goods:
        df_finished = pd.DataFrame(finished_goods)
        
        # Display current stock metrics
        st.subheader("📊 Current Stock Levels")
        
        # Fixed: Handle any number of products (1-4)
        num_products = len(df_finished)
        if num_products <= 4:
            cols = st.columns(num_products)
            for idx, row in df_finished.iterrows():
                with cols[idx]:
                    st.metric(
                        row['product_type'], 
                        f"{row['current_stock']} units",
                        delta=f"Sold: {row.get('total_sold', 0)}"
                    )
        else:
            # If more than 4 products, show in rows of 4
            rows = (num_products + 3) // 4
            for r in range(rows):
                cols = st.columns(4)
                for c in range(4):
                    product_idx = r * 4 + c
                    if product_idx < num_products:
                        row = df_finished.iloc[product_idx]
                        with cols[c]:
                            st.metric(
                                row['product_type'], 
                                f"{row['current_stock']} units",
                                delta=f"Sold: {row.get('total_sold', 0)}"
                            )
        
        # Stock table
        st.dataframe(
            df_finished[['product_type', 'current_stock', 'total_produced', 'total_sold', 'reorder_level']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "product_type": "Product",
                "current_stock": st.column_config.NumberColumn("Current Stock", format="%d"),
                "total_produced": st.column_config.NumberColumn("Total Produced", format="%d"),
                "total_sold": st.column_config.NumberColumn("Total Sold", format="%d"),
                "reorder_level": st.column_config.NumberColumn("Reorder at", format="%d")
            }
        )
        
        # Stock level visualization
        fig = px.bar(df_finished, x='product_type', y='current_stock', 
                    title='Current Finished Goods Stock',
                    color='current_stock',
                    color_continuous_scale='RdYlGn',
                    text='current_stock')
        fig.update_traces(texttemplate='%{text} units', textposition='outside')
        fig.add_hline(y=100, line_dash="dash", line_color="red", 
                     annotation_text="Reorder Alert (100 units)")
        st.plotly_chart(fig, width='stretch')
        
        # Low stock warnings
        low_stock = df_finished[df_finished['current_stock'] < df_finished['reorder_level']]
        if not low_stock.empty:
            st.warning("⚠️ **Low Stock Alert!** The following products need production:")
            for _, item in low_stock.iterrows():
                st.write(f"- {item['product_type']}: {item['current_stock']} units left (Reorder at {item['reorder_level']})")
    else:
        st.info("No finished goods data available")

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
                st.plotly_chart(fig, width='stretch')
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
        st.plotly_chart(fig, width='stretch')
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
    st.plotly_chart(fig, width='stretch')
    
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

# ==================== TAB 8: ASSETS & EQUIPMENT ====================
with tab8:
    st.markdown('<div class="section-header">🏭 Assets & Equipment Management</div>', unsafe_allow_html=True)
    
    # Summary Cards at the top
    st.subheader("📊 Asset Summary")
    
    # Get assets from database
    assets_list = get_assets()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_assets = len(assets_list)
        st.metric("Total Assets", total_assets)
    with col2:
        total_value = sum([a.get('purchase_cost', 0) for a in assets_list]) if assets_list else 0
        st.metric("Total Asset Value", f"KES {total_value:,.0f}")
    with col3:
        # Calculate total depreciation
        total_depreciation = sum([a.get('purchase_cost', 0) - a.get('current_value', a.get('purchase_cost', 0)) for a in assets_list]) if assets_list else 0
        st.metric("Total Depreciation", f"KES {total_depreciation:,.0f}")
    with col4:
        current_value = total_value - total_depreciation
        st.metric("Current Value", f"KES {current_value:,.0f}")
    
    st.markdown("---")
    
    # ========== REFUND SECTION ==========
    with st.expander("💰 Record Refund (Money Coming Back)", expanded=False):
        st.info("📌 Use this for deposit refunds, supplier refunds, or any money you receive back")
        
        col1, col2 = st.columns(2)
        with col1:
            refund_amount = st.number_input("Refund Amount (KES)", min_value=0, step=1000, value=0, key="refund_amount_input")
            refund_date = st.date_input("Refund Date", value=date.today(), key="refund_date_input")
            refund_category = st.selectbox("Refund Type", ["Deposit Refund", "Supplier Refund", "Customer Refund", "Other"], key="refund_category_select")
        with col2:
            refund_source = st.text_input("Refund From", placeholder="e.g., Landlord, Supplier", key="refund_source_input")
            refund_description = st.text_area("Description", placeholder="e.g., Office deposit refund after canceling lease", key="refund_description_area")
        
        if st.button("💰 Record Refund", type="primary", use_container_width=True, key="record_refund_btn"):
            if refund_amount > 0:
                # Record as negative expense
                expense_record = {
                    "date": str(refund_date),
                    "category": refund_category,
                    "description": f"Refund from {refund_source} - {refund_description}",
                    "amount": -refund_amount,
                    "payment_method": "Bank Transfer",
                    "paid_by": refund_source,
                    "receipt": "",
                    "status": "Received"
                }
                save_expense(expense_record)
                st.success(f"✅ Refund of KES {refund_amount:,.0f} recorded!")
                st.info("💰 Money ADDED back to your cash balance")
                st.balloons()
                st.rerun()
            else:
                st.error("Please enter a refund amount")
    
    st.markdown("---")
    
    # ========== ADD NEW ASSET ==========
    with st.expander("➕ Add New Equipment/Asset", expanded=False):
        st.markdown("Record new equipment like grinder, mixer, etc.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            asset_name = st.text_input("Asset Name", placeholder="e.g., Commercial Grinder, Industrial Mixer", key="asset_name_input")
            asset_type = st.selectbox("Asset Type", ["Equipment", "Machinery", "Vehicle", "Furniture", "Office", "Other"], key="asset_type_select")
            purchase_date = st.date_input("Purchase Date", value=date.today(), key="asset_purchase_date")
            purchase_cost = st.number_input("Purchase Cost (KES)", min_value=0, step=1000, value=0, key="asset_purchase_cost")
        
        with col2:
            useful_life = st.number_input("Useful Life (Years)", min_value=1, max_value=20, value=5, key="asset_useful_life")
            supplier_name = st.text_input("Supplier", placeholder="e.g., Jumia, Local Store", key="asset_supplier_input")
            warranty_until = st.date_input("Warranty Until", value=date.today() + timedelta(days=365), key="asset_warranty_date")
            asset_notes = st.text_area("Notes", placeholder="Model number, specifications, etc.", key="asset_notes_area")
        
        if st.button("💾 Save Asset", type="primary", use_container_width=True, key="save_asset_btn"):
            if asset_name and purchase_cost > 0:
                # Save to ASSETS table
                asset_data = {
                    "asset_name": asset_name,
                    "asset_type": asset_type,
                    "purchase_date": str(purchase_date),
                    "purchase_cost": purchase_cost,
                    "current_value": purchase_cost,
                    "useful_life_years": useful_life,
                    "supplier": supplier_name,
                    "warranty_until": str(warranty_until),
                    "notes": asset_notes,
                    "status": "Active"
                }
                
                asset_id = save_asset(asset_data)
                
                if asset_id:
                    # Also record as expense
                    expense_record = {
                        "date": str(purchase_date),
                        "category": "Equipment Purchase",
                        "description": f"Purchased {asset_name} from {supplier_name} - {asset_notes}",
                        "amount": purchase_cost,
                        "payment_method": "Bank Transfer",
                        "paid_by": "Business",
                        "receipt": "",
                        "status": "Paid"
                    }
                    save_expense(expense_record)
                    
                    st.success(f"✅ Asset '{asset_name}' recorded successfully!")
                    st.info(f"💰 KES {purchase_cost:,.0f} recorded as equipment expense")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to save asset to database")
            else:
                st.error("Please enter Asset Name and Purchase Cost")
    
    st.markdown("---")
    
    # ========== DISPLAY ASSETS ==========
    st.markdown("### 📋 Current Assets & Equipment")
    
    if assets_list:
        # Create DataFrame for display
        df_assets = pd.DataFrame(assets_list)
        df_assets['purchase_date'] = pd.to_datetime(df_assets['purchase_date']).dt.strftime('%Y-%m-%d')
        df_assets['purchase_cost'] = df_assets['purchase_cost'].apply(lambda x: f"KES {x:,.0f}")
        
        # Calculate depreciation
        df_assets['current_value'] = df_assets['current_value'].apply(lambda x: f"KES {x:,.0f}" if x else "N/A")
        
        st.dataframe(
            df_assets[['asset_name', 'asset_type', 'purchase_date', 'purchase_cost', 'current_value', 'supplier', 'status']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "asset_name": "Asset Name",
                "asset_type": "Type",
                "purchase_date": "Purchase Date",
                "purchase_cost": "Purchase Cost",
                "current_value": "Current Value",
                "supplier": "Supplier",
                "status": "Status"
            }
        )
        
        # Asset type distribution chart
        st.markdown("### 📊 Asset Distribution")
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart by asset type
            asset_type_summary = df_assets.groupby('asset_type').size().reset_index(name='count')
            fig = px.pie(asset_type_summary, values='count', names='asset_type', title='Assets by Type')
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            # Bar chart of asset values
            asset_value_data = pd.DataFrame(assets_list)
            asset_value_data['value'] = asset_value_data['purchase_cost']
            fig = px.bar(asset_value_data, x='asset_name', y='value', title='Asset Values',
                        color='asset_type', text='value')
            fig.update_traces(texttemplate='KES %{text:,.0f}', textposition='outside')
            fig.update_layout(xaxis_title='Asset', yaxis_title='Value (KES)')
            st.plotly_chart(fig, width='stretch')
        
        # Depreciation schedule
        st.markdown("### 📉 Depreciation Schedule")
        st.info("Linear depreciation over useful life")
        
        depreciation_data = []
        for asset in assets_list:
            annual_dep = asset['purchase_cost'] / asset['useful_life_years']
            monthly_dep = annual_dep / 12
            depreciation_data.append({
                'Asset': asset['asset_name'],
                'Cost': f"KES {asset['purchase_cost']:,.0f}",
                'Useful Life': f"{asset['useful_life_years']} years",
                'Annual Depreciation': f"KES {annual_dep:,.0f}",
                'Monthly Depreciation': f"KES {monthly_dep:,.0f}"
            })
        
        st.dataframe(pd.DataFrame(depreciation_data), use_container_width=True, hide_index=True)
        
    else:
        st.info("No assets recorded yet. Add your grinder and mixer using the form above!")
        
        # Show equipment purchases from expenses as fallback
        if not expenses_df.empty:
            equipment_expenses = expenses_df[expenses_df['category'].str.contains('Equipment', case=False, na=False)]
            if not equipment_expenses.empty:
                st.markdown("### 📋 Recent Equipment Purchases (from Expenses)")
                display_df = equipment_expenses.copy()
                display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
                display_df['amount'] = display_df['amount'].apply(lambda x: f"KES {x:,.0f}")
                st.dataframe(display_df[['date', 'description', 'amount']], use_container_width=True, hide_index=True)

# ==================== TAB 9: DAILY SALES ENTRY ====================
with tab9:
    st.markdown('<div class="section-header">📝 Daily Sales Entry</div>', unsafe_allow_html=True)
    
    st.info("💡 **Quick Daily Sales Entry** - Record your opening stock (morning) and closing stock (afternoon) to calculate what you sold")
    
    # Date selector
    sale_date = st.date_input("Sale Date", value=date.today(), key="daily_sale_date")
    
    # ========== STOCK TRACKING SECTION ==========
    st.markdown("### 📦 Stock Tracking")
    st.caption("Enter your stock levels to automatically calculate what you sold")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌅 Opening Stock (Morning)")
        opening_3 = st.number_input("3 KES Sachet - Opening", min_value=0, step=1, value=0, key="opening_3")
        opening_5 = st.number_input("5 KES Sachet - Opening", min_value=0, step=1, value=0, key="opening_5")
        opening_10 = st.number_input("10 KES Sachet - Opening", min_value=0, step=1, value=0, key="opening_10")
        opening_20 = st.number_input("20 KES Sachet - Opening", min_value=0, step=1, value=0, key="opening_20")
        opening_30 = st.number_input("30 KES Sachet - Opening", min_value=0, step=1, value=0, key="opening_30")
        opening_40 = st.number_input("40 KES Sachet - Opening", min_value=0, step=1, value=0, key="opening_40")
        opening_bottle = st.number_input("100g Bottle - Opening", min_value=0, step=1, value=0, key="opening_bottle")
        opening_refill = st.number_input("100g Refill - Opening", min_value=0, step=1, value=0, key="opening_refill")
    
    with col2:
        st.markdown("#### 🌇 Closing Stock (Afternoon)")
        closing_3 = st.number_input("3 KES Sachet - Closing", min_value=0, step=1, value=0, key="closing_3")
        closing_5 = st.number_input("5 KES Sachet - Closing", min_value=0, step=1, value=0, key="closing_5")
        closing_10 = st.number_input("10 KES Sachet - Closing", min_value=0, step=1, value=0, key="closing_10")
        closing_20 = st.number_input("20 KES Sachet - Closing", min_value=0, step=1, value=0, key="closing_20")
        closing_30 = st.number_input("30 KES Sachet - Closing", min_value=0, step=1, value=0, key="closing_30")
        closing_40 = st.number_input("40 KES Sachet - Closing", min_value=0, step=1, value=0, key="closing_40")
        closing_bottle = st.number_input("100g Bottle - Closing", min_value=0, step=1, value=0, key="closing_bottle")
        closing_refill = st.number_input("100g Refill - Closing", min_value=0, step=1, value=0, key="closing_refill")
    
    # Calculate what was sold (Opening - Closing)
    sold_3 = opening_3 - closing_3
    sold_5 = opening_5 - closing_5
    sold_10 = opening_10 - closing_10
    sold_20 = opening_20 - closing_20
    sold_30 = opening_30 - closing_30
    sold_40 = opening_40 - closing_40
    sold_bottle = opening_bottle - closing_bottle
    sold_refill = opening_refill - closing_refill
    
    # Validate that sold quantities are not negative
    valid = True
    if sold_3 < 0 or sold_5 < 0 or sold_10 < 0 or sold_20 < 0 or sold_30 < 0 or sold_40 < 0 or sold_bottle < 0 or sold_refill < 0:
        st.error("❌ Closing stock cannot be greater than opening stock! Please check your numbers.")
        valid = False
    
    # ========== CALCULATED SALES SECTION ==========
    if valid:
        st.markdown("---")
        st.markdown("### 📊 Calculated Sales (Based on Stock Difference)")
        
        # Calculate revenue
        revenue_3 = sold_3 * 3
        revenue_5 = sold_5 * 5
        revenue_10 = sold_10 * 10
        revenue_20 = sold_20 * 20
        revenue_30 = sold_30 * 30
        revenue_40 = sold_40 * 40
        revenue_bottle = sold_bottle * 150
        revenue_refill = sold_refill * 120
        
        total_quantity = sold_5 + sold_10 + sold_20 + sold_30 + sold_40 + sold_bottle + sold_refill
        total_revenue = revenue_5 + revenue_10 + revenue_20 + revenue_30 + revenue_40 + revenue_bottle + revenue_refill
        
        # Display summary of what was sold
        summary_data = []
        if sold_3 > 0:
            summary_data.append({"Product": "3 KES Sachet", "Sold": sold_3, "Unit Price": 3, "Total": revenue_3})
        if sold_5 > 0:
            summary_data.append({"Product": "5 KES Sachet", "Sold": sold_5, "Unit Price": 5, "Total": revenue_5})
        if sold_10 > 0:
            summary_data.append({"Product": "10 KES Sachet", "Sold": sold_10, "Unit Price": 10, "Total": revenue_10})
        if sold_20 > 0:
            summary_data.append({"Product": "20 KES Sachet", "Sold": sold_20, "Unit Price": 20, "Total": revenue_20})
        if sold_30 > 0:
            summary_data.append({"Product": "30 KES Sachet", "Sold": sold_30, "Unit Price": 30, "Total": revenue_30})
        if sold_40 > 0:
            summary_data.append({"Product": "40 KES Sachet", "Sold": sold_40, "Unit Price": 40, "Total": revenue_40})
        if sold_bottle > 0:
            summary_data.append({"Product": "100g Bottle", "Sold": sold_bottle, "Unit Price": 150, "Total": revenue_bottle})
        if sold_refill > 0:
            summary_data.append({"Product": "100g Refill", "Sold": sold_refill, "Unit Price": 120, "Total": revenue_refill})
        
        if summary_data:
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True, hide_index=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📦 Total Units Sold", f"{total_quantity:,}")
            with col2:
                st.metric("💰 Total Revenue", f"KES {total_revenue:,.0f}")
            with col3:
                avg_price = total_revenue / total_quantity if total_quantity > 0 else 0
                st.metric("📊 Average Price", f"KES {avg_price:.2f}")
        else:
            st.warning("No sales detected. Opening and closing stock are the same.")
        
        # ========== CUSTOMER & PAYMENT INFO ==========
        st.markdown("---")
        st.markdown("### 👤 Customer & Payment Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            customer_name = st.text_input("Customer Name", placeholder="e.g., Mama Mboga, Hotel Name", key="daily_customer")
            customer_type = st.selectbox(
                "Customer Type",
                ["Consumer (B2C)", "Shop/Mama Mboga (B2B)", "Hotel/Restaurant"],
                key="daily_customer_type"
            )
            payment_status = st.selectbox("Payment Status", ["Cash", "Credit / Pending"], key="daily_payment")
            location = st.text_input("Location", placeholder="e.g., Nairobi CBD", key="daily_location")
        
        with col2:
            if sales_person_options:
                sales_person_name = st.selectbox("Sales Person", ["Select..."] + list(sales_person_options.keys()), key="daily_sales_person")
            else:
                sales_person_name = "N/A"
                st.warning("No salespeople added yet.")
            phone = st.text_input("Phone Number", placeholder="Optional", key="daily_phone")
            feedback = st.text_area("Customer Feedback", placeholder="Any feedback from customer...", key="daily_feedback")
        
        # ========== SUBMIT BUTTON ==========
                # ========== SUBMIT BUTTON ==========
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_sale = st.button("💾 Save All Sales", type="primary", use_container_width=True)
        
        if submit_sale:
            if total_quantity == 0:
                st.error("No sales to record! Opening and closing stock are the same.")
            elif customer_name.strip() == "":
                st.error("Please enter customer name!")
            elif sales_person_name == "Select...":
                st.error("Please select a salesperson!")
            else:
                # Initialize counter OUTSIDE the function
                sales_recorded = 0
                errors = []
                
                # Helper function to save each sale
                def save_individual_sale(product_name, quantity, price, total):
                    # Use a mutable object or return value instead of nonlocal
                    if quantity > 0:
                        sale_record = {
                            "Date": str(sale_date),
                            "Name": customer_name,
                            "Phone": phone,
                            "Location": location,
                            "Product": product_name,
                            "Product_Type": product_name,
                            "Customer_Type": customer_type,
                            "Unit": "units",
                            "Quantity": quantity,
                            "Price_per_Unit": price,
                            "Total": total,
                            "Payment_Status": payment_status,
                            "Feedback": feedback,
                            "Follow_Up": "",
                            "Is_Refill": "Refill" in product_name,
                            "Tracking_Hotel": customer_name if customer_type == "Hotel/Restaurant" else None,
                            "Tracking_Mama": customer_name if customer_type == "Shop/Mama Mboga (B2B)" else None
                        }
                        
                        sale_id = save_sale(sale_record)
                        
                        if sale_id:
                            # Update finished goods inventory
                            product_mapping = { "3 KES Sachet": "Sachet 3",
                                "5 KES Sachet": "Sachet 5",
                                "10 KES Sachet": "Sachet 10",
                                "20 KES Sachet": "Sachet 20",
                                "30 KES Sachet": "Sachet 30",
                                "40 KES Sachet": "Sachet 40",
                                "100g Bottle": "Bottle 100g",
                                "100g Refill": "Refill 100g"
                            }
                            mapped_product = product_mapping.get(product_name, None)
                            if mapped_product:
                                update_finished_goods_sale(mapped_product, quantity)
                            
                            # Save distribution if salesperson selected
                            if sales_person_name not in ["Select...", "N/A"] and sales_person_name in sales_person_options:
                                save_distribution(
                                    sale_id=sale_id,
                                    sales_person_id=sales_person_options[sales_person_name],
                                    quantity=quantity,
                                    sale_date=str(sale_date),
                                    price=price,
                                    sale_data=sale_record
                                )
                            return True
                        else:
                            errors.append(product_name)
                            return False
                    return True  # No sale to record is fine
                
                # Save each product that was sold
                success = True
                sold_products = [
                    (sold_3, "3 KES Sachet", 3, revenue_3),
                    (sold_5, "5 KES Sachet", 5, revenue_5),
                    (sold_10, "10 KES Sachet", 10, revenue_10),
                    (sold_20, "20 KES Sachet", 20, revenue_20),
                    (sold_30, "30 KES Sachet", 30, revenue_30),
                    (sold_40, "40 KES Sachet", 40, revenue_40),
                    (sold_bottle, "100g Bottle", 150, revenue_bottle),
                    (sold_refill, "100g Refill", 120, revenue_refill)
                ]
                
                for sold_qty, product_name, price, revenue in sold_products:
                    if sold_qty > 0:
                        if save_individual_sale(product_name, sold_qty, price, revenue):
                            sales_recorded += 1
                        else:
                            success = False
                
                if success and sales_recorded > 0:
                    st.success(f"✅ Successfully recorded {sales_recorded} sale(s) for {customer_name}!")
                    st.balloons()
                elif errors:
                    st.error(f"❌ Failed to record: {', '.join(errors)}")
                else:
                    st.error("❌ Failed to record sales. Please check and try again.")

# ==================== TAB 10: STOCK RECONCILIATION ====================
with tab10:
    st.markdown('<div class="section-header">📊 Daily Stock Reconciliation</div>', unsafe_allow_html=True)
    
    st.info("📌 **Track your daily stock movement:** Record what you went out with, what you came back with, and what you gave for free")
    
    # Date selector
    recon_date = st.date_input("Reconciliation Date", value=date.today(), key="recon_date")
    
    # Check if date already has records
    existing_summary = get_daily_summary(recon_date)
    if existing_summary:
        st.warning(f"⚠️ Records already exist for {recon_date}. You can add more products or update existing ones.")
    
    st.markdown("---")
    st.markdown("### 📦 Product Stock Entry")
    
    # Product selection
    products = [
        ("5 KES Sachet", 5),
        ("10 KES Sachet", 10),
        ("20 KES Sachet", 20),
        ("30 KES Sachet", 30),
        ("40 KES Sachet", 40),
        ("100g Bottle", 150),
        ("100g Refill", 120)
    ]
    
    # Create expandable sections for each product
    reconciliation_records = []
    
    for product_name, unit_price in products:
        with st.expander(f"📦 {product_name} - KES {unit_price}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                opening = st.number_input(
                    f"Opening Stock (went out with)", 
                    min_value=0, 
                    step=1, 
                    value=0, 
                    key=f"opening_{product_name.replace(' ', '_')}"
                )
            
            with col2:
                closing = st.number_input(
                    f"Closing Stock (came back with)", 
                    min_value=0, 
                    step=1, 
                    value=0, 
                    key=f"closing_{product_name.replace(' ', '_')}"
                )
            
            with col3:
                given_free = st.number_input(
                    f"Given for Free (promotions/damages)", 
                    min_value=0, 
                    step=1, 
                    value=0, 
                    key=f"free_{product_name.replace(' ', '_')}"
                )
            
            # Calculate sold
            sold = opening - closing - given_free
            
            if sold > 0:
                st.success(f"📊 **Calculated Sold:** {sold} units = KES {sold * unit_price:,.0f}")
                reconciliation_records.append({
                    "product_name": product_name,
                    "opening_stock": opening,
                    "closing_stock": closing,
                    "given_free": given_free,
                    "sold_quantity": sold,
                    "unit_price": unit_price,
                    "total_revenue": sold * unit_price
                })
            elif sold < 0:
                st.error(f"❌ **Error:** Closing stock + given free cannot exceed opening stock! (Opening: {opening}, Closing: {closing}, Free: {given_free})")
            else:
                st.info("📊 No sales recorded for this product.")
    
    # Summary of all products
    st.markdown("---")
    st.markdown("### 📊 Daily Summary")
    
    if reconciliation_records:
        df_summary = pd.DataFrame(reconciliation_records)
        total_sold = df_summary['sold_quantity'].sum()
        total_revenue = df_summary['total_revenue'].sum()
        total_free = df_summary['given_free'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 Total Units Sold", f"{total_sold:,}")
        with col2:
            st.metric("💰 Total Revenue", f"KES {total_revenue:,.0f}")
        with col3:
            st.metric("🎁 Given Free", f"{total_free:,}")
        with col4:
            avg_price = total_revenue / total_sold if total_sold > 0 else 0
            st.metric("📊 Average Price", f"KES {avg_price:.2f}")
        
        # Display detailed table
        st.dataframe(
            df_summary[['product_name', 'opening_stock', 'closing_stock', 'given_free', 'sold_quantity', 'total_revenue']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "product_name": "Product",
                "opening_stock": "Opening",
                "closing_stock": "Closing",
                "given_free": "Given Free",
                "sold_quantity": "Sold",
                "total_revenue": st.column_config.NumberColumn("Revenue", format="KES %d")
            }
        )
        
        # Additional info
        st.markdown("---")
        st.markdown("### 📝 Additional Information")
        
        col1, col2 = st.columns(2)
        with col1:
            sales_person = st.selectbox("Sales Person", ["Select..."] + list(sales_person_options.keys()) if sales_person_options else ["N/A"], key="recon_sales_person")
            location = st.text_input("Location", placeholder="e.g., Nairobi CBD", key="recon_location")
        with col2:
            notes = st.text_area("Daily Notes", placeholder="Any observations, challenges, or notable events...", key="recon_notes")
        
        # Save button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            save_recon = st.button("💾 Save Stock Reconciliation", type="primary", use_container_width=True)
        
        if save_recon:
            if sales_person == "Select...":
                st.error("Please select a sales person!")
            else:
                saved_count = 0
                for record in reconciliation_records:
                    recon_data = {
                        "reconciliation_date": str(recon_date),
                        "product_name": record['product_name'],
                        "opening_stock": record['opening_stock'],
                        "closing_stock": record['closing_stock'],
                        "given_free": record['given_free'],
                        "unit_price": record['unit_price'],
                        "notes": notes
                    }
                    
                    result = save_daily_stock_reconciliation(recon_data)
                    if result:
                        saved_count += 1
                        
                        # Also create actual sale records for the sold items
                        if record['sold_quantity'] > 0:
                            sale_record = {
                                "Date": str(recon_date),
                                "Name": f"Daily Stock Sale - {recon_date}",
                                "Phone": "",
                                "Location": location,
                                "Product": record['product_name'],
                                "Product_Type": record['product_name'],
                                "Customer_Type": "Consumer (B2C)",
                                "Unit": "units",
                                "Quantity": record['sold_quantity'],
                                "Price_per_Unit": record['unit_price'],
                                "Total": record['total_revenue'],
                                "Payment_Status": "Cash",
                                "Feedback": notes,
                                "Follow_Up": "",
                                "Is_Refill": "Refill" in record['product_name'],
                                "Tracking_Hotel": None,
                                "Tracking_Mama": None
                            }
                            save_sale(sale_record)
                            
                            # Update finished goods inventory
                            product_mapping = {
                                "5 KES Sachet": "Sachet 5",
                                "10 KES Sachet": "Sachet 10",
                                "20 KES Sachet": "Sachet 20",
                                "30 KES Sachet": "Sachet 30",
                                "40 KES Sachet": "Sachet 40",
                                "100g Bottle": "Bottle 100g",
                                "100g Refill": "Refill 100g"
                            }
                            mapped_product = product_mapping.get(record['product_name'], None)
                            if mapped_product:
                                update_finished_goods_sale(mapped_product, record['sold_quantity'])
                
                if saved_count > 0:
                    st.success(f"✅ Successfully saved {saved_count} product records for {recon_date}!")
                    st.balloons()
                else:
                    st.error("Failed to save records. Please try again.")
    else:
        st.warning("No products with valid sales data. Please enter stock information above.")
    
    # ========== VIEW HISTORY ==========
    st.markdown("---")
    st.markdown("### 📋 Reconciliation History")
    
    # Date filter for history
    col1, col2 = st.columns(2)
    with col1:
        history_date = st.date_input("View History for Date", value=date.today(), key="history_date")
    with col2:
        show_history = st.button("📊 Show History", use_container_width=True)
    
    if show_history:
        history_records = get_daily_stock_reconciliation(date_filter=history_date)
        if history_records:
            df_history = pd.DataFrame(history_records)
            df_history['total_revenue'] = df_history['total_revenue'].apply(lambda x: f"KES {x:,.0f}")
            st.dataframe(
                df_history[['product_name', 'opening_stock', 'closing_stock', 'given_free', 'sold_quantity', 'total_revenue']],
                use_container_width=True,
                hide_index=True
            )
            
            # Summary for the date
            total_sold_history = df_history['sold_quantity'].sum()
            total_revenue_history = df_history['total_revenue'].str.replace('KES ', '').str.replace(',', '').astype(float).sum()
            st.metric(f"Total for {history_date}", f"KES {total_revenue_history:,.0f} from {total_sold_history} units")
        else:
            st.info(f"No records found for {history_date}")


# ==================== TAB 11: PROFIT CALCULATOR ====================
with tab11:
    st.markdown('<div class="section-header">💰 Profit Calculator</div>', unsafe_allow_html=True)
    
    st.info("📊 **Calculate profit margins for each product based on ingredient costs, packaging, and selling price**")
    
    # ========== COST CONFIGURATION ==========
    with st.expander("⚙️ Cost Configuration", expanded=True):
        st.markdown("### 📦 Raw Material & Packaging Costs")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Raw Materials**")
            cost_per_gram = st.number_input("Cost per gram (KES)", min_value=0.0, step=0.01, value=0.34, key="cost_per_gram")
            st.caption("Current: KES 0.34 per gram")
        
        with col2:
            st.markdown("**Packaging Costs**")
            label_cost = st.number_input("Label cost (KES)", min_value=0.0, step=1.0, value=11.0, key="label_cost")
            bottle_cost = st.number_input("Bottle cost (KES)", min_value=0.0, step=1.0, value=12.0, key="bottle_cost")
            sachet_cost = st.number_input("Sachet packaging cost (KES)", min_value=0.0, step=0.5, value=0.5, key="sachet_cost")
    
    # ========== PRODUCT PROFIT CALCULATIONS ==========
    st.markdown("---")
    st.markdown("### 📊 Product Profitability Analysis")
    
    # Define all products
    products = [
        # Sachets
        {"name": "1.5g Sachet (Street)", "weight_g": 1.5, "b2b_price": None, "b2c_price": 10.0, "channel": "Street"},
        {"name": "1.5g Sachet (School)", "weight_g": 1.5, "b2b_price": 5.0, "b2c_price": None, "channel": "School B2B"},
        {"name": "1.5g Sachet (B2B)", "weight_g": 1.5, "b2b_price": 2.9, "b2c_price": None, "channel": "Wholesale"},
        {"name": "5g Sachet", "weight_g": 5.0, "b2b_price": None, "b2c_price": 20.0, "channel": "Retail"},
        {"name": "10g Sachet (B2B)", "weight_g": 10.0, "b2b_price": 30.0, "b2c_price": None, "channel": "Wholesale"},
        {"name": "10g Sachet (B2C)", "weight_g": 10.0, "b2b_price": None, "b2c_price": 40.0, "channel": "Retail"},
        # Bottles
        {"name": "100g Bottle (B2B)", "weight_g": 100.0, "b2b_price": 150.0, "b2c_price": None, "channel": "Wholesale", "uses_bottle": True},
        {"name": "100g Bottle (B2C)", "weight_g": 100.0, "b2b_price": None, "b2c_price": 200.0, "channel": "Retail", "uses_bottle": True},
        {"name": "100g Refill (B2B)", "weight_g": 100.0, "b2b_price": 100.0, "b2c_price": None, "channel": "Refill Wholesale", "uses_bottle": False},
        {"name": "100g Refill (B2C)", "weight_g": 100.0, "b2b_price": None, "b2c_price": 120.0, "channel": "Refill Retail", "uses_bottle": False},
    ]
    
    # Calculate for each product
    results = []
    
    for product in products:
        # Calculate ingredient cost
        ingredient_cost = product["weight_g"] * cost_per_gram
        
        # Calculate packaging cost
        packaging_cost = 0
        if "sachet" in product["name"].lower():
            packaging_cost = sachet_cost
        elif "bottle" in product["name"].lower() and product.get("uses_bottle", True):
            packaging_cost = label_cost + bottle_cost
        elif "refill" in product["name"].lower():
            packaging_cost = label_cost  # Refill only needs label, no bottle
        
        total_cost = ingredient_cost + packaging_cost
        
        # Get selling price
        selling_price = product.get("b2b_price") if product.get("b2b_price") else product.get("b2c_price")
        channel = product.get("channel", "Retail")
        
        # Calculate profit
        profit = selling_price - total_cost
        profit_margin = (profit / selling_price) * 100 if selling_price and selling_price > 0 else 0
        
        results.append({
            "Product": product["name"],
            "Channel": channel,
            "Weight (g)": product["weight_g"],
            "Ingredient Cost": ingredient_cost,
            "Packaging Cost": packaging_cost,
            "Total Cost": total_cost,
            "Selling Price": selling_price,
            "Profit": profit,
            "Margin %": profit_margin
        })
    
    # Display results table - format for display only
    df_results = pd.DataFrame(results)
    
    # Create formatted version for display
    df_display = df_results.copy()
    for col in ["Ingredient Cost", "Packaging Cost", "Total Cost", "Selling Price", "Profit"]:
        df_display[col] = df_display[col].apply(lambda x: f"KES {x:.2f}")
    df_display["Margin %"] = df_display["Margin %"].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Product": st.column_config.TextColumn("Product", width="medium"),
            "Channel": st.column_config.TextColumn("Channel", width="small"),
            "Weight (g)": st.column_config.NumberColumn("Weight", format="%.1f g"),
            "Ingredient Cost": st.column_config.TextColumn("Ingredient", width="small"),
            "Packaging Cost": st.column_config.TextColumn("Packaging", width="small"),
            "Total Cost": st.column_config.TextColumn("Total Cost", width="small"),
            "Selling Price": st.column_config.TextColumn("Selling Price", width="small"),
            "Profit": st.column_config.TextColumn("Profit", width="small"),
            "Margin %": st.column_config.TextColumn("Margin", width="small")
        }
    )
    
    # ========== PROFIT SUMMARY CARDS ==========
    st.markdown("---")
    st.markdown("### 📈 Profit Summary")
    
    # Use the numeric values from results (not formatted strings)
    margin_values = [r["Margin %"] for r in results]
    profit_values = [r["Profit"] for r in results]
    
    if margin_values:
        # Find highest margin product
        best_idx = margin_values.index(max(margin_values))
        best_product = results[best_idx]
        
        # Find lowest margin product (excluding zero)
        valid_margins = [(i, v) for i, v in enumerate(margin_values) if v > 0]
        if valid_margins:
            worst_idx = min(valid_margins, key=lambda x: x[1])[0]
            worst_product = results[worst_idx]
        else:
            worst_product = results[0]
        
        avg_margin = sum(margin_values) / len([v for v in margin_values if v > 0]) if [v for v in margin_values if v > 0] else 0
        
        # Find most profitable product
        most_profitable_idx = profit_values.index(max(profit_values))
        most_profitable = results[most_profitable_idx]
    else:
        best_product = results[0]
        worst_product = results[0]
        avg_margin = 0
        most_profitable = results[0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏆 Highest Margin", best_product["Product"], f"{max(margin_values):.1f}%" if margin_values else "N/A")
    
    with col2:
        st.metric("📉 Lowest Margin", worst_product["Product"], f"{min([v for v in margin_values if v > 0]):.1f}%" if [v for v in margin_values if v > 0] else "N/A")
    
    with col3:
        st.metric("📊 Average Margin", f"{avg_margin:.1f}%")
    
    with col4:
        st.metric("💰 Most Profit per Unit", most_profitable["Product"], f"KES {max(profit_values):.2f}")
    
    # ========== CHARTS ==========
    st.markdown("---")
    st.markdown("### 📊 Visual Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Profit margin bar chart
        chart_data = []
        for r in results:
            chart_data.append({
                "Product": r["Product"][:20],
                "Margin %": r["Margin %"]
            })
        
        df_chart = pd.DataFrame(chart_data)
        fig = px.bar(df_chart, x='Product', y='Margin %', 
                    title='Profit Margin by Product',
                    color='Margin %', color_continuous_scale='RdYlGn',
                    text='Margin %')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        # Profit per unit chart
        profit_data = []
        for r in results:
            profit_data.append({
                "Product": r["Product"][:20],
                "Profit (KES)": r["Profit"]
            })
        
        df_profit = pd.DataFrame(profit_data)
        fig = px.bar(df_profit, x='Product', y='Profit (KES)', 
                    title='Profit per Unit by Product',
                    color='Profit (KES)', color_continuous_scale='Greens',
                    text='Profit (KES)')
        fig.update_traces(texttemplate='KES %{text:.2f}', textposition='outside')
        fig.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig, width='stretch')
    
    # ========== COST BREAKDOWN ==========
    st.markdown("---")
    st.markdown("### 🔍 Cost Breakdown for Selected Product")
    
    selected_product = st.selectbox("Select a product to see detailed cost breakdown", [r["Product"] for r in results])
    product_detail = next((r for r in results if r["Product"] == selected_product), None)
    
    if product_detail:
        col1, col2 = st.columns(2)
        
        with col1:
            # Cost breakdown pie chart
            cost_data = pd.DataFrame({
                'Category': ['Ingredient Cost', 'Packaging Cost'],
                'Amount': [product_detail["Ingredient Cost"], product_detail["Packaging Cost"]]
            })
            fig = px.pie(cost_data, values='Amount', names='Category', 
                        title=f'Cost Breakdown for {selected_product}',
                        color_discrete_sequence=['#FF9800', '#2196F3'])
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            st.markdown(f"### 📊 {selected_product}")
            st.metric("💰 Selling Price", f"KES {product_detail['Selling Price']:.2f}")
            st.metric("🏭 Total Cost", f"KES {product_detail['Total Cost']:.2f}")
            st.metric("📈 Profit", f"KES {product_detail['Profit']:.2f}", delta=f"{product_detail['Margin %']:.1f}%")
            
            # Show profit recommendation
            margin_pct = product_detail["Margin %"]
            if margin_pct > 50:
                st.success(f"✅ Excellent margin! Keep this price point.")
            elif margin_pct > 30:
                st.info(f"📈 Good margin. Consider testing higher price.")
            elif margin_pct > 15:
                st.warning(f"⚠️ Low margin. Review costs or increase price.")
            else:
                st.error(f"❌ Very low margin! Consider discontinuing or raising price significantly.")
    
    # ========== WHAT-IF ANALYSIS ==========
    st.markdown("---")
    st.markdown("### 🔮 What-If Analysis")
    st.caption("Adjust costs or prices to see how profit changes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        test_product = st.selectbox("Select product for analysis", [r["Product"] for r in results], key="test_product")
        test_price = st.number_input("Test Selling Price (KES)", min_value=0.0, step=5.0, value=0.0, key="test_price")
    
    with col2:
        test_ingredient_cost = st.number_input("Test Ingredient Cost (KES per gram)", min_value=0.0, step=0.01, value=cost_per_gram, key="test_ingredient")
        test_packaging = st.number_input("Test Packaging Cost (KES)", min_value=0.0, step=1.0, value=0.0, key="test_packaging")
    
    if test_price > 0:
        product_data = next((r for r in results if r["Product"] == test_product), None)
        if product_data:
            # Calculate with new values
            weight = product_data["Weight (g)"]
            ingredient_cost_new = weight * test_ingredient_cost
            packaging_cost_new = test_packaging if test_packaging > 0 else product_data["Packaging Cost"]
            total_cost_new = ingredient_cost_new + packaging_cost_new
            profit_new = test_price - total_cost_new
            margin_new = (profit_new / test_price) * 100 if test_price > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("New Total Cost", f"KES {total_cost_new:.2f}")
            with col2:
                st.metric("New Profit", f"KES {profit_new:.2f}")
            with col3:
                st.metric("New Margin", f"{margin_new:.1f}%")
            
            if margin_new > 50:
                st.success("✅ This pricing strategy gives excellent margin!")
            elif margin_new > 30:
                st.info("📈 Good margin achievable with these numbers.")
            else:
                st.warning("⚠️ Margin is low. Consider reducing costs or increasing price.")

# ==================== TAB 12: BUSINESS HEALTH ====================
with tab12:
    st.markdown('<div class="section-header">🏥 Business Health Dashboard</div>', unsafe_allow_html=True)
    
    st.info("📊 **Business Health Analysis** - Instant insights about your business temperature and valuation")
    
    # ========== BUSINESS TEMPERATURE ==========
    st.markdown("---")
    st.markdown("### 🌡️ Business Temperature")
    
    # Calculate key metrics
    total_sales = kpis['total_sales']
    total_expenses = kpis['total_expenses']
    net_profit = kpis['net_profit']
    cash_balance = kpis['running_balance']
    total_funding = get_total_funding()
    
    # Calculate growth metrics
    if not sales_df.empty and len(sales_df) >= 7:
        last_7_days = sales_df.tail(7)['Total'].sum()
        previous_7_days = sales_df.head(7)['Total'].sum() if len(sales_df) > 14 else last_7_days
        sales_growth = ((last_7_days - previous_7_days) / previous_7_days * 100) if previous_7_days > 0 else 0
    else:
        sales_growth = 0
    
    # Calculate profit margin
    profit_margin = (net_profit / total_sales * 100) if total_sales > 0 else 0
    
    # Calculate burn rate
    if not expenses_df.empty:
        last_30_days = expenses_df[expenses_df['date'] >= datetime.now() - timedelta(days=30)]
        monthly_burn = last_30_days['amount'].sum() if len(last_30_days) > 0 else 0
    else:
        monthly_burn = 0
    
    # Calculate runway
    runway_months = cash_balance / monthly_burn if monthly_burn > 0 else 0
    
    # Customer count
    customer_count = sales_df['Name'].nunique() if not sales_df.empty else 0
    
    # Average order value
    avg_order = sales_df['Total'].mean() if not sales_df.empty else 0
    
    # Determine business temperature
    temperature_score = 0
    
    if profit_margin > 20:
        temperature_score += 30
    elif profit_margin > 10:
        temperature_score += 20
    elif profit_margin > 0:
        temperature_score += 10
    
    if sales_growth > 20:
        temperature_score += 30
    elif sales_growth > 10:
        temperature_score += 20
    elif sales_growth > 0:
        temperature_score += 10
    
    if runway_months > 12:
        temperature_score += 25
    elif runway_months > 6:
        temperature_score += 15
    elif runway_months > 3:
        temperature_score += 10
    
    if cash_balance > 100000:
        temperature_score += 15
    elif cash_balance > 50000:
        temperature_score += 10
    elif cash_balance > 10000:
        temperature_score += 5
    
    # Determine status
    if temperature_score >= 70:
        temperature_status = "🔥 HOT - Business is on fire!"
        temperature_color = "🟢"
        temperature_advice = "Excellent! Keep doing what you're doing. Consider expanding."
    elif temperature_score >= 50:
        temperature_status = "🌡️ WARM - Good, but room for improvement"
        temperature_color = "🟡"
        temperature_advice = "You're on the right track. Focus on increasing sales and managing costs."
    elif temperature_score >= 30:
        temperature_status = "❄️ COOL - Needs attention"
        temperature_color = "🟠"
        temperature_advice = "Review your expenses and look for ways to increase revenue."
    else:
        temperature_status = "🧊 COLD - Critical attention needed"
        temperature_color = "🔴"
        temperature_advice = "Urgent action required. Focus on cash flow and cost reduction."
    
    # Display temperature gauge
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=temperature_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"{temperature_color} Business Health Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkgreen" if temperature_score >= 70 else "orange" if temperature_score >= 40 else "red"},
                'steps': [
                    {'range': [0, 30], 'color': 'lightcoral'},
                    {'range': [30, 50], 'color': 'lightsalmon'},
                    {'range': [50, 70], 'color': 'lightyellow'},
                    {'range': [70, 100], 'color': 'lightgreen'}
                ]
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.markdown(f"## {temperature_color}")
        st.markdown(f"### {temperature_status}")
        st.metric("Health Score", f"{temperature_score:.0f}/100")
        st.caption(temperature_advice)
    
    # ========== KEY METRICS SUMMARY ==========
    st.markdown("---")
    st.markdown("### 📊 Key Business Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Total Sales", f"KES {total_sales:,.0f}")
    with col2:
        st.metric("📈 Profit Margin", f"{profit_margin:.1f}%")
    with col3:
        st.metric("📊 Sales Growth", f"{sales_growth:.1f}%" if sales_growth != 0 else "N/A")
    with col4:
        st.metric("🏃 Runway", f"{runway_months:.1f} months" if runway_months > 0 else "N/A")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💵 Cash Balance", f"KES {cash_balance:,.0f}")
    with col2:
        st.metric("🔥 Monthly Burn", f"KES {monthly_burn:,.0f}")
    with col3:
        st.metric("📦 Total Customers", customer_count)
    with col4:
        st.metric("💰 Avg Order Value", f"KES {avg_order:,.0f}")
    
    # ========== TRUE PROFITABILITY ANALYSIS ==========
    st.markdown("---")
    st.markdown("### 💡 True Profitability Analysis")
    st.info("🔍 **Separating Startup Costs from Operational Profitability**")
    
    # Calculate operational vs capital expenses
    capital_expenses = expenses_df[expenses_df['category'].str.contains('Equipment|Asset|Bottle|Label', case=False, na=False)]['amount'].sum() if not expenses_df.empty else 0
    operational_expenses = total_expenses - capital_expenses
    
    # Calculate operational profit
    operational_profit = total_sales - operational_expenses
    operational_margin = (operational_profit / total_sales * 100) if total_sales > 0 else 0
    
    # Show comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📦 Capital Expenses (One-time)")
        st.metric("Equipment & Setup", f"KES {capital_expenses:,.0f}")
        st.caption("Bottles, labels, equipment - one-time investments")
        
        st.markdown("#### 💰 Total Investment")
        st.metric("Startup Capital", f"KES {total_funding:,.0f}")
        st.metric("Capital Expenses", f"KES {capital_expenses:,.0f}")
        remaining_capital = total_funding - capital_expenses
        st.metric("Remaining Capital", f"KES {remaining_capital:,.0f}")
    
    with col2:
        st.markdown("#### 📈 Operational Profitability")
        st.metric("Sales Revenue", f"KES {total_sales:,.0f}")
        st.metric("Operational Expenses", f"KES {operational_expenses:,.0f}")
        
        profit_color = "normal" if operational_profit > 0 else "inverse"
        st.metric("✅ Operational Profit", f"KES {operational_profit:,.0f}", delta_color=profit_color)
        st.metric("📊 Operational Margin", f"{operational_margin:.1f}%")
        
        if operational_profit > 0:
            st.success(f"✅ Your day-to-day operations are PROFITABLE! You make KES {operational_margin:.0f} on every KES 100 sold")
        else:
            st.warning(f"⚠️ Operations are losing money. Need to reduce daily costs by KES {abs(operational_profit):,.0f}")
    
    # ========== BUSINESS VALUATION ==========
    st.markdown("---")
    st.markdown("### 💰 Business Valuation")
    
    # Valuation calculations
    annual_revenue = total_sales * 12 if total_sales > 0 else 0
    revenue_multiple = 5.0 if sales_growth > 30 else 4.0 if sales_growth > 20 else 3.0 if sales_growth > 10 else 2.5
    valuation_revenue = annual_revenue * revenue_multiple
    
    annual_profit = max(0, operational_profit * 12)
    profit_multiple = 8.0 if operational_margin > 20 else 5.0
    valuation_profit = annual_profit * profit_multiple
    
    customer_value = customer_count * 5000
    asset_value = total_funding + total_sales - total_expenses
    
    valuation_final = (valuation_revenue * 0.4 + valuation_profit * 0.4 + asset_value * 0.1 + customer_value * 0.1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Revenue Multiple ({revenue_multiple}x):** KES {valuation_revenue:,.0f}")
        st.write(f"**Profit Multiple ({profit_multiple}x):** KES {valuation_profit:,.0f}")
        st.write(f"**Customer-based:** KES {customer_value:,.0f}")
    
    with col2:
        st.markdown(f"## 🏆 KES {valuation_final:,.0f}")
        st.caption(f"Based on {customer_count} customers and {sales_growth:.1f}% growth rate")
    
    # ========== RECOMMENDATIONS ==========
    st.markdown("---")
    st.markdown("### 🎯 Recommendations to Improve Profitability")
    
    recommendations = []
    
    if operational_margin < 20 and operational_margin > 0:
        recommendations.append("💰 **Increase prices by 10-15%** - your customers will likely accept it")
    elif operational_margin < 0:
        recommendations.append("🚨 **Urgent: Increase prices OR reduce daily operating costs**")
    
    if operational_expenses > total_sales * 0.7:
        recommendations.append("📊 **Review your top expense categories** - look for unnecessary subscriptions or services")
    
    if customer_count < 20:
        recommendations.append("👥 **Grow your customer base** - implement a referral program")
    
    recommendations.append("📈 **Focus on repeat customers** - they spend 3x more than new customers")
    recommendations.append("🏆 **Promote your best-selling products** - they drive most of your revenue")
    
    for i, rec in enumerate(recommendations[:5], 1):
        st.write(f"{i}. {rec}")
    
    # ========== PROFITABILITY SCENARIOS ==========
    st.markdown("---")
    st.markdown("### 🔮 What-If Scenarios")
    
    col1, col2 = st.columns(2)
    
    with col1:
        price_increase = st.slider("Price Increase %", 0, 50, 10, key="price_scenario_health")
        new_revenue = total_sales * (1 + price_increase / 100)
        new_profit = new_revenue - operational_expenses
        new_margin = (new_profit / new_revenue * 100) if new_revenue > 0 else 0
        
        st.write(f"**With {price_increase}% price increase:**")
        st.write(f"• New Revenue: KES {new_revenue:,.0f}")
        st.write(f"• New Profit: KES {new_profit:,.0f}")
        st.write(f"• New Margin: {new_margin:.1f}%")
    
    with col2:
        cost_reduction = st.slider("Cost Reduction %", 0, 50, 15, key="cost_scenario_health")
        new_expenses = operational_expenses * (1 - cost_reduction / 100)
        new_profit2 = total_sales - new_expenses
        new_margin2 = (new_profit2 / total_sales * 100) if total_sales > 0 else 0
        
        st.write(f"**With {cost_reduction}% cost reduction:**")
        st.write(f"• New Expenses: KES {new_expenses:,.0f}")
        st.write(f"• New Profit: KES {new_profit2:,.0f}")
        st.write(f"• New Margin: {new_margin2:.1f}%")

    # ========== TRUE BUSINESS PERFORMANCE (From April 1st) ==========
st.markdown("---")
st.markdown("### 📅 Business Performance Since April 1st")
st.info("🔍 **This analysis excludes all pre-launch/startup costs and only shows your actual business operations since April 1, 2026**")

# Filter data from April 1st
start_date_filter = date(2026, 4, 1)
current_date_filter = datetime.now().date()

# Filter sales from April 1st
sales_from_april = sales_df[sales_df['Date'] >= pd.Timestamp(start_date_filter)] if not sales_df.empty else pd.DataFrame()
expenses_from_april = expenses_df[expenses_df['date'] >= pd.Timestamp(start_date_filter)] if not expenses_df.empty else pd.DataFrame()

# Calculate metrics from April 1st
total_sales_april = sales_from_april['Total'].sum() if not sales_from_april.empty else 0
total_expenses_april = expenses_from_april['amount'].sum() if not expenses_from_april.empty else 0

# Separate operational vs capital from April
capital_keywords = [
    'kebs', 'standardization', 'trademark', 'permit', 'registration', 
    'grinder', 'mixer', 'machine', 'equipment', 'design', 'posters', 'envelope',
    'application', 'certificate', 'deposit', 'rent', 'permit'
]

operational_keywords = [
    'salaries', 'supplies', 'transport', 'delivery', 'utilities', 'credit', 
    'water', 'food', 'ingredients', 'salt', 'pepper', 'cayenne', 'paprika',
    'onion', 'garlic', 'bottle', 'label', 'packaging', 'labelling', 'salary'
]

if not expenses_from_april.empty:
    expenses_from_april['is_capital'] = expenses_from_april['category'].str.lower().str.contains('|'.join(capital_keywords), na=False)
    expenses_from_april['is_capital'] = expenses_from_april['is_capital'] | expenses_from_april['description'].str.lower().str.contains('|'.join(capital_keywords), na=False)
    
    capital_from_april = expenses_from_april[expenses_from_april['is_capital']]['amount'].sum()
    operational_from_april = expenses_from_april[~expenses_from_april['is_capital']]['amount'].sum()
else:
    capital_from_april = 0
    operational_from_april = 0

# Calculate operational profit
operational_profit_april = total_sales_april - operational_from_april
operational_margin_april = (operational_profit_april / total_sales_april * 100) if total_sales_april > 0 else 0

# Display metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📅 Period", "Apr 1 - Present")
    st.caption(f"{start_date_filter.strftime('%b %d')} to {current_date_filter.strftime('%b %d')}")
with col2:
    st.metric("💰 Total Sales", f"KES {total_sales_april:,.0f}")
with col3:
    st.metric("💵 Operational Expenses", f"KES {operational_from_april:,.0f}")
with col4:
    profit_color = "normal" if operational_profit_april > 0 else "inverse"
    st.metric("✅ Operational Profit", f"KES {operational_profit_april:,.0f}", delta_color=profit_color)

# Key metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📈 Operational Margin", f"{operational_margin_april:.1f}%")
with col2:
    # Average daily sales
    days_active = (datetime.now() - datetime(2026, 4, 1)).days
    avg_daily_sales = total_sales_april / days_active if days_active > 0 else 0
    st.metric("📊 Avg Daily Sales", f"KES {avg_daily_sales:,.0f}")
with col3:
    # Customer count since April
    customer_count_april = sales_from_april['Name'].nunique() if not sales_from_april.empty else 0
    st.metric("👥 Total Customers", customer_count_april)
with col4:
    # Average order value
    avg_order_april = total_sales_april / len(sales_from_april) if not sales_from_april.empty else 0
    st.metric("💰 Avg Order Value", f"KES {avg_order_april:,.0f}")

# Business Health Status
st.markdown("---")
st.markdown("### 🩺 Business Health Status (Since April 1st)")

if operational_profit_april > 0:
    st.success(f"✅ **HEALTHY!** Your business is operationally profitable, making KES {operational_margin_april:.0f} profit on every KES 100 sold.")
    
    # Projection
    monthly_profit = operational_profit_april / (days_active / 30)
    st.info(f"📈 **Projection:** At current rate, you're making ~KES {monthly_profit:,.0f} profit per month")
    
elif operational_profit_april < 0:
    st.warning(f"⚠️ **NEEDS IMPROVEMENT:** Your operations are losing KES {abs(operational_profit_april):,.0f}. Need to increase sales or reduce costs.")
    
    # Break-even analysis
    needed_sales = abs(operational_profit_april) + total_sales_april
    st.info(f"🎯 **Break-even target:** Need KES {needed_sales:,.0f} in sales to break even")
else:
    st.info("📊 **BREAKING EVEN:** Your sales exactly cover operational costs.")

# One-time costs (pre-April)
st.markdown("---")
st.markdown("### 🏭 One-Time Startup Costs (Before April 1st)")

# Filter expenses before April
expenses_before_april = expenses_df[expenses_df['date'] < pd.Timestamp(start_date_filter)] if not expenses_df.empty else pd.DataFrame()
capital_before = expenses_before_april['amount'].sum() if not expenses_before_april.empty else 0

col1, col2 = st.columns(2)
with col1:
    st.metric("💰 Total Investment to Date", f"KES {total_funding:,.0f}")
    st.caption("From Grandma + other sources")
with col2:
    st.metric("🏭 Startup Costs (Pre-April)", f"KES {abs(capital_before):,.0f}")
    st.caption("KEBS, Permits, Equipment, Trademark")

# Show breakdown of pre-April costs
if not expenses_before_april.empty:
    with st.expander("View One-Time Startup Costs"):
        for _, row in expenses_before_april.iterrows():
            st.write(f"• {row['date']}: {row['description'][:60]} - KES {row['amount']:,.0f}")

# Remaining capital
remaining_capital = total_funding - abs(capital_before) - operational_from_april
col1, col2 = st.columns(2)
with col1:
    st.metric("💵 Remaining Capital", f"KES {remaining_capital:,.0f}")
    if remaining_capital > 0:
        st.caption(f"~{remaining_capital / avg_daily_sales:.0f} days of runway at current sales")
with col2:
    # ROI calculation based on operational profit only
    if total_funding > 0:
        roi_operational = (operational_profit_april / total_funding) * 100
        st.metric("📈 ROI (Operational)", f"{roi_operational:.1f}%")
        st.caption("Based on operational profit vs total investment")

# Actionable insights
st.markdown("---")
st.markdown("### 🎯 Actionable Insights")

insights = []

if operational_profit_april < 0:
    insights.append(f"🚨 **Reduce operational costs by KES {abs(operational_profit_april):,.0f}** to break even")
    
if avg_order_april < 500:
    insights.append("💰 **Increase average order value** - Offer bundle deals (e.g., 3 bottles for KES 400)")

if customer_count_april > 0:
    avg_customer_value = total_sales_april / customer_count_april
    insights.append(f"👥 **Customer lifetime value: KES {avg_customer_value:,.0f}** - Focus on repeat purchases")

# Sales per day analysis
if len(sales_from_april) > 0:
    busiest_days = sales_from_april.groupby(sales_from_april['Date'].dt.day_name())['Total'].sum()
    if not busiest_days.empty:
        best_day = busiest_days.idxmax()
        insights.append(f"📅 **Best sales day: {best_day}** - Run promotions on slow days")

for i, insight in enumerate(insights[:4], 1):
    st.write(f"{i}. {insight}")

# Summary
st.markdown("---")
st.markdown("### 📋 Executive Summary")

summary = f"""
**Since April 1st ({days_active} days):**

• **Total Sales:** KES {total_sales_april:,.0f}
• **Operational Expenses:** KES {operational_from_april:,.0f}
• **Operational Profit:** KES {operational_profit_april:,.0f} ({operational_margin_april:.1f}% margin)
• **Customers Acquired:** {customer_count_april}
• **Average Daily Sales:** KES {avg_daily_sales:,.0f}

**Startup Investment:** KES {total_funding:,.0f} (Grandma)
**One-time Setup Costs:** KES {abs(capital_before):,.0f}
**Remaining Capital:** KES {remaining_capital:,.0f}

**Verdict:** {'Your business is OPERATIONALLY PROFITABLE! The negative numbers come from one-time startup costs.' if operational_profit_april > 0 else 'Your business is still in investment phase. Focus on increasing sales.'}
"""

st.info(summary)

# ========== DETAILED EXPENSE ANALYSIS & OPTIMIZATION ==========
st.markdown("---")
st.markdown("### 💰 Where Your Money Is Going")
st.info("🔍 **Deep dive into your spending patterns - see exactly what you can change**")

if not expenses_df.empty:
    
    # Create proper categories
    def categorize_expense(row):
        desc = str(row['description']).lower()
        cat = str(row['category']).lower() if pd.notna(row['category']) else ""
        
        # Salary & Personal
        if 'salary' in cat or 'salaries' in cat or 'food' in desc or 'personal' in desc or 'shopping' in desc:
            return '💰 Salaries & Personal'
        # Ingredients & Supplies
        elif 'supplies' in cat or 'ingredient' in desc or 'salt' in desc or 'pepper' in desc or 'paprika' in desc:
            return '📦 Ingredients & Supplies'
        # Transport
        elif 'transport' in cat or 'delivery' in desc or 'transport' in desc:
            return '🚚 Transport & Delivery'
        # Equipment (One-time)
        elif 'equipment' in cat or 'grinder' in desc or 'mixer' in desc or 'machine' in desc or 'cooker' in desc:
            return '🔧 Equipment (One-time)'
        # KEBS & Permits (One-time)
        elif 'kebs' in desc or 'permit' in cat or 'standardization' in desc or 'trademark' in desc or 'registration' in desc:
            return '📋 Permits & Licenses (One-time)'
        # Rent & Utilities
        elif 'rent' in cat or 'utilities' in cat or 'water' in desc or 'credit' in desc:
            return '🏠 Rent & Utilities'
        # Packaging
        elif 'bottle' in desc or 'label' in desc or 'packaging' in desc:
            return '📦 Packaging'
        # Marketing
        elif 'marketing' in cat or 'posters' in desc:
            return '📢 Marketing'
        # Refunds
        elif 'refund' in cat:
            return '💰 Refunds (Money Back)'
        else:
            return '📌 Other'
    
    expenses_df['analysis_category'] = expenses_df.apply(categorize_expense, axis=1)
    
    # Group by category
    category_totals = expenses_df.groupby('analysis_category')['amount'].sum().reset_index()
    category_totals = category_totals.sort_values('amount', ascending=False)
    
    # Display pie chart
    fig = px.pie(category_totals, values='amount', names='analysis_category', 
                title='Where Every Shilling Goes',
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, width='stretch')
    
    # Display table with details
    st.markdown("### 📋 Detailed Spending Breakdown")
    
    for _, row in category_totals.iterrows():
        amount = row['amount']
        category = row['analysis_category']
        percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
        
        # Color code based on category type
        if 'One-time' in category:
            color = "🟣"
        elif 'Salaries' in category:
            color = "🔴"
        elif 'Ingredients' in category:
            color = "🟢"
        elif 'Transport' in category:
            color = "🟠"
        else:
            color = "🔵"
        
        st.write(f"{color} **{category}:** KES {amount:,.0f} ({percentage:.1f}%)")
        
        # Show top expenses in this category
        category_expenses = expenses_df[expenses_df['analysis_category'] == category].nlargest(3, 'amount')
        for _, exp in category_expenses.iterrows():
            st.write(f"   └─ {exp['date']}: {exp['description'][:50]} - KES {exp['amount']:,.0f}")
        st.write("")
    
    # ========== SALARY SPECIFIC ANALYSIS ==========
    st.markdown("---")
    st.markdown("### 💼 Salary & Personal Spending Analysis")
    st.info("🔍 **This is where you can optimize your spending**")
    
    # Filter salary/personal expenses
    salary_expenses = expenses_df[expenses_df['analysis_category'] == '💰 Salaries & Personal']
    
    if not salary_expenses.empty:
        total_salary = salary_expenses['amount'].sum()
        salary_percentage = (total_salary / total_expenses * 100) if total_expenses > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Total Salary/Personal", f"KES {total_salary:,.0f}")
        with col2:
            st.metric("📊 % of Total Expenses", f"{salary_percentage:.1f}%")
        with col3:
            # Average monthly salary
            months_active = (datetime.now() - sales_df['Date'].min()).days / 30 if not sales_df.empty else 1
            monthly_salary = total_salary / max(months_active, 1)
            st.metric("📅 Avg Monthly Salary", f"KES {monthly_salary:,.0f}")
        
        # Show salary breakdown
        st.write("**Salary & Personal Expenses Breakdown:**")
        salary_by_date = salary_expenses.groupby('date')['amount'].sum().reset_index()
        salary_by_date = salary_by_date.sort_values('date')
        
        fig = px.bar(salary_by_date, x='date', y='amount', 
                    title='Salary & Personal Spending Over Time',
                    color='amount', color_continuous_scale='Reds',
                    text='amount')
        fig.update_traces(texttemplate='KES %{text:,.0f}', textposition='outside')
        st.plotly_chart(fig, width='stretch')
        
        # List all salary expenses
        with st.expander("View All Salary/Personal Expenses"):
            for _, row in salary_expenses.sort_values('date', ascending=False).iterrows():
                st.write(f"• {row['date']}: {row['description'][:60]} - KES {row['amount']:,.0f}")
    
    # ========== OPTIMIZATION RECOMMENDATIONS ==========
    st.markdown("---")
    st.markdown("### 🎯 Optimization Recommendations")
    
    recommendations = []
    
    # Analyze salary vs revenue
    if not salary_expenses.empty and total_sales > 0:
        salary_to_revenue = (total_salary / total_sales * 100) if total_sales > 0 else 0
        if salary_to_revenue > 30:
            recommendations.append(f"⚠️ **Salary/Revenue ratio is {salary_to_revenue:.0f}%** - Consider performance-based pay or reducing personal drawings")
        elif salary_to_revenue > 20:
            recommendations.append(f"📊 **Salary/Revenue ratio is {salary_to_revenue:.0f}%** - Monitor this as you grow")
        else:
            recommendations.append(f"✅ **Salary/Revenue ratio is {salary_to_revenue:.0f}%** - Good efficiency!")
    
    # Analyze transport costs
    transport_expenses = expenses_df[expenses_df['analysis_category'] == '🚚 Transport & Delivery']['amount'].sum()
    if transport_expenses > 0:
        transport_percentage = (transport_expenses / total_expenses * 100) if total_expenses > 0 else 0
        if transport_percentage > 15:
            recommendations.append(f"🚚 **Transport costs are {transport_percentage:.0f}% of expenses** - Consider batching deliveries or negotiating better rates")
    
    # Analyze ingredient costs
    ingredient_expenses = expenses_df[expenses_df['analysis_category'] == '📦 Ingredients & Supplies']['amount'].sum()
    if ingredient_expenses > 0 and total_sales > 0:
        ingredient_percentage = (ingredient_expenses / total_sales * 100) if total_sales > 0 else 0
        if ingredient_percentage > 40:
            recommendations.append(f"📦 **Ingredients cost {ingredient_percentage:.0f}% of sales** - Consider bulk purchasing or finding cheaper suppliers")
        elif ingredient_percentage > 30:
            recommendations.append(f"📦 **Ingredients cost {ingredient_percentage:.0f}% of sales** - Room for improvement")
    
    # General recommendations
    if total_expenses > total_sales and total_sales > 0:
        loss = total_expenses - total_sales
        recommendations.append(f"🚨 **You're spending KES {loss:,.0f} more than you earn** - Focus on increasing sales or reducing non-essential expenses")
    
    # One-time vs operational ratio
    one_time = expenses_df[expenses_df['analysis_category'].str.contains('One-time', na=False)]['amount'].sum()
    operational = total_expenses - one_time
    if one_time > operational:
        recommendations.append(f"🏭 **Most expenses are one-time startup costs ({one_time/total_expenses*100:.0f}%)** - Your actual monthly operational costs are lower")
    
    if not recommendations:
        recommendations.append("✅ Your spending patterns look healthy! Focus on increasing sales to improve profitability.")
    
    for i, rec in enumerate(recommendations, 1):
        if "⚠️" in rec or "🚨" in rec:
            st.warning(rec)
        elif "✅" in rec:
            st.success(rec)
        else:
            st.info(rec)
    
    # ========== MONTHLY TREND ==========
    st.markdown("---")
    st.markdown("### 📈 Monthly Spending Trend")
    
    expenses_df['month'] = expenses_df['date'].dt.strftime('%Y-%m')
    monthly_trend = expenses_df.groupby('month')['amount'].sum().reset_index()
    monthly_trend = monthly_trend.sort_values('month')
    
    fig = px.line(monthly_trend, x='month', y='amount', 
                 title='Monthly Spending Trend',
                 markers=True, line_shape='spline')
    fig.update_traces(line=dict(color='#FF4B4B', width=3))
    fig.update_layout(xaxis_title='Month', yaxis_title='Total Expenses (KES)')
    st.plotly_chart(fig, width='stretch')
    
    # Identify months with unusual spending
    if len(monthly_trend) > 1:
        avg_spending = monthly_trend['amount'].mean()
        high_spending_months = monthly_trend[monthly_trend['amount'] > avg_spending * 1.3]
        if not high_spending_months.empty:
            st.warning(f"⚠️ **High spending detected in:** {', '.join(high_spending_months['month'].tolist())}")
            st.caption("Review these months for one-time purchases or unusual expenses")
    
else:
    st.info("Add expense data to see detailed analysis")

# ==================== INVOICE SYSTEM TAB ====================
with tab13:  
    st.markdown('<div class="section-header">📄 Invoice Management</div>', unsafe_allow_html=True)
    
    st.info("💡 **Create professional invoices for bulk orders, hotels, and credit customers**")
    
    # ========== INVOICE SETTINGS ==========
    # Define product list
    product_list = [
        "SpiseUp Spicy Salt Sachet (5 KES)",
        "SpiseUp Spicy Salt Sachet (10 KES)",
        "SpiseUp Spicy Salt Sachet (20 KES)",
        "SpiseUp Spicy Salt Sachet (30 KES)",
        "SpiseUp Spicy Salt Sachet (40 KES)",
        "SpiseUp Spicy Salt Bottle (100g) - 150 KES",
        "SpiseUp Spicy Salt Refill (100g) - 120 KES",
        "SpiseUp Hot Sauce - 200 KES"
    ]
    
    # ========== CREATE NEW INVOICE ==========
    with st.expander("➕ Create New Invoice", expanded=True):
        
        col1, col2 = st.columns(2)
        
        with col1:
            invoice_number = st.text_input("Invoice Number", value=f"INV-{datetime.now().strftime('%Y%m')}-{len(st.session_state.get('invoices', [])) + 1:03d}")
            customer_name = st.text_input("Customer Name *", placeholder="e.g., Hotel Sakina")
            customer_phone = st.text_input("Customer Phone", placeholder="e.g., 0712345678")
        
        with col2:
            invoice_date = st.date_input("Invoice Date", value=date.today())
            due_date = st.date_input("Due Date", value=date.today() + timedelta(days=30))
            payment_terms = st.selectbox("Payment Terms", ["Due on Receipt", "Net 15", "Net 30", "Net 60"])
        
        st.markdown("#### 📦 Items")
        
        # Dynamic item rows
        items = []
        cols = st.columns([3, 1, 1, 1, 1])
        cols[0].write("**Product**")
        cols[1].write("**Qty**")
        cols[2].write("**Price**")
        cols[3].write("**Total**")
        cols[4].write("")
        
        for i in range(5):
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            with col1:
                product = st.selectbox("Product", product_list, key=f"inv_prod_{i}", label_visibility="collapsed")
            with col2:
                qty = st.number_input("Qty", min_value=0, step=1, value=0, key=f"inv_qty_{i}", label_visibility="collapsed")
            with col3:
                # Extract price from product name or allow manual entry
                if "5 KES" in product:
                    default_price = 5
                elif "10 KES" in product:
                    default_price = 10
                elif "20 KES" in product:
                    default_price = 20
                elif "30 KES" in product:
                    default_price = 30
                elif "40 KES" in product:
                    default_price = 40
                elif "150 KES" in product:
                    default_price = 150
                elif "120 KES" in product:
                    default_price = 120
                elif "200 KES" in product:
                    default_price = 200
                else:
                    default_price = 0
                price = st.number_input("Price", min_value=0, step=10, value=default_price, key=f"inv_price_{i}", label_visibility="collapsed")
            with col4:
                total = qty * price
                st.write(f"KES {total:,.0f}")
            with col5:
                if qty > 0:
                    st.write("📦")
            
            if qty > 0:
                items.append({"product": product, "qty": qty, "price": price, "total": total})
        
        if items:
            subtotal = sum(i['total'] for i in items)
            vat = subtotal * 0.16  # 16% VAT
            grand_total = subtotal + vat
            
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 1, 1])
            with col2:
                st.write(f"**Subtotal:** KES {subtotal:,.0f}")
                st.write(f"**VAT (16%):** KES {vat:,.0f}")
                st.write(f"**Total Due:** KES {grand_total:,.0f}")
            
            notes = st.text_area("Invoice Notes", placeholder="Payment instructions, delivery details, thank you message...")
            
            if st.button("💾 Create Invoice", type="primary", use_container_width=True):
                if not customer_name:
                    st.error("Please enter customer name!")
                else:
                    # Save to session state (or database)
                    if 'invoices' not in st.session_state:
                        st.session_state.invoices = []
                    
                    new_invoice = {
                        "invoice_number": invoice_number,
                        "customer_name": customer_name,
                        "customer_phone": customer_phone,
                        "invoice_date": str(invoice_date),
                        "due_date": str(due_date),
                        "payment_terms": payment_terms,
                        "items": items,
                        "subtotal": subtotal,
                        "vat": vat,
                        "total": grand_total,
                        "notes": notes,
                        "status": "Pending",
                        "created_at": str(datetime.now())
                    }
                    
                    st.session_state.invoices.append(new_invoice)
                    st.success(f"✅ Invoice {invoice_number} created for {customer_name}!")
                    st.info(f"💰 Total Amount Due: KES {grand_total:,.0f}")
                    st.balloons()
    
    # ========== VIEW INVOICES ==========
    st.markdown("---")
    st.markdown("### 📋 Invoice History")
    
    if 'invoices' in st.session_state and st.session_state.invoices:
        # Summary metrics
        total_outstanding = sum(inv['total'] for inv in st.session_state.invoices if inv['status'] == 'Pending')
        total_paid = sum(inv['total'] for inv in st.session_state.invoices if inv['status'] == 'Paid')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Invoices", len(st.session_state.invoices))
        with col2:
            st.metric("💰 Outstanding", f"KES {total_outstanding:,.0f}")
        with col3:
            st.metric("✅ Paid", f"KES {total_paid:,.0f}")
        
        # Display invoices
        for idx, inv in enumerate(st.session_state.invoices):
            with st.expander(f"{inv['invoice_number']} - {inv['customer_name']} - {inv['status']} - KES {inv['total']:,.0f}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Date:** {inv['invoice_date']}")
                    st.write(f"**Due Date:** {inv['due_date']}")
                    st.write(f"**Payment Terms:** {inv['payment_terms']}")
                with col2:
                    st.write(f"**Status:** {inv['status']}")
                    if inv['status'] == 'Pending':
                        days_overdue = (datetime.now() - datetime.strptime(inv['due_date'], '%Y-%m-%d')).days
                        if days_overdue > 0:
                            st.warning(f"⚠️ {days_overdue} days overdue")
                
                st.write("**Items:**")
                for item in inv['items']:
                    st.write(f"• {item['product']}: {item['qty']} x KES {item['price']} = KES {item['total']:,.0f}")
                
                st.write(f"**Total:** KES {inv['total']:,.0f}")
                
                if inv['status'] == 'Pending':
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Mark as Paid", key=f"pay_{idx}"):
                            st.session_state.invoices[idx]['status'] = 'Paid'
                            st.success(f"✅ Invoice {inv['invoice_number']} marked as paid!")
                            st.rerun()
                    with col2:
                        if st.button(f"Delete", key=f"del_{idx}"):
                            st.session_state.invoices.pop(idx)
                            st.rerun()
                
                if inv['notes']:
                    st.write(f"**Notes:** {inv['notes']}")
    else:
        st.info("No invoices created yet. Create your first invoice above!")
    
    # ========== QUICK INVOICE TEMPLATES ==========
    st.markdown("---")
    st.markdown("### 📝 Quick Invoice Templates")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏨 Hotel Starter Pack (5 Bottles)", use_container_width=True):
            # Pre-fill form with hotel pack
            st.session_state.quick_invoice = {
                "items": [{"product": "SpiseUp Spicy Salt Bottle (100g) - 150 KES", "qty": 5, "price": 150, "total": 750}],
                "subtotal": 750,
                "vat": 120,
                "total": 870
            }
            st.success("Hotel Starter Pack loaded! Fill in customer details above.")
    
    with col2:
        if st.button("🏪 Mama Mboga Starter Pack (50 Sachets)", use_container_width=True):
            st.session_state.quick_invoice = {
                "items": [{"product": "SpiseUp Spicy Salt Sachet (5 KES)", "qty": 50, "price": 5, "total": 250}],
                "subtotal": 250,
                "vat": 40,
                "total": 290
            }
            st.success("Mama Mboga Pack loaded! Fill in customer details above.")          

# ==================== FREE ITEMS / GIVEAWAYS TAB ====================
with tab14:  # Add to your tabs list
    st.markdown('<div class="section-header">🎁 Free Items & Giveaways</div>', unsafe_allow_html=True)
    
    st.info("📌 **Track free samples and giveaways** - This helps you know your true inventory usage and marketing costs")
    
    # ========== RECORD GIVEAWAY ==========
    with st.expander("➕ Record Giveaway / Free Item", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            giveaway_date = st.date_input("Date", value=date.today(), key="giveaway_date")
            product_type = st.selectbox(
                "Product", 
                ["5 KES Sachet", "10 KES Sachet", "20 KES Sachet", "30 KES Sachet", "40 KES Sachet", 
                 "100g Bottle", "100g Refill", "Hot Sauce"],
                key="giveaway_product"
            )
            quantity = st.number_input("Quantity", min_value=1, step=1, value=1, key="giveaway_qty")
        
        with col2:
            reason = st.selectbox(
                "Reason for Giveaway",
                ["Sample - New Customer", "Sample - Existing Customer", "Promotion", 
                 "Damaged Product", "Customer Appreciation", "Testing/Feedback", "Bulk Sample"],
                key="giveaway_reason"
            )
            customer_name = st.text_input("Customer Name (optional)", placeholder="Who received it?", key="giveaway_customer")
            notes = st.text_area("Notes", placeholder="Any additional details...", key="giveaway_notes")
        
        # Calculate value
        product_prices = {
            "5 KES Sachet": 5,
            "10 KES Sachet": 10,
            "20 KES Sachet": 20,
            "30 KES Sachet": 30,
            "40 KES Sachet": 40,
            "100g Bottle": 150,
            "100g Refill": 120,
            "Hot Sauce": 200
        }
        unit_price = product_prices.get(product_type, 0)
        total_value = quantity * unit_price
        
        st.info(f"💰 Estimated value of giveaway: KES {total_value:,.0f}")
        
        if st.button("💾 Record Giveaway", type="primary", use_container_width=True):
            giveaway_data = {
                "giveaway_date": str(giveaway_date),
                "customer_name": customer_name if customer_name else None,
                "product_type": product_type,
                "quantity": quantity,
                "reason": reason,
                "unit_cost": unit_price,
                "total_value": total_value,
                "notes": notes
            }
            
            result = save_free_item(giveaway_data)
            if result:
                st.success(f"✅ Recorded {quantity} x {product_type} given away for: {reason}")
                st.caption(f"💡 This helps track your true inventory usage - {total_value} KES worth of product")
                st.rerun()
    
    # ========== GIVEAWAY SUMMARY ==========
    st.markdown("---")
    st.markdown("### 📊 Giveaway Summary")
    
    free_items = get_free_items()
    
    if free_items:
        df_free = pd.DataFrame(free_items)
        df_free['giveaway_date'] = pd.to_datetime(df_free['giveaway_date']).dt.strftime('%Y-%m-%d')
        df_free['total_value'] = df_free['total_value'].apply(lambda x: f"KES {x:,.0f}")
        
        # Summary metrics
        total_free_quantity = df_free['quantity'].sum() if 'quantity' in df_free.columns else 0
        total_free_value = sum([f['total_value'] for f in free_items]) if free_items else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🎁 Total Items Given", f"{total_free_quantity:,}")
        with col2:
            st.metric("💰 Total Value Given", f"KES {total_free_value:,.0f}")
        with col3:
            reasons_count = df_free['reason'].nunique() if 'reason' in df_free.columns else 0
            st.metric("📋 Types of Giveaways", reasons_count)
        with col4:
            if total_sales > 0:
                giveaway_percentage = (total_free_value / total_sales * 100)
                st.metric("📊 % of Sales Value", f"{giveaway_percentage:.1f}%")
        
        # Giveaway by reason chart
        if 'reason' in df_free.columns:
            reason_summary = df_free.groupby('reason')['quantity'].sum().reset_index()
            fig = px.pie(reason_summary, values='quantity', names='reason',
                        title='Giveaways by Reason',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, width='stretch')
        
        # Giveaway by product chart
        if 'product_type' in df_free.columns:
            product_summary = df_free.groupby('product_type')['quantity'].sum().reset_index()
            fig = px.bar(product_summary, x='product_type', y='quantity',
                        title='Giveaways by Product',
                        color='quantity', color_continuous_scale='Oranges',
                        text='quantity')
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, width='stretch')
        
        # Recent giveaways table
        st.markdown("### 📋 Recent Giveaways")
        st.dataframe(
            df_free[['giveaway_date', 'product_type', 'quantity', 'reason', 'customer_name', 'notes']],
            use_container_width=True,
            hide_index=True
        )
        
        # Insight
        st.markdown("---")
        st.markdown("### 💡 Marketing Insight")
        
        sample_count = df_free[df_free['reason'].str.contains('Sample', case=False)]['quantity'].sum() if 'reason' in df_free.columns else 0
        if sample_count > 0:
            st.info(f"📊 You've given away {sample_count} samples. Track which customers buy after receiving samples!")
        else:
            st.info("📊 Start giving samples to new customers - it's a great way to acquire customers!")
        
        # Update inventory button
        st.warning("⚠️ Remember: These items have been removed from your inventory. Make sure your stock levels reflect these giveaways.")
        
    else:
        st.info("No giveaways recorded yet. Use the form above to track free samples and promotions.")

# Footer
st.markdown("---")
st.caption(f"🌶️ SpiseUp Finance Tracker • Data range: {start_date} to {end_date} • {len(sales_df)} sales • {len(expenses_df)} expenses")