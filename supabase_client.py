from supabase import create_client, Client
import uuid
import streamlit as st

# -------------------------------
# Initialize Supabase client
# -------------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_SERVICE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------
# SALES FUNCTIONS
# -------------------------------
def save_sale(record: dict):
    """Save a sale to the SALES table"""
    if "id" not in record or not record["id"]:
        record["id"] = str(uuid.uuid4())

    sale_data = {
        "Date": record.get("Date"),
        "Name": record.get("Name") or record.get("Shop_Name"),
        "Phone": int(record.get("Phone", 0)) if record.get("Phone") else None,
        "Location": record.get("Location"),
        "Product": record.get("Product"),
        "Quantity": int(record.get("Quantity", 0)),
        "Price_per_Unit": int(record.get("Price_per_Unit", 0)),
        "Total": int(record.get("Total", 0)),
        "Payment_Status": record.get("Payment_Status"),
        "Feedback": record.get("Feedback"),
        "Follow_Up": record.get("Follow_Up"),
        "id": record.get("id")
    }

    response = supabase.table("SALES").insert(sale_data).execute()
    if response.error:
        st.error(f"Error saving sale: {response.error.message}")
        return None
    return record["id"]  # Return ID for linking to distribution

def get_sales_summary():
    """Fetch all sales from Supabase"""
    response = supabase.table("SALES").select("*").execute()
    return response.data if response.data else []

# -------------------------------
# EXPENSE FUNCTIONS
# -------------------------------
def save_expense(record: dict):
    expense_data = {
        "date": record["date"],
        "category": record["category"],
        "description": record.get("description", ""),
        "amount": record["amount"],
        "payment_method": record["payment_method"],
        "paid_by": record["paid_by"],
        "receipt": record.get("receipt", ""),
        "status": record["status"],
    }
    response = supabase.table("EXPENSES").insert(expense_data).execute()
    if response.error:
        st.error(f"Error saving expense: {response.error.message}")

def get_expenses_summary():
    """Fetch all expenses from Supabase"""
    response = supabase.table("EXPENSES").select("*").execute()
    return response.data if response.data else []

# -------------------------------
# SALESPEOPLE FUNCTIONS
# -------------------------------
def get_sales_people():
    """Fetch all salespeople"""
    response = supabase.table("SALES_PEOPLE").select("*").execute()
    return response.data if response.data else []

def save_sales_person(full_name: str, phone: str, role: str, location: str, status: str, commission_rate=None, notes=None):
    """Save a new salesperson to Supabase"""
    record = {
        "full_name": full_name.strip(),
        "phone": phone.strip(),
        "role": role.strip(),
        "location": location.strip(),
        "status": status.strip(),
        "commission_rate": commission_rate,
        "notes": notes
    }
    response = supabase.table("SALES_PEOPLE").insert(record).execute()
    if response.error:
        st.error(f"Error saving salesperson: {response.error.message}")
        return None
    return response.data[0]["id"]  # Returns the generated UUID

# -------------------------------
# DISTRIBUTION FUNCTIONS
# -------------------------------
def save_distribution(record: dict):
    """
    Save a distribution record linking a sale to a salesperson
    record = {
        'sale_id': <sale_id>,
        'sales_person_id': <sales_person_id>,
        'quantity': <sold_quantity>,
        'date': <date>,
        'price_per_unit': <price_per_unit>
    }
    """
    record["id"] = str(uuid.uuid4())
    response = supabase.table("DISTRIBUTION").insert(record).execute()
    if response.error:
        st.error(f"Error saving distribution: {response.error.message}")

def get_distribution_data(start_date=None, end_date=None):
    """
    Fetch distribution data from Supabase, optionally filtered by date range
    Returns a list of dicts
    """
    query = supabase.table("DISTRIBUTION").select("*")
    if start_date:
        query = query.gte("date", str(start_date))
    if end_date:
        query = query.lte("date", str(end_date))

    response = query.execute()

# Supabase APIResponse may have 'error' as dict or None
    error = getattr(response, "error", None)
    if error:
        st.error(f"Error fetching distribution data: {error}")
        return []

    data = getattr(response, "data", [])
    return data if data else []