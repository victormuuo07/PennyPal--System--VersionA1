import streamlit as st
from datetime import date
from supabase_client import save_sale, save_expense, get_sales_summary, get_expenses_summary
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="🌶️ SpiseUp Finance Tracker", layout="wide")
st.title("🌶️ SpiseUp Field & Finance Tracker")
st.write("Track sales, expenses, and net profit in real-time with analytics and CSV export!")

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
    save_sale(sale_record)
    st.success(f"✅ Sale saved! Total: KES {total}")

# ---------- EXPENSE FORM ----------
st.header("💸 Record an Expense")
with st.form("expense_form"):
    expense_date = st.date_input("Date", value=date.today(), key="exp_date")
    category = st.text_input("Category (e.g., Supplies, Transport)")
    amount = st.number_input("Amount (KES)", min_value=0, step=1)
    notes = st.text_area("Notes / Details")
    payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Mobile Money"])
    paid_by = st.text_input("Paid By")
    status = st.selectbox("Status", ["Paid", "Pending"])
    submitted_expense = st.form_submit_button("💾 Save Expense")

if submitted_expense:
    expense_record = {
        "Date": str(expense_date),
        "Category": category,
        "Amount": amount,
        "Description": notes,
        "Payment_Method": payment_method,
        "Paid_By": paid_by,
        "Receipt": "",
        "Status": status
    }
    save_expense(expense_record)
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
    sales_df['Total'] = pd.to_numeric(sales_df['Total'])
else:
    sales_df = pd.DataFrame(columns=["Date", "Total", "Payment_Status"])

if not expenses_df.empty:
    expenses_df['Amount'] = pd.to_numeric(expenses_df['Amount'])
else:
    expenses_df = pd.DataFrame(columns=["Date", "Amount", "Category"])

# Totals
total_sales = sales_df['Total'].sum() if not sales_df.empty else 0
total_cash = sales_df[sales_df['Payment_Status'] == "Cash"]['Total'].sum() if not sales_df.empty else 0
total_credit = sales_df[sales_df['Payment_Status'] != "Cash"]['Total'].sum() if not sales_df.empty else 0
total_expenses = expenses_df['Amount'].sum() if not expenses_df.empty else 0
net_profit = total_sales - total_expenses
running_balance = total_cash - total_expenses

# Metrics display
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Sales (KES)", total_sales)
col2.metric("Cash Collected (KES)", total_cash)
col3.metric("Credit / Pending (KES)", total_credit)
col4.metric("Total Expenses (KES)", total_expenses)
col5.metric("Net Profit (KES)", net_profit)
col6.metric("Running Cash Balance (KES)", running_balance)

# ---------- CHARTS ----------
st.subheader("📈 Visualizations")

# Sales over time
if not sales_df.empty:
    sales_df_grouped = sales_df.groupby("Date")['Total'].sum().reset_index()
else:
    sales_df_grouped = pd.DataFrame(columns=["Date", "Total"])
    
fig_sales = px.line(sales_df_grouped, x='Date', y='Total', title="Total Sales Over Time") if not sales_df_grouped.empty else None
if fig_sales:
    st.plotly_chart(fig_sales, use_container_width=True)

# Expenses over time
if not expenses_df.empty:
    expenses_df_grouped = expenses_df.groupby("Date")['Amount'].sum().reset_index()
else:
    expenses_df_grouped = pd.DataFrame(columns=["Date", "Amount"])

fig_expenses = px.line(expenses_df_grouped, x='Date', y='Amount', title="Total Expenses Over Time", color_discrete_sequence=["red"]) if not expenses_df_grouped.empty else None
if fig_expenses:
    st.plotly_chart(fig_expenses, use_container_width=True)

# Net profit over time
combined_df = pd.merge(
    sales_df_grouped.rename(columns={"Total": "Sales"}),
    expenses_df_grouped.rename(columns={"Amount": "Expenses"}),
    on="Date",
    how="outer"
).fillna(0)

if not combined_df.empty:
    combined_df['Net_Profit'] = combined_df['Sales'] - combined_df['Expenses']
    fig_profit = px.line(combined_df, x='Date', y='Net_Profit', title="Net Profit Over Time", color_discrete_sequence=["green"])
    st.plotly_chart(fig_profit, use_container_width=True)

# ---------- OVERDUE / CREDIT SALES ----------
if not sales_df.empty:
    st.subheader("⚠️ Credit / Pending Sales")
    pending_sales = sales_df[sales_df['Payment_Status'] != "Cash"]
    if not pending_sales.empty:
        st.dataframe(pending_sales)
    else:
        st.info("No pending credit sales!")

# ---------- EXPENSES BY CATEGORY ----------
if not expenses_df.empty:
    st.subheader("💼 Expenses by Category")
    category_summary = expenses_df.groupby("Category")['Amount'].sum().reset_index()
    fig_category = px.pie(category_summary, names="Category", values="Amount", title="Expenses by Category")
    st.plotly_chart(fig_category, use_container_width=True)

# ---------- EXPORT DATA ----------
st.subheader("📁 Export Data")
if st.button("Export Sales to CSV"):
    csv_buffer = io.StringIO()
    sales_df.to_csv(csv_buffer, index=False)
    st.download_button("Download Sales CSV", csv_buffer.getvalue(), "sales_data.csv", "text/csv")

if st.button("Export Expenses to CSV"):
    csv_buffer = io.StringIO()
    expenses_df.to_csv(csv_buffer, index=False)
    st.download_button("Download Expenses CSV", csv_buffer.getvalue(), "expenses_data.csv", "text/csv")
