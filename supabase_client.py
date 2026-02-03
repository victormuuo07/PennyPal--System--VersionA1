import os
import uuid
from supabase import create_client, Client
from datetime import datetime

# ---------------- SECRETS / ENV ----------------
SUPABASE_URL = os.environ.get("SUPABASE_URL") or st.secrets["SUPABASE_URL"]
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or st.secrets["SUPABASE_SERVICE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- SALES FUNCTIONS ----------------
def save_sale(record: dict) -> bool:
    """
    Save a sale record to the SALES table
    """
    if "id" not in record:
        record["id"] = str(uuid.uuid4())
    try:
        response = supabase.table("SALES").insert(record).execute()
        if response.status_code in [200, 201]:
            return True
        else:
            print("Error saving sale:", response.data)
            return False
    except Exception as e:
        print("Exception saving sale:", e)
        return False

def get_sales_summary() -> list:
    """
    Fetch all sales from the SALES table
    """
    try:
        response = supabase.table("SALES").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        print("Exception fetching sales:", e)
        return []

# ---------------- EXPENSES FUNCTIONS ----------------
def save_expense(record: dict) -> bool:
    """
    Save an expense record to the EXPENSES table
    """
    if "id" not in record:
        record["id"] = str(uuid.uuid4())
    if "status" not in record:
        record["status"] = "Paid"  # default
    try:
        response = supabase.table("EXPENSES").insert(record).execute()
        if response.status_code in [200, 201]:
            return True
        else:
            print("Error saving expense:", response.data)
            return False
    except Exception as e:
        print("Exception saving expense:", e)
        return False

def get_expenses_summary() -> list:
    """
    Fetch all expenses from the EXPENSES table
    """
    try:
        response = supabase.table("EXPENSES").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        print("Exception fetching expenses:", e)
        return []
