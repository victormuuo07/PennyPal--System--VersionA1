import streamlit as st
from datetime import date
from supabase_client import save_sale, save_expense, get_sales_summary, get_expenses_summary
import pandas as pd
import plotly.express as px
import uuid

st.set_page_config(page_title="🌶️ SpiseUp Finance Tracker", layout="wide")
st.title("🌶️ SpiseUp Field & Finance Tracker")
st.write("Track sales, expenses, and net profit in real-time!")

# ---------- SALES FORM ----------
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
    feedback = st.text_area("Customer Feedback")
    follow_up = st.text_input("Follow-up Action")
    submitted_sale = st.form_submit_button("💾 Save Sale")

if submitted_sale:
    total = quantity * price
    sale_record = {
        "id": str(uuid.uuid4()),
        "Date": str(sale_date),
        "Name": shop_name,
        "Phone": int(phone) if phone else None,
        "Location": location,
        "Product": product,
        "Quantity": quantity,
        "Price_per_Unit": price,
        "Total": total,
        "Feedback": feedback,
        "Follow_Up": follow_up
    }
    if save_sale(sale_record):
        st.success(f"✅ Sale saved! Total: KES {total}")

# ---------- EXPENSE FORM ----------
st.header("💸 Record an Expense")
with st.form("expense_form"):
    expense_date = st.date_input("Date", value=date.today(), key="exp_date")
    category = st.text_input("Category (e.g., Supplies, Transport)")
    description = st.text_area("Description / Details")
    amount = st.number_input("Amount (KES)", min_value=0, step=1)
    payment_method = st.selectbox("Payment Method", ["Cash", "Bank", "Mobile Payment"])
    paid_by = st.text_input("Paid By")
    receipt = st.text_input("Receipt Number / Link")
    status = st.selectbox("Status", ["Paid", "Pending"])
    submitted_expense = st.form_submit_button("💾 Save Expense")

if submitted_expense:
    expense_record = {
        "id": str(uuid.uuid4()),
        "date": str(expense_date),
        "category": category,
        "description": description,
        "amount": amount,
        "payment_method": payment_method,
        "paid_by": paid_by,
        "receipt": receipt,
        "status": status
    }
    if save_expense(expense_record):
        st.success(f"✅ Expense saved! Amount: KES {amount}")

# ---------- DASHBOARD ----------
st.header("📊 Finance Summary & Charts")

# Fetch data
sales_data = get_sales_summary()
expense_data = get_expenses_summary()

# Convert to DataFrames
sales_df = pd.DataFrame(sales_data)
expenses_df = pd.DataFrame(expense_data)

# Ensure numeric types
if not sales_df.empty:
    sales_df["Total"] = pd.to_numeric(sales_df.get("Total", pd.Series(dtype=float)))
else:
    sales_df = pd.DataFrame(columns=["Date", "Total", "Payment_Status"])

if not expenses_df.empty:
    expenses_df["amount"] = pd.to_numeric(expenses_df.get("amount", pd.Series(dtype=float)))
else:
    expenses_df = pd.DataFrame(columns=["date", "amount", "category"])

# Totals
total_sales = sales_df["Total"].sum() if not sales_df.empty else 0
total_cash = sales_df[sales_df.get("Payment_Status") == "Cash"]["Total"].sum() if not sales_df.empty else 0
total_credit = sales_df[sales_df.get("Payment_Status") != "Cash"]["Total"].sum() if not sales_df.empty else 0
total_expenses = expenses_df["amount"].sum() if not expenses_df.empty else 0
net_profit = total_sales - total_expenses

# Metrics display
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Sales (KES)", total_sales)
col2.metric("Cash Collected (KES)", total_cash)
col3.metric("Credit / Pending (KES)", total_credit)
col4.metric("Total Expenses (KES)", total_expenses)
col5.metric("Net Profit (KES)", net_profit)

# ---------- CHARTS ----------
st.subheader("📈 Visualizations")

# Sales over time
if not sales_df.empty:
    sales_over_time = sales_df.groupby("Date")["Total"].sum().reset_index()
    fig_sales = px.line(sales_over_time, x="Date", y="Total", title="Sales Over Time")
    st.plotly_chart(fig_sales, use_container_width=True)

# Expenses over time
if not expenses_df.empty:
    expenses_over_time = expenses_df.groupby("date")["amount"].sum().reset_index()
    fig_expenses = px.line(expenses_over_time, x="date", y="amount", title="Expenses Over Time", color_discrete_sequence=["red"])
    st.plotly_chart(fig_expenses, use_container_width=True)

# Net profit over time
if not sales_df.empty or not expenses_df.empty:
    combined = pd.merge(
        sales_over_time.rename(columns={"Total": "Sales"}),
        expenses_over_time.rename(columns={"amount": "Expenses"}),
        left_on="Date",
        right_on="date",
        how="outer"
    ).fillna(0)
    combined["Net_Profit"] = combined["Sales"] - combined["Expenses"]
    fig_profit = px.line(combined, x="Date", y="Net_Profit", title="Net Profit Over Time", color_discrete_sequence=["green"])
    st.plotly_chart(fig_profit, use_container_width=True)
