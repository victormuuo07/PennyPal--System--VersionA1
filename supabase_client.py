from supabase import create_client, Client
import os
import uuid
from datetime import date
import pandas as pd
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
    # Ensure ID for uniqueness
    if "id" not in record or not record["id"]:
        record["id"] = str(uuid.uuid4())

    # Map fields to match Supabase table
    sale_data = {
        "Date": record.get("Date"),
        "Name": record.get("Name") or record.get("Shop_Name"),
        "Phone": int(record.get("Phone", 0)) if record.get("Phone") else None,
        "Location": record.get("Location"),
        "Product": record.get("Product"),
        "Quantity": int(record.get("Quantity", 0)),
        "Price_per_Unit": int(record.get("Price_per_Unit", 0)),
        "Total": int(record.get("Total", 0)),
        "Feedback": record.get("Feedback"),
        "Follow_Up": record.get("Follow_Up"),
        "id": record.get("id")
    }
    supabase.table("SALES").insert(sale_data).execute()

def get_sales_summary():
    """Fetch all sales from Supabase"""
    response = supabase.table("SALES").select("*").execute()
    return response.data if response.data else []

# -------------------------------
# EXPENSE FUNCTIONS
# -------------------------------
def save_expense(record: dict):
    """Save an expense to the EXPENSES table"""
    # Ensure ID for uniqueness
    if "id" not in record or not record["id"]:
        record["id"] = str(uuid.uuid4())

    expense_data = {
        "id": record.get("id"),
        "date": record.get("Date"),
        "category": record.get("Category"),
        "description": record.get("Description") or record.get("Notes"),
        "amount": float(record.get("Amount", 0)),
        "payment_method": record.get("Payment_Method", "Cash"),
        "paid_by": record.get("Paid_By", ""),
        "receipt": record.get("Receipt", ""),
        "status": record.get("Status", "Paid")
    }
    supabase.table("EXPENSES").insert(expense_data).execute()

def get_expenses_summary():
    """Fetch all expenses from Supabase"""
    response = supabase.table("EXPENSES").select("*").execute()
    return response.data if response.data else []
