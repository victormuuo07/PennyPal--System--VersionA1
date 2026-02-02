# supabase_client.py
from supabase import create_client, Client
import streamlit as st

# Get secrets from Streamlit
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_SERVICE_KEY"]

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL or Key not set! Check Streamlit secrets.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_record(record: dict):
    """Insert a record into the Supabase 'SALES' table."""
    response = supabase.table("SALES").insert(record).execute()
    if response.data:
        return True
    else:
        raise Exception(f"Failed to insert record: {response}")

def get_all_records():
    """Fetch all records from Supabase 'SALES' table."""
    response = supabase.table("SALES").select("*").execute()
    if response.data:
        return response.data
    return []
