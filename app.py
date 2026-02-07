import streamlit as st
from datetime import date
import pandas as pd
import plotly.express as px
import io

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

# -------------------------------
# Streamlit page setup
# -------------------------------
st.set_page_config(page_title="🌶️ SpiseUp Finance Tracker", layout="wide")
st.title("🌶️ SpiseUp Field & Finance Tracker")
st.write("Track sales, expenses, salespeople, distribution, and net profit in real-time!")

# -------------------------------
# SALESPEOPLE MANAGEMENT
# -------------------------------
st.header("🧑‍💼 Salespeople Management")
with st.form("sales_people_form"):
    full_name = st.text_input("Full Name")
    phone = st.text_input("Phone Number")
    role = st.selectbox("Role", ["Sales Rep", "Manager", "Distributor"])
    location = st.text_input("Location")
    status = st.selectbox("Status", ["Active", "Inactive"])
    commission_rate = st.number_input("Commission Rate (%)", min_value=0.0, max_value=100.0, step=0.1, value=0.0)
    notes = st.text_area("Notes")
    
    add_sales_person = st.form_submit_button("➕ Add Salesperson")
    
    if add_sales_person:
        if not full_name.strip() or not phone.strip() or not role.strip() or not location.strip() or not status.strip():
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
                st.success(f"✅ Salesperson '{full_name}' added! ID: {sp_id}")
            else:
                st.error("❌ Failed to add salesperson. Check logs for details.")

# Fetch salespeople for dropdowns
sales_people = get_sales_people()
sales_person_options = {p['full_name']: p['id'] for p in sales_people} if sales_people else {}

# -------------------------------
# SALES FORM
# -------------------------------
st.header("💰 Record a Sale")
with st.form("sales_form"):
    sale_date = st.date_input("Date", value=date.today())
    shop_name = st.text_input("Shop / Contact Name")
    phone = st.text_input("Phone Number")
    location = st.text_input("Location")
    product = st.text_input("Product", value="SpiseUp Chilli Sachet")
    quantity = st.number_input("Quantity (sachets)", min_value=0, step=1)
    price = st.number_input("Price per sachet (KES)", min_value=0, step=1)
    payment_status = st.selectbox("Payment Status", ["Cash", "Credit / Pending"])
    sales_person_name = st.selectbox(
        "Sales Person",
        list(sales_person_options.keys()) if sales_person_options else ["N/A"]
    )
    feedback = st.text_area("Customer Feedback")
    follow_up = st.text_input("Follow-up Action")
    submitted_sale = st.form_submit_button("💾 Save Sale")

if submitted_sale:
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
    sale_id = save_sale(sale_record)

    if sales_person_options and sales_person_name != "N/A":
        distribution_record = {
            "sale_id": sale_id,
            "sales_person_id": sales_person_options[sales_person_name],
            "quantity": quantity,
            "date": str(sale_date),
            "price_per_unit": price
        }
        save_distribution(distribution_record)

    st.success(f"✅ Sale saved! Total: KES {total} by {sales_person_name}")

# -------------------------------
# EXPENSE FORM
# -------------------------------
st.header("💸 Record an Expense")
with st.form("expense_form"):
    expense_date = st.date_input("Date", value=date.today(), key="exp_date")
    category = st.text_input("Category (e.g., Supplies, Transport)")
    amount = st.number_input("Amount (KES)", min_value=0, step=1)
    description = st.text_area("Notes / Details")
    payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Mobile Money"])
    paid_by = st.text_input("Paid By")
    status = st.selectbox("Status", ["Paid", "Pending"])
    submitted_expense = st.form_submit_button("💾 Save Expense")

if submitted_expense:
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
    st.success(f"✅ Expense saved! Amount: KES {amount}")

# -------------------------------
# DASHBOARD
# -------------------------------
st.header("📊 Finance Summary & Charts")

# -------------------------------
# DATE FILTER
# -------------------------------
st.sidebar.header("📅 Filter Data")
filter_mode = st.sidebar.selectbox("Select Period", ["Custom Range", "Today", "This Week", "This Month"])
start_date = end_date = date.today()

