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
def save_distribution(sale_id: str, sales_person_id: str, quantity: int, sale_date: str, price: float, sale_data: dict = None):
    """Save a distribution record linking a sale to a salesperson"""
    try:
        distribution_record = {
            "id": str(uuid.uuid4()),
            "date": sale_date,
            "sales_person_id": sales_person_id,
            "sale_id": sale_id,  # NEW: Link to sale
            "distributor_type": "Sales Rep",
            "location": sale_data.get("Location", "") if sale_data else "",
            "product": sale_data.get("Product", "SpiseUp Chilli Sachet") if sale_data else "SpiseUp Chilli Sachet",
            "quantity_distributed": quantity,
            "unit_price": price,
            "expected_amount": quantity * price,
            "distribution_type": "Direct Sale",
            "status": "Completed",
            "notes": f"Auto-linked to sale {sale_id}"
        }
        
        response = supabase.table("DISTRIBUTION").insert(distribution_record).execute()
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

# -------------------------------
# PRODUCTION & INVENTORY FUNCTIONS
# -------------------------------

def save_batch(batch_data: dict):
    """Save a production batch"""
    try:
        batch_data["id"] = str(uuid.uuid4())
        response = supabase.table("BATCHES").insert(batch_data).execute()
        if hasattr(response, 'error') and response.error:
            st.error(f"Error saving batch: {response.error.message}")
            return None
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        st.error(f"Error saving batch: {str(e)}")
        return None

