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
def save_expense(record):
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

    supabase.table("EXPENSES").insert(expense_data).execute()

def get_expenses_summary():
    """Fetch all expenses from Supabase"""
    response = supabase.table("EXPENSES").select("*").execute()
    return response.data if response.data else []
