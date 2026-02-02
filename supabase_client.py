import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_record(record: dict):
    """Insert a record into Supabase 'sales' table."""
    response = supabase.table("SALES").insert(record).execute()
    if not response.data:
        raise Exception("❌ Failed to insert record into Supabase.")
    return response.data


def get_all_records():
    """Fetch all records from Supabase 'sales' table."""
    response = supabase.table("SALES").select("*").order("Date", desc=True).execute()
    return response.data