if filter_mode == "Custom Range":
    start_date = st.sidebar.date_input("Start Date", value=date(2024,1,1))
    end_date = st.sidebar.date_input("End Date", value=date.today())
elif filter_mode == "Today":
    start_date = end_date = date.today()
elif filter_mode == "This Week":
    start_date = date.today() - pd.Timedelta(days=date.today().weekday())
    end_date = date.today()
elif filter_mode == "This Month":
    start_date = date.today().replace(day=1)
    end_date = date.today()

# -------------------------------
# FETCH & PREP DATA
# -------------------------------
sales_data = get_sales_summary()
expense_data = get_expenses_summary()
distribution_data = get_distribution_data(start_date, end_date)  # <--- UPDATED

sales_df = pd.DataFrame(sales_data) if sales_data else pd.DataFrame()
expenses_df = pd.DataFrame(expense_data) if expense_data else pd.DataFrame()
dist_df = pd.DataFrame(distribution_data) if distribution_data else pd.DataFrame()
sp_df = pd.DataFrame(sales_people) if sales_people else pd.DataFrame()

# Date filtering
if not sales_df.empty:
    sales_df['Date'] = pd.to_datetime(sales_df['Date'])
    sales_df = sales_df[(sales_df['Date'] >= pd.to_datetime(start_date)) & (sales_df['Date'] <= pd.to_datetime(end_date))]
if not expenses_df.empty:
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    expenses_df = expenses_df[(expenses_df['date'] >= pd.to_datetime(start_date)) & (expenses_df['date'] <= pd.to_datetime(end_date))]
if not dist_df.empty:
    dist_df['date'] = pd.to_datetime(dist_df['date'])
    dist_df = dist_df[(dist_df['date'] >= pd.to_datetime(start_date)) & (dist_df['date'] <= pd.to_datetime(end_date))]

# Convert numeric safely
sales_df['Total'] = pd.to_numeric(sales_df['Total'], errors='coerce').fillna(0)
expenses_df['amount'] = pd.to_numeric(expenses_df['amount'], errors='coerce').fillna(0)

# -------------------------------
# FINANCE METRICS
# -------------------------------
total_sales = sales_df['Total'].sum()
total_cash = sales_df[sales_df['Payment_Status'] == "Cash"]['Total'].sum()
total_credit = sales_df[sales_df['Payment_Status'] != "Cash"]['Total'].sum()
total_expenses = expenses_df['amount'].sum()
net_profit = total_sales - total_expenses
running_balance = total_cash - total_expenses

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Sales (KES)", total_sales)
col2.metric("Cash Collected (KES)", total_cash)
col3.metric("Credit / Pending (KES)", total_credit)
col4.metric("Total Expenses (KES)", total_expenses)
col5.metric("Net Profit (KES)", net_profit)
col6.metric("Running Cash Balance (KES)", running_balance)

# -------------------------------
# VISUALIZATIONS
# -------------------------------
st.subheader("📈 Sales, Expenses & Profit Over Time")
if not sales_df.empty:
    sales_over_time = sales_df.groupby("Date")['Total'].sum().reset_index()
    st.plotly_chart(px.line(sales_over_time, x='Date', y='Total', title="Total Sales Over Time"), use_container_width=True)
if not expenses_df.empty:
    expenses_over_time = expenses_df.groupby("date")['amount'].sum().reset_index()
    st.plotly_chart(px.line(expenses_over_time, x='date', y='amount', title="Total Expenses Over Time", color_discrete_sequence=["red"]), use_container_width=True)
if not sales_df.empty or not expenses_df.empty:
    combined_df = pd.merge(
        sales_df.groupby("Date")['Total'].sum().reset_index().rename(columns={"Total":"Sales"}),
        expenses_df.groupby("date")['amount'].sum().reset_index().rename(columns={"amount":"Expenses", "date":"Date"}),
        on="Date", how="outer"
    ).fillna(0)
    combined_df['Net_Profit'] = combined_df['Sales'] - combined_df['Expenses']
    st.plotly_chart(px.line(combined_df, x='Date', y='Net_Profit', title="Net Profit Over Time", color_discrete_sequence=["green"]), use_container_width=True)

