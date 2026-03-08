import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import numpy as np
from dateutil.relativedelta import relativedelta



# Supabase functions
from supabase_client import (
    save_sale,
    save_expense,
    save_distribution,
    get_sales_summary,
    get_expenses_summary,
    get_sales_people,
    save_sales_person,
    get_distribution_data
)

# DEBUG MODE - Set to True for testing
DEBUG_MODE = True  # Change to False when done testing

def test_distribution_connection():
    """Test if distribution table works"""
    try:
        # Test with minimal data
        test_record = {
            "id": str(uuid.uuid4()),
            "date": str(date.today()),
            "sales_person_id": "00000000-0000-0000-0000-000000000000",  # Dummy UUID
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
        
        if DEBUG_MODE:
            st.sidebar.write("🔍 DEBUG: Testing distribution connection...")
            st.sidebar.write("Test record:", test_record)
        
        return True
    except Exception as e:
        if DEBUG_MODE:
            st.sidebar.error(f"❌ Distribution test failed: {str(e)}")
        return False

# -------------------------------
# Streamlit page setup with custom CSS
# -------------------------------
st.set_page_config(
    page_title="🌶️ SpiseUp Finance Tracker",
    layout="wide",
    page_icon="🌶️",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling with improved visibility
st.markdown("""
<style>
    /* Main container */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header styling - Improved for visibility */
    .main-header {
        font-size: 2.8rem !important;
        font-weight: 700;
        background: linear-gradient(90deg, #D32F2F 0%, #F57C00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        color: #333333;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Metric cards - Improved text contrast */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #D32F2F;
        transition: transform 0.3s ease;
    }
    
    .metric-card h3 {
        color: #333333 !important;
        font-weight: 600;
    }
    
    .metric-card .st-emotion-cache-1fcdlhc {
        color: #333333 !important;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
    }
    
            // Fix metric text colors
document.addEventListener('DOMContentLoaded', function() {
    // Fix all metric values
    const metrics = document.querySelectorAll('[data-testid="stMetricValue"]');
    metrics.forEach(metric => {
        metric.style.color = '#333333';
        metric.style.fontWeight = 'bold';
    });
    
    // Fix metric labels
    const labels = document.querySelectorAll('[data-testid="stMetricLabel"]');
    labels.forEach(label => {
        label.style.color = '#666666';
    });
            
            // Detect dark mode
const isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

if (isDarkMode) {
    // Add dark mode specific overrides
    const style = document.createElement('style');
    style.textContent = `
        .main-header {
            background: linear-gradient(90deg, #FF8A80 0%, #FFD180 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stMetric div[data-testid="stMetricValue"] {
            color: #FFFFFF !important;
        }
        .stMarkdown, .stText, .stTitle, .stHeader {
            color: #FFFFFF !important;
        }
    `;
    document.head.appendChild(style);
}
            
    /* Section headers - Better contrast */
    .section-header {
        background: linear-gradient(90deg, #1565C0 0%, #1976D2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0 1rem 0;
        font-weight: 600;
        font-size: 1.2rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    /* Custom tabs styling - Better visibility */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: #f0f2f6;
        padding: 0px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding: 0 24px;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0 0;
        font-weight: 500;
        color: #555555;  /* Darker for better visibility */
        border-right: 1px solid #ddd;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #D32F2F;  /* Stronger red */
        font-weight: 700;
        border-bottom: 3px solid #D32F2F;
    }
    
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        color: #333333;  /* Darker on hover */
        background-color: #e6e9ef;
    }
    
    /* Form styling */
    .stForm {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .stForm label {
        color: #333333 !important;
        font-weight: 500;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #D32F2F 0%, #F57C00 100%);
        color: white !important;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(211, 47, 47, 0.3);
        color: white !important;
    }
    
    /* Alert boxes - Better contrast */
    .alert-box {
        background: linear-gradient(90deg, #FFF3E0 0%, #FFECB3 100%);
        border-left: 5px solid #FF9800;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #5D4037;
        font-weight: 500;
    }
    
    .alert-box strong {
        color: #D32F2F;
    }
    
    /* Data table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .dataframe th {
        background-color: #1976D2 !important;
        color: white !important;
        font-weight: 600;
    }
    
    .dataframe td {
        color: #333333 !important;
    }
    
    /* Fix for Streamlit's default text colors */
    .stMarkdown, .stText, .stTitle, .stHeader {
        color: #333333 !important;
    }
    
    /* Improve visibility for metric values */
    .stMetric {
        color: #333333 !important;
    }
    
    .stMetric label {
        color: #666666 !important;
        font-weight: 500;
    }
    
    .stMetric div[data-testid="stMetricValue"] {
        color: #333333 !important;
        font-weight: 700;
    }
    
    /* Improve form input labels */
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stDateInput label, .stTextArea label {
        color: #333333 !important;
        font-weight: 500;
    }
    
    /* Make placeholders more visible */
    ::placeholder {
        color: #999999 !important;
        opacity: 1;
    }
    
    /* Improve info/warning/success/error boxes */
    .stAlert {
        color: #333333 !important;
    }
    
    .stAlert [data-testid="stMarkdownContainer"] {
        color: #333333 !important;
    }
    
    /* Improve expander visibility */
    .streamlit-expanderHeader {
        color: #333333 !important;
        font-weight: 600;
    }
    
    /* Make all text in containers dark */
    .stContainer, .stColumn, .stExpander {
        color: #333333 !important;
    }
    
    /* Fix for captions and small text */
    .stCaption {
        color: #666666 !important;
    }
    
    /* Improve selectbox dropdown */
    .stSelectbox div[data-baseweb="select"] {
        color: #333333 !important;
    }
    
    /* Make all h1-h6 tags dark */
    h1, h2, h3, h4, h5, h6 {
        color: #333333 !important;
    }
    
    /* Divider color */
    hr {
        border-color: #e0e0e0 !important;
    }
    
    /* Make sidebar text more visible */
    .sidebar .sidebar-content {
        color: #333333 !important;
    }
    
    .sidebar .stSelectbox label, 
    .sidebar .stMultiselect label, 
    .sidebar .stDateInput label,
    .sidebar .stButton button {
        color: #333333 !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
col1, col2 = st.columns([1, 5])
with col1:
    st.image("spicyup.jpeg", width=80)
with col2:
    st.markdown('<h1 class="main-header">🌶️ SpiseUp Field & Finance Tracker</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Track sales, expenses, salespeople, distribution, and net profit in real-time!</p>', unsafe_allow_html=True)

st.markdown("---")

# -------------------------------
# SIDEBAR FILTERS
# -------------------------------
with st.sidebar:
    st.markdown('<div class="section-header">📅 Filter Data</div>', unsafe_allow_html=True)
    
    # Date filter
    filter_mode = st.selectbox(
        "Select Period",
        ["Custom Range", "Today", "Yesterday", "This Week", "Last Week", "This Month", "Last Month", "Last 7 Days", "Last 30 Days"]
    )
    
    start_date = end_date = date.today()
    
    if filter_mode == "Custom Range":
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
    
    # Advanced Filters
    st.markdown('<div class="section-header">🔍 Advanced Filters</div>', unsafe_allow_html=True)
    
    # Salesperson filter
    sales_people = get_sales_people()
    sales_person_options = {p['full_name']: p['id'] for p in sales_people} if sales_people else {}
    
    if sales_people:
        salesperson_filter = st.multiselect(
            "Filter by Salesperson:",
            options=["All"] + list(sales_person_options.keys()),
            default=["All"]
        )
    
    # Payment status filter
    payment_filter = st.multiselect(
        "Payment Status:",
        ["All", "Cash", "Credit / Pending"],
        default=["All"]
    )
    
    # Product filter
    product_filter = st.multiselect(
        "Product:",
        ["All", "SpiseUp Chilli Sachet", "Other"],
        default=["All"]
    )
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    if st.button("📊 Generate Report", use_container_width=True):
        st.info("Report generation feature coming soon!")
    
    # Last updated
    st.markdown(f"**Last updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # In the sidebar, after other filters
st.sidebar.markdown("---")
st.sidebar.markdown("### 🧪 Testing")

if st.sidebar.button("Test Distribution Connection"):
    if test_distribution_connection():
        st.sidebar.success("✅ Distribution connection test passed!")
    else:
        st.sidebar.error("❌ Distribution connection test failed!")

if st.sidebar.button("Check Database Structure"):
    # Show current table structure
    st.sidebar.write("**Current DISTRIBUTION columns expected:**")
    expected_columns = [
        "id", "date", "sales_person_id", "sale_id", "distributor_type",
        "location", "product", "quantity_distributed", "unit_price",
        "expected_amount", "distribution_type", "status", "notes"
    ]
    for col in expected_columns:
        st.sidebar.write(f"- {col}")

# -------------------------------
# FETCH & PREPARE DATA
# -------------------------------
# -------------------------------
# FETCH & PREPARE DATA (FIXED VERSION)
# -------------------------------
@st.cache_data(ttl=0, show_spinner=False)  # Cache for 5 minutes
def fetch_raw_data():
    """Fetch raw data without filtering - cache this only"""
    sales_data = get_sales_summary()
    expense_data = get_expenses_summary()
    distribution_data = get_distribution_data()  # Fetch all, filter later
    sales_people_data = get_sales_people()
    
    # Convert to DataFrames
    sales_df = pd.DataFrame(sales_data) if sales_data else pd.DataFrame()
    expenses_df = pd.DataFrame(expense_data) if expense_data else pd.DataFrame()
    dist_df = pd.DataFrame(distribution_data) if distribution_data else pd.DataFrame()
    sp_df = pd.DataFrame(sales_people_data) if sales_people_data else pd.DataFrame()
    
    # Debug: Show raw counts
    if DEBUG_MODE:
        st.sidebar.write(f"📊 RAW DATA COUNTS:")
        st.sidebar.write(f"- Sales in DB: {len(sales_df)}")
        st.sidebar.write(f"- Expenses in DB: {len(expenses_df)}")
        st.sidebar.write(f"- Distributions in DB: {len(dist_df)}")
        st.sidebar.write(f"- Salespeople: {len(sp_df)}")
    
    return sales_df, expenses_df, dist_df, sp_df

# Fetch raw data (cached)
raw_sales_df, raw_expenses_df, raw_dist_df, raw_sp_df = fetch_raw_data()

# -------------------------------
# APPLY DATE FILTERS (outside cache)
# -------------------------------
def filter_by_date(df, date_column, start_date, end_date):
    """Safely filter dataframe by date range"""
    if df.empty or date_column not in df.columns:
        return df
    
    try:
        # Ensure datetime conversion
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        df = df.dropna(subset=[date_column])
        
        # Convert filter dates to datetime
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        # Filter
        mask = (df[date_column] >= start_dt) & (df[date_column] <= end_dt)
        filtered = df[mask].copy()
        
        if DEBUG_MODE and len(df) > 0 and len(filtered) == 0:
            st.sidebar.warning(f"⚠️ No data in selected range!")
            st.sidebar.write(f"Data range: {df[date_column].min().date()} to {df[date_column].max().date()}")
            st.sidebar.write(f"Selected: {start_dt.date()} to {end_dt.date()}")
        
        return filtered
    except Exception as e:
        if DEBUG_MODE:
            st.sidebar.error(f"Filter error: {e}")
        return df

# Apply filters
sales_df = filter_by_date(raw_sales_df.copy(), 'Date', start_date, end_date)
expenses_df = filter_by_date(raw_expenses_df.copy(), 'date', start_date, end_date)
dist_df = filter_by_date(raw_dist_df.copy(), 'date', start_date, end_date)
sp_df = raw_sp_df.copy()  # No date filter for salespeople

# Convert numeric safely
if not sales_df.empty:
    for col in ['Total', 'Quantity', 'Price_per_Unit']:
        if col in sales_df.columns:
            sales_df[col] = pd.to_numeric(sales_df[col], errors='coerce').fillna(0)

if not expenses_df.empty and 'amount' in expenses_df.columns:
    expenses_df['amount'] = pd.to_numeric(expenses_df['amount'], errors='coerce').fillna(0)

# Debug: Show filtered counts
if DEBUG_MODE:
    with st.sidebar.expander("📊 Filtered Data Debug", expanded=False):
        st.write(f"**FILTERED DATA:**")
        st.write(f"- Sales: {len(sales_df)} of {len(raw_sales_df)}")
        st.write(f"- Expenses: {len(expenses_df)} of {len(raw_expenses_df)}")
        st.write(f"- Distributions: {len(dist_df)} of {len(raw_dist_df)}")
        
        if not sales_df.empty:
            st.write(f"**Sales Date Range:**")
            st.write(f"Min: {sales_df['Date'].min().date()}")
            st.write(f"Max: {sales_df['Date'].max().date()}")
        
        st.write(f"**Current Filter:**")
        st.write(f"Mode: {filter_mode}")
        st.write(f"Start: {start_date}")
        st.write(f"End: {end_date}")

# -------------------------------
# CALCULATE KPIs
# -------------------------------
def calculate_kpis(sales_df, expenses_df):
    # Basic metrics
    total_sales = sales_df['Total'].sum() if not sales_df.empty else 0
    total_cash = sales_df[sales_df['Payment_Status'] == "Cash"]['Total'].sum() if not sales_df.empty else 0
    total_credit = sales_df[sales_df['Payment_Status'] != "Cash"]['Total'].sum() if not sales_df.empty else 0
    total_expenses = expenses_df['amount'].sum() if not expenses_df.empty else 0
    net_profit = total_sales - total_expenses
    running_balance = total_cash - total_expenses
    
    # Additional KPIs
    if not sales_df.empty:
        total_sachets = sales_df['Quantity'].sum()
        avg_sale_value = sales_df['Total'].mean() if len(sales_df) > 0 else 0
        avg_sachets_per_sale = sales_df['Quantity'].mean() if len(sales_df) > 0 else 0
        cash_percentage = (total_cash / total_sales * 100) if total_sales > 0 else 0
        credit_percentage = (total_credit / total_sales * 100) if total_sales > 0 else 0
        
        # Calculate daily metrics
        sales_by_date = sales_df.groupby('Date')['Total'].sum()
        if len(sales_by_date) > 0:
            avg_daily_sales = sales_by_date.mean()
            best_day = sales_by_date.idxmax()
            best_day_sales = sales_by_date.max()
        else:
            avg_daily_sales = 0
            best_day = None
            best_day_sales = 0
    else:
        total_sachets = 0
        avg_sale_value = 0
        avg_sachets_per_sale = 0
        cash_percentage = 0
        credit_percentage = 0
        avg_daily_sales = 0
        best_day = None
        best_day_sales = 0
    
    if not expenses_df.empty:
        avg_expense = expenses_df['amount'].mean()
        top_expense_category = expenses_df.groupby('category')['amount'].sum().idxmax() if len(expenses_df['category'].unique()) > 0 else "None"
    else:
        avg_expense = 0
        top_expense_category = "None"
    
    return {
        'total_sales': total_sales,
        'total_cash': total_cash,
        'total_credit': total_credit,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'running_balance': running_balance,
        'total_sachets': total_sachets,
        'avg_sale_value': avg_sale_value,
        'avg_sachets_per_sale': avg_sachets_per_sale,
        'cash_percentage': cash_percentage,
        'credit_percentage': credit_percentage,
        'avg_daily_sales': avg_daily_sales,
        'best_day': best_day,
        'best_day_sales': best_day_sales,
        'avg_expense': avg_expense,
        'top_expense_category': top_expense_category
    }

kpis = calculate_kpis(sales_df, expenses_df)

# -------------------------------
# CREATE TABS
# -------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard", 
    "💰 Sales", 
    "💸 Expenses", 
    "👥 Salespeople", 
    "📈 Analytics"
])

# -------------------------------
# TAB 1: DASHBOARD
# -------------------------------
with tab1:
    st.markdown('<div class="section-header">📈 Financial Overview</div>', unsafe_allow_html=True)
    
    # Top Metrics Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Sales", f"KES {kpis['total_sales']:,.0f}")
        st.caption(f"📦 {kpis['total_sachets']:,.0f} sachets sold")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Net Profit", f"KES {kpis['net_profit']:,.0f}")
        profit_color = "green" if kpis['net_profit'] >= 0 else "red"
        st.caption(f"Profit Margin: {(kpis['net_profit']/kpis['total_sales']*100 if kpis['total_sales'] > 0 else 0):.1f}%", 
                  help="Net Profit ÷ Total Sales")
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
        st.metric("Cash Collected", f"KES {kpis['total_cash']:,.0f}", 
                 delta=f"{kpis['cash_percentage']:.1f}% of total")
    
    with col5:
        st.metric("Credit Pending", f"KES {kpis['total_credit']:,.0f}", 
                 delta=f"{kpis['credit_percentage']:.1f}% of total", 
                 delta_color="inverse")
    
    with col6:
        st.metric("Total Expenses", f"KES {kpis['total_expenses']:,.0f}",
                 help=f"Top category: {kpis['top_expense_category']}")
    
    # Alerts Section
    alerts = []
    if kpis['credit_percentage'] > 30:
        alerts.append("⚠️ **High credit sales** (>30% of total). Consider following up on pending payments.")
    if kpis['net_profit'] < 0:
        alerts.append("🔴 **Negative net profit**. Review expenses and pricing strategy.")
    if kpis['running_balance'] < 10000:
        alerts.append("💰 **Low cash balance**. Monitor expenses closely.")
    if kpis['total_credit'] > kpis['total_cash']:
        alerts.append("📈 **Credit exceeds cash**. Focus on cash sales collection.")
    
    if alerts:
        st.markdown('<div class="section-header">🚨 Alerts & Notifications</div>', unsafe_allow_html=True)
        for alert in alerts:
            st.markdown(f'<div class="alert-box">{alert}</div>', unsafe_allow_html=True)
    
    # Charts Section
    st.markdown('<div class="section-header">📊 Performance Charts</div>', unsafe_allow_html=True)
    
    if not sales_df.empty or not expenses_df.empty:
        # Create combined data for charts
        if not sales_df.empty:
            sales_by_date = sales_df.groupby("Date")['Total'].sum().reset_index()
            sales_by_date.columns = ['Date', 'Sales']
        
        if not expenses_df.empty:
            expenses_by_date = expenses_df.groupby("date")['amount'].sum().reset_index()
            expenses_by_date.columns = ['Date', 'Expenses']
        
        # Combined chart
        if not sales_df.empty and not expenses_df.empty:
            combined_df = pd.merge(sales_by_date, expenses_by_date, on='Date', how='outer').fillna(0)
            combined_df['Net Profit'] = combined_df['Sales'] - combined_df['Expenses']
        elif not sales_df.empty:
            combined_df = sales_by_date.copy()
            combined_df['Expenses'] = 0
            combined_df['Net Profit'] = combined_df['Sales']
        elif not expenses_df.empty:
            combined_df = expenses_by_date.copy()
            combined_df['Sales'] = 0
            combined_df['Net Profit'] = -combined_df['Expenses']
        
        # Chart 1: Sales vs Expenses vs Profit
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=combined_df['Date'],
            y=combined_df['Sales'],
            name='Sales',
            marker_color='#36B37E',
            opacity=0.7
        ))
        fig.add_trace(go.Bar(
            x=combined_df['Date'],
            y=combined_df['Expenses'],
            name='Expenses',
            marker_color='#FF4B4B',
            opacity=0.7
        ))
        fig.add_trace(go.Scatter(
            x=combined_df['Date'],
            y=combined_df['Net Profit'],
            name='Net Profit',
            mode='lines+markers',
            line=dict(color='#FFB020', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Sales vs Expenses vs Net Profit',
            xaxis_title='Date',
            yaxis_title='Amount (KES)',
            hovermode='x unified',
            template='plotly_white',
            barmode='group',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Quick Stats
    st.markdown('<div class="section-header">📋 Quick Statistics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info(f"**Avg Sale Value:**\nKES {kpis['avg_sale_value']:,.0f}")
    with col2:
        st.info(f"**Avg Sachets/Sale:**\n{kpis['avg_sachets_per_sale']:.1f}")
    with col3:
        st.info(f"**Avg Daily Sales:**\nKES {kpis['avg_daily_sales']:,.0f}")
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
                st.write(f"📦 {int(row['Quantity'])} sachets")
            with col3:
                st.write(f"💰 KES {row['Total']:,.0f}")
            st.divider()

# -------------------------------
# TAB 2: SALES
# -------------------------------
with tab2:
    st.markdown('<div class="section-header">💰 Record New Sale</div>', unsafe_allow_html=True)
    
    # Two-column form layout
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
            product = st.selectbox("Product", ["SpiseUp Chilli Sachet", "SpiseUp Hot Sauce", "Other"])
            quantity = st.number_input("Quantity (sachets)", min_value=1, step=1, value=10)
            price = st.number_input("Price per sachet (KES)", min_value=1, step=10, value=5)
            payment_status = st.selectbox("Payment Status", ["Cash", "Credit / Pending"])
            
            if sales_person_options:
                sales_person_name = st.selectbox(
                    "Sales Person",
                    ["Select..."] + list(sales_person_options.keys())
                )
            else:
                sales_person_name = "N/A"
                st.warning("No salespeople added yet. Add salespeople in the Salespeople tab.")
    
    # Additional details in expander
    with st.expander("📝 Additional Details"):
        feedback = st.text_area("Customer Feedback", placeholder="Any feedback from the customer...")
        follow_up = st.text_input("Follow-up Action", placeholder="Next steps or follow-up required...")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        submitted_sale = st.button("💾 Save Sale", type="primary", use_container_width=True)
    
    with col2:
        clear_form = st.button("🗑️ Clear Form", use_container_width=True)

       # ⬇️⬇️⬇️ CLEAR FORM LOGIC  ⬇️⬇️⬇️  

    if clear_form:
        # Clear session state
        for key in ['shop_name', 'phone', 'location', 'product', 
                    'quantity', 'price', 'payment_status', 
                    'sales_person_name', 'feedback', 'follow_up']:
            if key in st.session_state:
                del st.session_state[key]
        st.success("✅ Form cleared!")
        st.rerun()
    
    if submitted_sale:
    # ALL validation MUST be INSIDE this if block
        if not shop_name.strip():
            st.error("Please enter a Shop/Contact Name!")
        elif sales_person_name == "Select...":
            st.error("Please select a salesperson!")
        else:
            total = quantity * price
            sale_record = {
            "Date": str(sale_date),
            "Name": shop_name,
            "Phone": phone,
            "Location": location,
            "Product": product,
            "Quantity": quantity,
            "Price_per_Unit": price,
            "Total": total,
            "Payment_Status": payment_status,
            "Feedback": feedback,
            "Follow_Up": follow_up
        }
        
        if DEBUG_MODE:
            st.write("🔍 **DEBUG MODE ACTIVE**")
            st.write("Form data received:")
            st.write(f"- Shop Name: {shop_name}")
            st.write(f"- Quantity: {quantity}")
            st.write(f"- Price: {price}")
            st.write(f"- Salesperson: {sales_person_name}")
            st.write("🔍 Sale record to save:", sale_record)
        
        # Save the sale first
        sale_id = save_sale(sale_record)
        
        if DEBUG_MODE:
            st.write(f"🔍 Save sale returned ID: {sale_id}")
        
        if sale_id:
            st.success(f"✅ Sale saved successfully! Total: **KES {total:,.0f}**")
            st.write(f"**Sale ID:** `{sale_id}`")
            
            # Only save distribution if a salesperson is selected
            if sales_person_name not in ["Select...", "N/A"] and sales_person_name in sales_person_options:
                sales_person_id = sales_person_options[sales_person_name]
                
                if DEBUG_MODE:
                    st.write("🔍 Attempting to save distribution...")
                    st.write(f"- Sale ID: {sale_id}")
                    st.write(f"- Salesperson ID: {sales_person_id}")
                    st.write(f"- Salesperson Name: {sales_person_name}")
                    st.write(f"- Quantity: {quantity}")
                    st.write(f"- Price: {price}")
                
                # Call the UPDATED save_distribution function
                try:
                    success = save_distribution(
                        sale_id=sale_id,
                        sales_person_id=sales_person_id,
                        quantity=quantity,
                        sale_date=str(sale_date),
                        price=price,
                        sale_data=sale_record
                    )
                    
                    if DEBUG_MODE:
                        st.write(f"🔍 save_distribution returned: {success}")
                    
                    if success:
                        st.info(f"👤 Successfully assigned to: **{sales_person_name}**")
                        st.balloons()
                    else:
                        st.warning(f"⚠️ Sale saved but could not assign to {sales_person_name}.")
                        
                except Exception as e:
                    st.error(f"❌ Error saving distribution: {str(e)}")
                    if DEBUG_MODE:
                        import traceback
                        st.write("Full traceback:")
                        st.code(traceback.format_exc())
            else:
                if DEBUG_MODE:
                    st.write("🔍 No distribution saved because:")
                    st.write(f"- Salesperson name: {sales_person_name}")
                    st.write(f"- In options: {sales_person_name in sales_person_options}")
        else:
            st.error("❌ Failed to save sale. Please check your input and try again.")
    
    # Recent Sales Table
    st.markdown('<div class="section-header">📋 Recent Sales</div>', unsafe_allow_html=True)
    
    if not sales_df.empty:
        recent_sales = sales_df.sort_values('Date', ascending=False).head(20)
        
        # Format for display
        display_df = recent_sales.copy()
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        display_df['Total'] = display_df['Total'].apply(lambda x: f"KES {x:,.0f}")
        display_df['Price_per_Unit'] = display_df['Price_per_Unit'].apply(lambda x: f"KES {x:,.0f}")
        
        st.dataframe(
            display_df[['Date', 'Name', 'Quantity', 'Price_per_Unit', 'Total', 'Payment_Status', 'Location']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Date": st.column_config.TextColumn("Date"),
                "Name": st.column_config.TextColumn("Shop Name"),
                "Quantity": st.column_config.NumberColumn("Qty"),
                "Price_per_Unit": st.column_config.TextColumn("Unit Price"),
                "Total": st.column_config.TextColumn("Total"),
                "Payment_Status": st.column_config.TextColumn("Payment"),
                "Location": st.column_config.TextColumn("Location")
            }
        )
        
        # Sales analysis
        st.markdown('<div class="section-header">📊 Sales Analysis</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            # Sales by payment status
            if not sales_df.empty:
                payment_summary = sales_df.groupby('Payment_Status')['Total'].sum().reset_index()
                fig = px.pie(payment_summary, values='Total', names='Payment_Status',
                            title='Sales by Payment Status',
                            color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top locations
            if not sales_df.empty:
                location_summary = sales_df.groupby('Location')['Total'].sum().reset_index().sort_values('Total', ascending=False).head(10)
                fig = px.bar(location_summary, x='Location', y='Total',
                           title='Top 10 Locations by Sales',
                           color='Total', color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)

# In your Sales tab (Tab 2), add at the bottom
if DEBUG_MODE:
    st.markdown("---")
    st.subheader("🧪 Debug Testing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Test Sale + Distribution", type="primary", help="Create a test sale with distribution"):
            try:
                # Generate unique shop name
                shop_name = f"Debug Shop {datetime.now().strftime('%H:%M:%S')}"
                
                # Create sale
                sale_data = {
                    "Date": str(date.today()),
                    "Name": shop_name,
                    "Phone": "0712000000",
                    "Location": "Test Location",
                    "Product": "SpiseUp Chilli Sachet",
                    "Quantity": 15,
                    "Price_per_Unit": 50,
                    "Total": 750,
                    "Payment_Status": "Cash",
                    "Feedback": "Debug sale",
                    "Follow_Up": ""
                }
                
                sale_id = save_sale(sale_data)
                
                if sale_id:
                    st.success(f"✅ Sale created: {shop_name}")
                    
                    # Try distribution
                    if sales_person_options:
                        sp_name = list(sales_person_options.keys())[0]
                        sp_id = sales_person_options[sp_name]
                        
                        dist_success = save_distribution(
                            sale_id=sale_id,
                            sales_person_id=sp_id,
                            quantity=15,
                            sale_date=str(date.today()),
                            price=50,
                            sale_data=sale_data
                        )
                        
                        if dist_success:
                            st.info(f"✅ Distribution assigned to {sp_name}")
                        else:
                            st.warning("⚠️ Distribution failed (check logs)")
                    else:
                        st.warning("⚠️ No salespeople to assign")
                else:
                    st.error("❌ Sale creation failed")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.button("Test Sale Only", help="Create test sale without distribution"):
            try:
                shop_name = f"Test Only {datetime.now().strftime('%H:%M:%S')}"
                sale_data = {
                    "Date": str(date.today()),
                    "Name": shop_name,
                    "Phone": "0722000000",
                    "Location": "Test Only",
                    "Product": "SpiseUp Chilli Sachet",
                    "Quantity": 5,
                    "Price_per_Unit": 40,
                    "Total": 200,
                    "Payment_Status": "Credit / Pending",
                    "Feedback": "",
                    "Follow_Up": ""
                }
                
                sale_id = save_sale(sale_data)
                if sale_id:
                    st.success(f"✅ Sale created: {shop_name}")
                else:
                    st.error("❌ Failed")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")       
# -------------------------------
# TAB 3: EXPENSES
# -------------------------------
with tab3:
    st.markdown('<div class="section-header">💸 Record New Expense</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        expense_date = st.date_input("Date", value=date.today(), key="expense_date")
        category = st.selectbox("Category", 
                              ["Supplies", "Transport", "Marketing", "Salaries", 
                               "Office Rent", "Utilities", "Other"])
        amount = st.number_input("Amount (KES)", min_value=0, step=100, value=1000)
        description = st.text_area("Description", placeholder="Details about this expense...")
    
    with col2:
        payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Mobile Money", "Credit Card"])
        paid_by = st.text_input("Paid By", placeholder="Name of person who paid")
        status = st.selectbox("Status", ["Paid", "Pending", "Reimbursed"])
        
        if category == "Other":
            custom_category = st.text_input("Specify Category", placeholder="Enter custom category...")
            if custom_category:
                category = custom_category
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        submitted_expense = st.button("💾 Save Expense", type="primary", use_container_width=True)
    
    if submitted_expense:
        if amount <= 0:
            st.error("Please enter a valid amount!")
        else:
            expense_record = {
                "date": str(expense_date),
                "category": category,
                "description": description,
                "amount": amount,
                "payment_method": payment_method,
                "paid_by": paid_by,
                "receipt": "",
                "status": status
            }
            save_expense(expense_record)
            st.success(f"✅ Expense saved! Amount: **KES {amount:,.0f}**")
    
    # Expense Analysis
    st.markdown('<div class="section-header">📊 Expense Analysis</div>', unsafe_allow_html=True)
    
    if not expenses_df.empty:
        # Expense metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            total_exp = expenses_df['amount'].sum()
            st.metric("Total Expenses", f"KES {total_exp:,.0f}")
        with col2:
            avg_exp = expenses_df['amount'].mean()
            st.metric("Average Expense", f"KES {avg_exp:,.0f}")
        with col3:
            expense_count = len(expenses_df)
            st.metric("Number of Expenses", expense_count)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Expenses by category
            category_summary = expenses_df.groupby("category")['amount'].sum().reset_index().sort_values('amount', ascending=False)
            fig = px.bar(category_summary, x='category', y='amount',
                        title='Expenses by Category',
                        color='amount', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Expense trend
            expenses_by_date = expenses_df.groupby('date')['amount'].sum().reset_index()
            fig = px.line(expenses_by_date, x='date', y='amount',
                         title='Expense Trend Over Time',
                         markers=True, line_shape='spline')
            fig.update_traces(line=dict(color='#FF4B4B', width=3))
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent expenses table
        st.markdown('<div class="section-header">📋 Recent Expenses</div>', unsafe_allow_html=True)
        
        recent_expenses = expenses_df.sort_values('date', ascending=False).head(20)
        display_expenses = recent_expenses.copy()
        display_expenses['date'] = display_expenses['date'].dt.strftime('%Y-%m-%d')
        display_expenses['amount'] = display_expenses['amount'].apply(lambda x: f"KES {x:,.0f}")
        
        st.dataframe(
            display_expenses[['date', 'category', 'description', 'amount', 'payment_method', 'status']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No expenses recorded yet. Start by adding an expense above.")

# -------------------------------
# TAB 4: SALESPEOPLE
# -------------------------------
with tab4:
    st.markdown('<div class="section-header">👥 Manage Sales Team</div>', unsafe_allow_html=True)
    
    # Add Salesperson Form
    with st.expander("➕ Add New Salesperson", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name", key="sp_name")
            phone = st.text_input("Phone Number", key="sp_phone")
            role = st.selectbox("Role", ["Sales Rep", "Manager", "Distributor", "Team Lead"], key="sp_role")
        
        with col2:
            location = st.text_input("Location", key="sp_location")
            status = st.selectbox("Status", ["Active", "Inactive", "On Leave"], key="sp_status")
            commission_rate = st.number_input("Commission Rate (%)", 
                                            min_value=0.0, max_value=100.0, 
                                            step=0.5, value=5.0, key="sp_commission")
        
        notes = st.text_area("Notes", placeholder="Additional information...", key="sp_notes")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            add_sales_person = st.button("➕ Add Salesperson", type="primary", use_container_width=True)
        
        if add_sales_person:
            if not full_name.strip() or not phone.strip() or not role.strip() or not location.strip():
                st.warning("Please fill in all required fields!")
            else:
                sp_id = save_sales_person(
                    full_name=full_name,
                    phone=phone,
                    role=role,
                    location=location,
                    status=status,
                    commission_rate=commission_rate,
                    notes=notes
                )
                if sp_id:
                    st.success(f"✅ Salesperson '{full_name}' added successfully!")
                    st.balloons()
                else:
                    st.error("❌ Failed to add salesperson. Please check the details.")
    
    # Sales Team Overview
    st.markdown('<div class="section-header">👥 Sales Team Overview</div>', unsafe_allow_html=True)
    
    if sales_people:
        # Stats
        active_count = len([p for p in sales_people if p.get('status') == 'Active'])
        managers = len([p for p in sales_people if p.get('role') in ['Manager', 'Team Lead']])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Team Members", len(sales_people))
        with col2:
            st.metric("Active Members", active_count)
        with col3:
            st.metric("Managers/Leads", managers)
        
        # Salesperson Cards
        st.markdown("### Team Members")
        
        # Filter by status
        status_filter = st.multiselect(
            "Filter by Status:",
            ["Active", "Inactive", "On Leave"],
            default=["Active"]
        )
        
        filtered_team = [p for p in sales_people if p.get('status') in status_filter]
        
        if filtered_team:
            for person in filtered_team:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 2])
                    with col1:
                        st.write(f"**{person['full_name']}**")
                        st.caption(f"📍 {person['location']} • {person['role']}")
                    with col2:
                        st.write(f"📱 {person['phone']}")
                        status_color = "🟢" if person['status'] == 'Active' else "🔴" if person['status'] == 'Inactive' else "🟡"
                        st.caption(f"{status_color} {person['status']}")
                    with col3:
                        if person.get('commission_rate'):
                            st.write(f"💰 {person['commission_rate']}% commission")
                        if person.get('notes'):
                            with st.expander("Notes"):
                                st.write(person['notes'])
                    st.divider()
        else:
            st.info("No team members match the selected filters.")
    else:
        st.info("No salespeople added yet. Use the form above to add your first salesperson.")

# -------------------------------
# TAB 5: ANALYTICS
# -------------------------------
with tab5:
    st.markdown('<div class="section-header">📈 Advanced Analytics</div>', unsafe_allow_html=True)
    
    # Analytics subtabs
    analytics_tab1, analytics_tab2, analytics_tab3 = st.tabs([
        "🏆 Performance Leaderboards",
        "📊 Distribution Insights",
        "📁 Data Management"
    ])
    
    with analytics_tab1:
        # Salespeople Leaderboard
        if not dist_df.empty and not sp_df.empty:
            st.markdown("### 🏆 Salespeople Performance Leaderboard")
            
            dist_merged = dist_df.merge(sp_df, left_on="sales_person_id", right_on="id")
            dist_merged['Total_Value'] = dist_merged['quantity_distributed'] * dist_merged['unit_price']
            
            # Top performers by value
            sp_summary_value = dist_merged.groupby("full_name").agg({
                'Total_Value': 'sum',
                'quantity_distributed': 'sum',
                'sales_person_id': 'count'
            }).reset_index()
            
            sp_summary_value.columns = ['Salesperson', 'Total Revenue (KES)', 'Total Quantity', 'Number of Sales']
            sp_summary_value = sp_summary_value.sort_values('Total Revenue (KES)', ascending=False)
            
            # Display as table with ranking
            sp_summary_value['Rank'] = range(1, len(sp_summary_value) + 1)
            display_cols = ['Rank', 'Salesperson', 'Total Revenue (KES)', 'Total Quantity', 'Number of Sales']
            
            st.dataframe(
                sp_summary_value[display_cols],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn("Rank", width="small"),
                    "Salesperson": st.column_config.TextColumn("Salesperson"),
                    "Total Revenue (KES)": st.column_config.NumberColumn("Revenue", format="KES %d"),
                    "Total Quantity": st.column_config.NumberColumn("Qty Sold", format="%d"),
                    "Number of Sales": st.column_config.NumberColumn("# Sales", format="%d")
                }
            )
            
            # Visualization
            col1, col2 = st.columns(2)
            
            with col1:
                top_10_value = sp_summary_value.head(10)
                fig = px.bar(top_10_value, x='Salesperson', y='Total Revenue (KES)',
                            title='Top 10 Salespeople by Revenue',
                            color='Total Revenue (KES)', color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                top_10_qty = sp_summary_value.sort_values('Total Quantity', ascending=False).head(10)
                fig = px.bar(top_10_qty, x='Salesperson', y='Total Quantity',
                            title='Top 10 Salespeople by Quantity Sold',
                            color='Total Quantity', color_continuous_scale='Plasma')
                st.plotly_chart(fig, use_container_width=True)
        
        # Shop Performance
        if not dist_df.empty and not sales_df.empty and not sp_df.empty:
            st.markdown("### 🏪 Shop Performance Analysis")
            
            merged_shop = dist_df.merge(sales_df, left_on="sale_id", right_on="id")
            merged_shop = merged_shop.merge(sp_df, left_on="sales_person_id", right_on="id")
            
            shop_summary = merged_shop.groupby("Name").agg(
                total_quantity=pd.NamedAgg(column="quantity", aggfunc="sum"),
                total_value=pd.NamedAgg(column="price_per_unit", 
                                      aggfunc=lambda x: (merged_shop.loc[x.index, 'quantity'] * x).sum()),
                num_visits=pd.NamedAgg(column="sale_id", aggfunc="nunique"),
                avg_order_value=pd.NamedAgg(column="Total", aggfunc="mean")
            ).reset_index()
            
            shop_summary.columns = ['Shop Name', 'Total Quantity', 'Total Revenue', 'Number of Visits', 'Average Order Value']
            shop_summary = shop_summary.sort_values('Total Revenue', ascending=False)
            
            # Display top shops
            st.dataframe(
                shop_summary.head(15),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Shop Name": st.column_config.TextColumn("Shop"),
                    "Total Revenue": st.column_config.NumberColumn("Revenue", format="KES %d"),
                    "Total Quantity": st.column_config.NumberColumn("Qty", format="%d"),
                    "Number of Visits": st.column_config.NumberColumn("Visits", format="%d"),
                    "Average Order Value": st.column_config.NumberColumn("Avg Order", format="KES %d")
                }
            )
            
            # Shop performance visualization
            fig = px.scatter(shop_summary.head(20), 
                           x='Number of Visits', 
                           y='Total Revenue',
                           size='Average Order Value',
                           color='Total Quantity',
                           hover_name='Shop Name',
                           title='Shop Performance: Visits vs Revenue',
                           labels={'Number of Visits': 'Number of Visits', 'Total Revenue': 'Total Revenue (KES)'},
                           color_continuous_scale='Rainbow')
            st.plotly_chart(fig, use_container_width=True)
    
    with analytics_tab2:
        st.markdown("### 📊 Distribution Channel Analysis")
        
        if not dist_df.empty and not sp_df.empty:
            # Sales by location
            dist_merged = dist_df.merge(sp_df, left_on="sales_person_id", right_on="id")
            
            # Location analysis
            location_summary = dist_merged.groupby('location').agg({
                'quantity': 'sum',
                'sales_person_id': 'nunique'
            }).reset_index()
            
            location_summary.columns = ['Location', 'Total Quantity', 'Number of Salespeople']
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.treemap(location_summary, 
                                path=['Location'], 
                                values='Total Quantity',
                                title='Sales Distribution by Location',
                                color='Total Quantity',
                                color_continuous_scale='RdBu')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Salesperson productivity
                productivity = dist_merged.groupby(['full_name', 'location']).agg({
                    'quantity': 'sum',
                    'sales_person_id': 'count'
                }).reset_index()
                
                fig = px.sunburst(productivity, 
                                path=['location', 'full_name'], 
                                values='quantity',
                                title='Salesperson Contribution by Location',
                                color='quantity',
                                color_continuous_scale='IceFire')
                st.plotly_chart(fig, use_container_width=True)
            
            # Time-based analysis
            st.markdown("### 📅 Time-Based Analysis")
            
            if not dist_df.empty:
                dist_df['day_of_week'] = dist_df['date'].dt.day_name()
                dist_df['month'] = dist_df['date'].dt.month_name()
                dist_df['week'] = dist_df['date'].dt.isocalendar().week
                
                # Sales by day of week
                daily_pattern = dist_df.groupby('day_of_week')['quantity'].sum().reindex([
                    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
                ]).reset_index()
                
                fig = px.line(daily_pattern, x='day_of_week', y='quantity',
                             title='Sales Pattern by Day of Week',
                             markers=True, line_shape='spline')
                fig.update_traces(line=dict(color='#667eea', width=3))
                st.plotly_chart(fig, use_container_width=True)
    
    with analytics_tab3:
        st.markdown("### 📁 Data Export & Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Export Sales Data", use_container_width=True, type="primary"):
                if not sales_df.empty:
                    csv_buffer = io.StringIO()
                    sales_df.to_csv(csv_buffer, index=False)
                    st.download_button(
                        label="Download Sales CSV",
                        data=csv_buffer.getvalue(),
                        file_name=f"sales_data_{date.today()}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.warning("No sales data to export")
        
        with col2:
            if st.button("📥 Export Expenses Data", use_container_width=True, type="primary"):
                if not expenses_df.empty:
                    csv_buffer = io.StringIO()
                    expenses_df.to_csv(csv_buffer, index=False)
                    st.download_button(
                        label="Download Expenses CSV",
                        data=csv_buffer.getvalue(),
                        file_name=f"expenses_data_{date.today()}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.warning("No expenses data to export")
        
        with col3:
            if st.button("📊 Generate Summary Report", use_container_width=True, type="primary"):
                # Generate a simple text report
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
                - Total Sachets Sold: {kpis['total_sachets']:,.0f}
                - Average Sale Value: KES {kpis['avg_sale_value']:,.0f}
                
                ### Performance Metrics
                - Average Daily Sales: KES {kpis['avg_daily_sales']:,.0f}
                - Best Day: {kpis['best_day'].strftime('%Y-%m-%d') if kpis['best_day'] else 'N/A'} (KES {kpis['best_day_sales']:,.0f})
                
                Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """
                
                st.download_button(
                    label="Download Report",
                    data=report,
                    file_name=f"spiseup_report_{date.today()}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        # Data cleaning and management
        st.markdown("### 🧹 Data Management")
        
        with st.expander("Data Quality Check"):
            if not sales_df.empty:
                missing_data = sales_df.isnull().sum()
                if missing_data.sum() > 0:
                    st.warning(f"Found {missing_data.sum()} missing values in sales data")
                    st.write(missing_data[missing_data > 0])
                else:
                    st.success("✅ Sales data quality check passed!")
            
            # Data statistics
            if not sales_df.empty:
                st.write("**Sales Data Statistics:**")
                st.write(f"- Total records: {len(sales_df)}")
                st.write(f"- Date range: {sales_df['Date'].min().date()} to {sales_df['Date'].max().date()}")
                st.write(f"- Unique shops: {sales_df['Name'].nunique()}")
                st.write(f"- Unique locations: {sales_df['Location'].nunique()}")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.caption(f"🌶️ SpiseUp Finance Tracker • Data range: {start_date} to {end_date}")
with col2:
    st.caption(f"📊 {len(sales_df) if not sales_df.empty else 0} sales • {len(expenses_df) if not expenses_df.empty else 0} expenses")
with col3:
    st.caption(f"🔄 Last refresh: {datetime.now().strftime('%H:%M:%S')}")