def get_batches():
    """Get all production batches"""
    try:
        response = supabase.table("BATCHES").select("*").order("production_date", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching batches: {str(e)}")
        return []

def save_production_output(output_data: dict):
    """Save finished goods from batch"""
    try:
        output_data["id"] = str(uuid.uuid4())
        response = supabase.table("PRODUCTION_OUTPUT").insert(output_data).execute()
        return True
    except Exception as e:
        st.error(f"Error saving production output: {str(e)}")
        return False

def get_raw_materials():
    """Get current raw materials inventory"""
    try:
        response = supabase.table("RAW_MATERIALS_INVENTORY").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching raw materials: {str(e)}")
        return []

def save_restock(restock_data: dict):
    """Save restock record and update inventory"""
    try:
        restock_data["id"] = str(uuid.uuid4())
        response = supabase.table("STOCK_RESTOCK").insert(restock_data).execute()
        
        # Update inventory
        material = restock_data["material_name"]
        quantity = restock_data["quantity_kg"]
        
        # Get current stock
        inv_response = supabase.table("RAW_MATERIALS_INVENTORY").select("*").eq("material_name", material).execute()
        if inv_response.data:
            current = inv_response.data[0]["current_stock_kg"]
            new_stock = current + quantity
            supabase.table("RAW_MATERIALS_INVENTORY").update({
                "current_stock_kg": new_stock, 
                "last_restock_date": str(date.today())
            }).eq("material_name", material).execute()
        
        return True
    except Exception as e:
        st.error(f"Error saving restock: {str(e)}")
        return False

def get_finished_goods():
    """Get finished goods inventory"""
    try:
        response = supabase.table("FINISHED_GOODS_INVENTORY").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching finished goods: {str(e)}")
        return []

def update_raw_material_stock(material_name: str, quantity_used_kg: float):
    """Update raw material stock after production"""
    try:
        response = supabase.table("RAW_MATERIALS_INVENTORY").select("*").eq("material_name", material_name).execute()
        if response.data:
            current_stock = response.data[0]["current_stock_kg"]
            new_stock = current_stock - quantity_used_kg
            supabase.table("RAW_MATERIALS_INVENTORY").update({"current_stock_kg": new_stock}).eq("material_name", material_name).execute()
        return True
    except Exception as e:
        st.error(f"Error updating stock: {str(e)}")
        return False

def update_finished_goods(product_type: str, quantity_sold: int):
    """Update finished goods stock after sale"""
    try:
        response = supabase.table("FINISHED_GOODS_INVENTORY").select("*").eq("product_type", product_type).execute()
        if response.data:
            current = response.data[0]["current_stock"]
            new_stock = current - quantity_sold
            supabase.table("FINISHED_GOODS_INVENTORY").update({
                "current_stock": new_stock, 
                "last_updated": str(datetime.now())
            }).eq("product_type", product_type).execute()
        return True
    except Exception as e:
        st.error(f"Error updating finished goods: {str(e)}")
        return False

# -------------------------------
# FUNDING/CAPITAL FUNCTIONS
# -------------------------------

def save_funding(funding_data: dict):
    """Save a funding record"""
    try:
        funding_data["id"] = str(uuid.uuid4())
        response = supabase.table("FUNDING").insert(funding_data).execute()
        if hasattr(response, 'error') and response.error:
            st.error(f"Error saving funding: {response.error.message}")
            return None
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        st.error(f"Error saving funding: {str(e)}")
        return None

def get_funding():
    """Get all funding records"""
    try:
        response = supabase.table("FUNDING").select("*").order("funding_date", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching funding: {str(e)}")
        return []

def get_total_funding():
    """Get total funding amount"""
    try:
        response = supabase.table("FUNDING").select("amount").execute()
        total = sum([r["amount"] for r in response.data]) if response.data else 0
        return total
    except Exception as e:
        st.error(f"Error calculating total funding: {str(e)}")
        return 0

def update_funding(funding_id: str, updates: dict):
    """Update a funding record"""
    try:
        response = supabase.table("FUNDING").update(updates).eq("id", funding_id).execute()
        return True
    except Exception as e:
        st.error(f"Error updating funding: {str(e)}")
        return False

def delete_funding(funding_id: str):
    """Delete a funding record"""
    try:
        response = supabase.table("FUNDING").delete().eq("id", funding_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting funding: {str(e)}")
        return False

# -------------------------------
# ADVANCED INVENTORY TRACKING FUNCTIONS
# -------------------------------

def get_material_balance(material_name: str):
    """Calculate current stock based on all transactions"""
    try:
        response = supabase.table("INVENTORY_TRANSACTIONS").select("*").eq("material_name", material_name).execute()
        if response.data:
            balance = 0
            for trans in response.data:
                if trans['transaction_type'] == 'RESTOCK':
                    balance += trans['quantity_kg']
                elif trans['transaction_type'] == 'USAGE':
                    balance -= abs(trans['quantity_kg'])
            return balance
        return 0
    except Exception as e:
        print(f"Error calculating balance: {str(e)}")
        return 0

def record_restock_with_transaction(material_name: str, quantity_kg: float, cost_per_kg: float, supplier: str, notes: str = ""):
    """Record a restock with transaction tracking"""
    try:
        restock_id = str(uuid.uuid4())
        today = str(date.today())
        
        # Record in STOCK_RESTOCK table
        restock_data = {
            "id": restock_id,
            "material_name": material_name,
            "quantity_kg": quantity_kg,
            "cost_per_kg": cost_per_kg,
            "total_cost": quantity_kg * cost_per_kg,
            "supplier": supplier,
            "restock_date": today,
            "notes": notes
        }
        supabase.table("STOCK_RESTOCK").insert(restock_data).execute()
        
        # Record transaction
        transaction_data = {
            "id": str(uuid.uuid4()),
            "transaction_date": today,
            "transaction_type": "RESTOCK",
            "material_name": material_name,
            "quantity_kg": quantity_kg,
            "cost_per_kg": cost_per_kg,
            "total_value": quantity_kg * cost_per_kg,
            "reference_id": restock_id,
            "notes": f"Restocked from {supplier}. {notes}"
        }
        supabase.table("INVENTORY_TRANSACTIONS").insert(transaction_data).execute()
        
        # Update raw materials inventory
        inv_response = supabase.table("RAW_MATERIALS_INVENTORY").select("*").eq("material_name", material_name).execute()
        if inv_response.data:
            current = inv_response.data[0]["current_stock_kg"]
            new_stock = current + quantity_kg
            supabase.table("RAW_MATERIALS_INVENTORY").update({
                "current_stock_kg": new_stock,
                "last_restock_date": today
            }).eq("material_name", material_name).execute()
        
        return True
    except Exception as e:
        print(f"Error recording restock: {str(e)}")
        return False

def record_material_usage(batch_id: str, material_name: str, quantity_used_kg: float, cost_per_kg: float):
    """Record material usage in a batch"""
    try:
        # Record in MATERIAL_USAGE table
        usage_data = {
            "id": str(uuid.uuid4()),
            "batch_id": batch_id,
            "material_name": material_name,
            "quantity_used_kg": quantity_used_kg,
            "cost_per_kg": cost_per_kg,
            "total_cost": quantity_used_kg * cost_per_kg
        }
        supabase.table("MATERIAL_USAGE").insert(usage_data).execute()
        
        # Record transaction
        transaction_data = {
            "id": str(uuid.uuid4()),
            "transaction_date": str(date.today()),
            "transaction_type": "USAGE",
            "material_name": material_name,
            "quantity_kg": -quantity_used_kg,  # Negative for usage
            "cost_per_kg": cost_per_kg,
            "total_value": -(quantity_used_kg * cost_per_kg),
            "reference_id": batch_id,
            "notes": f"Used in batch {batch_id}"
        }
        supabase.table("INVENTORY_TRANSACTIONS").insert(transaction_data).execute()
        
        # Update raw materials inventory
        inv_response = supabase.table("RAW_MATERIALS_INVENTORY").select("*").eq("material_name", material_name).execute()
        if inv_response.data:
            current = inv_response.data[0]["current_stock_kg"]
            new_stock = current - quantity_used_kg
            supabase.table("RAW_MATERIALS_INVENTORY").update({"current_stock_kg": new_stock}).eq("material_name", material_name).execute()
        
        return True
    except Exception as e:
        print(f"Error recording usage: {str(e)}")
        return False

def get_inventory_transactions(material_name: str = None, start_date=None, end_date=None):
    """Get inventory transactions with filters"""
    try:
        query = supabase.table("INVENTORY_TRANSACTIONS").select("*").order("transaction_date", desc=True)
        if material_name:
            query = query.eq("material_name", material_name)
        if start_date:
            query = query.gte("transaction_date", str(start_date))
        if end_date:
            query = query.lte("transaction_date", str(end_date))
        
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching transactions: {str(e)}")
        return []

def get_material_usage_summary(batch_id: str = None):
    """Get summary of material usage for a batch"""
    try:
        if batch_id:
            response = supabase.table("MATERIAL_USAGE").select("*").eq("batch_id", batch_id).execute()
        else:
            response = supabase.table("MATERIAL_USAGE").select("*").execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            summary = df.groupby('material_name').agg({
                'quantity_used_kg': 'sum',
                'total_cost': 'sum'
            }).reset_index()
            summary.columns = ['Material', 'Quantity Used (KG)', 'Total Cost (KES)']
            return summary
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching usage summary: {str(e)}")
        return pd.DataFrame()

def get_all_material_usage():
    """Get all material usage across all batches"""
    try:
        response = supabase.table("MATERIAL_USAGE").select("*, BATCHES(batch_number, production_date)").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching all usage: {str(e)}")
        return pd.DataFrame()