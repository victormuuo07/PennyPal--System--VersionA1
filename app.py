import streamlit as st
from validator import validate_record
from supabase_client import save_record, get_all_records
from datetime import date

st.set_page_config(page_title="🌶️ SpiseUp Field Bookkeeper", layout="centered")
st.title("🌶️ SpiseUp Field Bookkeeper (Supabase Live)")

st.write("Fill the form after visiting a shop. Data will be saved live to Supabase.")

# ----- FORM -----
with st.form("sales_form"):
    sale_date = st.date_input("Date", value=date.today())
    name = st.text_input("Shop / Contact Name")
    phone = st.text_input("Phone Number")
    location = st.text_input("Location")
    product = st.text_input("Product", value="SpiseUp Chilli Sachet")
    quantity = st.number_input("Quantity (sachets)", min_value=0, step=1)
    price = st.number_input("Price per sachet (KES)", min_value=0, step=1)
    feedback = st.text_area("Customer Feedback")
    follow_up = st.text_input("Follow-up Action")

    submitted = st.form_submit_button("💾 Save Record")

# ----- HANDLE FORM SUBMISSION -----
if submitted:
    total = quantity * price
    record = {
        "Date": str(sale_date),
        "Name": name,
        "Phone": phone,
        "Location": location,
        "Product": product,
        "Quantity": quantity,
        "Price_per_Unit": price,
        "Total": total,
        "Feedback": feedback,
        "Follow_Up": follow_up
    }

    missing = validate_record(record)
    if missing:
        st.warning(f"❗ Missing fields: {', '.join(missing)}")
    else:
        try:
            save_record(record)
            st.success("✅ Record saved live to Supabase!")
            st.json(record)
        except Exception as e:
            st.error(f"❌ Error saving record: {e}")

# ----- SHOW LIVE TABLE -----
st.subheader("📊 All Sales Records")
records = get_all_records()
if records:
    st.dataframe(records)
else:
    st.info("No records yet.")