# -------------------------------
# SALESPEOPLE LEADERBOARD
# -------------------------------
st.header("🏆 Salespeople Performance")
if not dist_df.empty and not sp_df.empty:
    dist_merged = dist_df.merge(sp_df, left_on="sales_person_id", right_on="id")
    dist_merged['Total_Value'] = dist_merged['quantity'] * dist_merged['price_per_unit']

    # Top 10 by Total Value
    sp_summary_value = dist_merged.groupby("full_name")['Total_Value'].sum().reset_index().sort_values("Total_Value", ascending=False).head(10)
    st.subheader("Top 10 by Total Sales Value")
    st.dataframe(sp_summary_value)
    st.plotly_chart(px.bar(sp_summary_value, x="full_name", y="Total_Value", title="Top 10 Salespeople by Total Value"), use_container_width=True)

    # Top 10 by Quantity Sold
    sp_summary_qty = dist_merged.groupby("full_name")['quantity'].sum().reset_index().sort_values("quantity", ascending=False).head(10)
    st.subheader("Top 10 by Quantity Sold")
    st.dataframe(sp_summary_qty)
    st.plotly_chart(px.bar(sp_summary_qty, x="full_name", y="quantity", title="Top 10 Salespeople by Quantity Sold", color="full_name"), use_container_width=True)

# -------------------------------
# SHOP & DISTRIBUTION LEADERBOARD
# -------------------------------
st.header("🏪 Shop & Distribution Performance")
if not dist_df.empty and not sales_df.empty and not sp_df.empty:
    merged_shop = dist_df.merge(sales_df, left_on="sale_id", right_on="id")
    merged_shop = merged_shop.merge(sp_df, left_on="sales_person_id", right_on="id")

    shop_summary = merged_shop.groupby("Name").agg(
        total_quantity=pd.NamedAgg(column="quantity", aggfunc="sum"),
        total_value=pd.NamedAgg(column="price_per_unit", aggfunc=lambda x: (merged_shop.loc[x.index,'quantity']*x).sum())
    ).reset_index().sort_values("total_value", ascending=False).head(10)

    st.subheader("Top 10 Shops by Revenue")
    st.dataframe(shop_summary)
    st.plotly_chart(px.bar(shop_summary, x="Name", y="total_value", title="Top 10 Shops by Revenue"), use_container_width=True)

    st.subheader("Top 10 Shops by Quantity Sold")
    st.plotly_chart(px.bar(shop_summary, x="Name", y="total_quantity", title="Top 10 Shops by Quantity Sold"), use_container_width=True)

    # Shop distribution by salesperson
    dist_shop_sp = merged_shop.groupby(["Name","full_name"])['quantity'].sum().reset_index().sort_values("quantity", ascending=False)
    st.subheader("Shop Sales Distribution by Salesperson")
    st.dataframe(dist_shop_sp)
    st.plotly_chart(px.bar(dist_shop_sp, x="Name", y="quantity", color="full_name", title="Shop Distribution by Salesperson"), use_container_width=True)

# -------------------------------
# EXPENSES BY CATEGORY
# -------------------------------
st.subheader("💼 Expenses by Category")
if not expenses_df.empty:
    category_summary = expenses_df.groupby("category")['amount'].sum().reset_index()
    st.plotly_chart(px.pie(category_summary, names="category", values="amount", title="Expenses by Category"), use_container_width=True)

# -------------------------------
# EXPORT DATA
# -------------------------------
st.subheader("📁 Export Data")
if st.button("Export Sales to CSV"):
    csv_buffer = io.StringIO()
    sales_df.to_csv(csv_buffer, index=False)
    st.download_button("Download Sales CSV", csv_buffer.getvalue(), "sales_data.csv", "text/csv")
if st.button("Export Expenses to CSV"):
    csv_buffer = io.StringIO()
    expenses_df.to_csv(csv_buffer, index=False)
    st.download_button("Download Expenses CSV", csv_buffer.getvalue(), "expenses_data.csv", "text/csv")