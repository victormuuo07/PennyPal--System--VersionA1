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
    """Save a sale to the SALES table - returns sale_id if successful, None if failed"""
    try:
        if "id" not in record or not record["id"]:
            record["id"] = str(uuid.uuid4())

        sale_data = {
            "id": record.get("id"),
            "Date": record.get("Date"),
            "Name": record.get("Name") or record.get("Shop_Name"),
            "Phone": record.get("Phone"),
            "Location": record.get("Location"),
            "Product": record.get("Product"),
            "Quantity": int(record.get("Quantity", 0)),
            "Price_per_Unit": int(record.get("Price_per_Unit", 0)),
            "Total": int(record.get("Total", 0)),
            "Payment_Status": record.get("Payment_Status"),
            "Feedback": record.get("Feedback", ""),
            "Follow_Up": record.get("Follow_Up", "")
        }

        response = supabase.table("SALES").insert(sale_data).execute()
        
        if hasattr(response, 'error') and response.error:
            st.error(f"Database error saving sale: {response.error.message}")
            return None
            
        if hasattr(response, 'data') and response.data and len(response.data) > 0:
            return response.data[0].get('id', record["id"])
        else:
            return record["id"]
            
    except Exception as e:
        st.error(f"Error saving sale: {str(e)}")
        return None

def save_distribution(record: dict):
    """Save a distribution record linking a sale to a salesperson - returns True if successful"""
    try:
        if "id" not in record or not record["id"]:
            record["id"] = str(uuid.uuid4())
        
        # Ensure all required fields are present
        required_fields = ["sale_id", "sales_person_id", "quantity", "date", "price_per_unit"]
        missing_fields = [field for field in required_fields if field not in record]
        
        if missing_fields:
            st.error(f"Missing required fields for distribution: {', '.join(missing_fields)}")
            return False
        
        response = supabase.table("DISTRIBUTION").insert(record).execute()
        
        if hasattr(response, 'error') and response.error:
            st.error(f"Database error saving distribution: {response.error.message}")
            return False
            
        return True
        
    except Exception as e:
        st.error(f"Error saving distribution: {str(e)}")
        return False

def get_sales_summary():
    """Fetch all sales from Supabase"""
    response = supabase.table("SALES").select("*").execute()
    error = getattr(response, "error", None)
    if error:
        st.error(f"Error fetching sales: {error}")
        return []
    return getattr(response, "data", []) or []

# -------------------------------
# EXPENSE FUNCTIONS
# -------------------------------
def save_expense(record: dict):
    """Save an expense to the EXPENSES table"""
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
    error = getattr(response, "error", None)
    if error:
        st.error(f"Error saving expense: {error}")

def get_expenses_summary():
    """Fetch all expenses from Supabase"""
    response = supabase.table("EXPENSES").select("*").execute()
    error = getattr(response, "error", None)
    if error:
        st.error(f"Error fetching expenses: {error}")
        return []
    return getattr(response, "data", []) or []

# -------------------------------
# SALESPEOPLE FUNCTIONS
# -------------------------------
def get_sales_people():
    """Fetch all salespeople"""
    response = supabase.table("SALES_PEOPLE").select("*").execute()
    error = getattr(response, "error", None)
    if error:
        st.error(f"Error fetching salespeople: {error}")
        return []
    return getattr(response, "data", []) or []

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
    error = getattr(response, "error", None)
    if error:
        st.error(f"Error saving salesperson: {error}")
        return None

    data = getattr(response, "data", [])
    return data[0]["id"] if data else None

# -------------------------------
# DISTRIBUTION FUNCTIONS
# -------------------------------
def save_distribution(record: dict):
    """Save a distribution record linking a sale to a salesperson"""
    try:
        if "id" not in record or not record["id"]:
            record["id"] = str(uuid.uuid4())
        
        # Ensure all required fields are present
        required_fields = ["sale_id", "sales_person_id", "quantity", "date"]
        for field in required_fields:
            if field not in record:
                st.error(f"Missing required field for distribution: {field}")
                return False
        
        response = supabase.table("DISTRIBUTION").insert(record).execute()
        error = getattr(response, "error", None)
        if error:
            st.error(f"Error saving distribution: {error.message}")
            return False
        
        return True
        
    except Exception as e:
        st.error(f"Exception while saving distribution: {str(e)}")
        return False

def get_distribution_data(start_date=None, end_date=None):
    """Fetch distribution records with optional date filtering"""
    query = supabase.table("DISTRIBUTION").select("*")
    if start_date:
        query = query.gte("date", str(start_date))
    if end_date:
        query = query.lte("date", str(end_date))

    response = query.execute()
    error = getattr(response, "error", None)
    if error:
        st.error(f"Error fetching distribution data: {error}")
        return []

    return getattr(response, "data", []) or []