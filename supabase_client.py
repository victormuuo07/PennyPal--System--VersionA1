from supabase import create_client, Client
import uuid
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import requests 


# -------------------------------
# Initialize Supabase client
# -------------------------------
def get_supabase_client():
    """Get Supabase client with retry logic and timeout"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            SUPABASE_URL = st.secrets["SUPABASE_URL"]
            SUPABASE_KEY = st.secrets["SUPABASE_SERVICE_KEY"]
            
            client = create_client(SUPABASE_URL, SUPABASE_KEY)
            
            # Test connection
            test_response = client.table("SALES").select("*").limit(1).execute()
            return client
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                st.error(f"❌ Failed to connect to Supabase after {max_retries} attempts")
                st.error(f"Error: {str(e)}")
                st.info("💡 Check your internet connection and Supabase credentials")
                st.stop()

# Initialize client
supabase = get_supabase_client()
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

def update_finished_goods_production(product_type: str, quantity_produced: int):
    """Increase finished goods stock when production is made"""
    try:
        response = supabase.table("FINISHED_GOODS_INVENTORY")\
            .select("*")\
            .eq("product_type", product_type)\
            .execute()
        
        if response.data:
            current = response.data[0]
            new_stock = current.get('current_stock', 0) + quantity_produced
            new_produced = current.get('total_produced', 0) + quantity_produced
            
            supabase.table("FINISHED_GOODS_INVENTORY").update({
                "current_stock": new_stock,
                "total_produced": new_produced,
                "last_updated": datetime.now().isoformat()
            }).eq("product_type", product_type).execute()
        else:
            # Get price based on product type
            prices = {"Sachet 5": 5, "Sachet 30": 30, "Bottle 100g": 150, "Refill 120g": 120}
            reorder = {"Sachet 5": 500, "Sachet 30": 200, "Bottle 100g": 100, "Refill 120g": 50}
            
            supabase.table("FINISHED_GOODS_INVENTORY").insert({
                "product_type": product_type,
                "current_stock": quantity_produced,
                "total_produced": quantity_produced,
                "total_sold": 0,
                "unit_price": prices.get(product_type, 0),
                "reorder_level": reorder.get(product_type, 100)
            }).execute()
        
        return True
    except Exception as e:
        print(f"Error updating finished goods: {str(e)}")
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
    
# -------------------------------
# COMPLETE INVENTORY TRACKING SYSTEM (FIXED)
# -------------------------------

def record_restock_with_balance(material_name: str, quantity_kg: float, cost_per_kg: float, supplier: str, restock_date, notes: str = ""):
    """Record a restock and update inventory balance"""
    try:
        from datetime import date
        
        # Convert date if needed
        if isinstance(restock_date, str):
            restock_date_str = restock_date
        else:
            restock_date_str = restock_date.strftime('%Y-%m-%d')
        
        restock_id = str(uuid.uuid4())
        
        # 1. Record restock in STOCK_RESTOCK table
        restock_data = {
            "id": restock_id,
            "material_name": material_name,
            "quantity_kg": quantity_kg,
            "cost_per_kg": cost_per_kg,
            "total_cost": quantity_kg * cost_per_kg,
            "supplier": supplier,
            "restock_date": restock_date_str,
            "remaining_kg": quantity_kg,  # Initially full
            "notes": notes
        }
        supabase.table("STOCK_RESTOCK").insert(restock_data).execute()
        
        # 2. Update RAW_MATERIALS_INVENTORY
        # Get current inventory
        inv_response = supabase.table("RAW_MATERIALS_INVENTORY").select("*").eq("material_name", material_name).execute()
        
        if inv_response.data:
            current = inv_response.data[0]
            new_purchased = current.get('total_purchased_kg', 0) + quantity_kg
            new_stock = current.get('current_stock_kg', 0) + quantity_kg
            
            supabase.table("RAW_MATERIALS_INVENTORY").update({
                "total_purchased_kg": new_purchased,
                "current_stock_kg": new_stock,
                "last_restock_date": restock_date_str
            }).eq("material_name", material_name).execute()
        else:
            # Create if doesn't exist
            supabase.table("RAW_MATERIALS_INVENTORY").insert({
                "material_name": material_name,
                "total_purchased_kg": quantity_kg,
                "current_stock_kg": quantity_kg,
                "unit_cost": cost_per_kg,
                "reorder_level": 10,
                "last_restock_date": restock_date_str
            }).execute()
        
        # 3. Record in INVENTORY_BALANCE
        current_balance = get_current_material_balance(material_name)
        new_balance = current_balance + quantity_kg
        
        balance_data = {
            "id": str(uuid.uuid4()),
            "material_name": material_name,
            "transaction_date": restock_date_str,
            "transaction_type": "RESTOCK",
            "quantity_kg": quantity_kg,
            "running_balance_kg": new_balance,
            "reference_id": restock_id,
            "notes": f"Restocked {quantity_kg}kg from {supplier}"
        }
        supabase.table("INVENTORY_BALANCE").insert(balance_data).execute()
        
        st.success(f"✅ Restocked {quantity_kg} KG of {material_name}")
        return True
        
    except Exception as e:
        st.error(f"Error recording restock: {str(e)}")
        return False

def record_material_usage_with_balance(batch_id: str, material_name: str, quantity_used_kg: float, usage_date):
    """Record material usage and update inventory balance (FIFO method)"""
    try:
        print(f"DEBUG: record_material_usage_with_balance called for {material_name}")
        print(f"DEBUG: quantity_used_kg = {quantity_used_kg}")
        
        # Convert date if needed
        if isinstance(usage_date, str):
            usage_date_str = usage_date
        else:
            usage_date_str = usage_date.strftime('%Y-%m-%d')
        
        # 1. Check if enough stock is available
        current_stock = get_current_material_balance(material_name)
        print(f"DEBUG: Current stock for {material_name} = {current_stock}")
        
        if current_stock < quantity_used_kg:
            st.error(f"Insufficient {material_name}! Need {quantity_used_kg:.2f}kg, have {current_stock:.2f}kg")
            return False
        
        
        # 2. Get all restocks with remaining stock (oldest first for FIFO)
        response = supabase.table("STOCK_RESTOCK")\
            .select("*")\
            .eq("material_name", material_name)\
            .gt("remaining_kg", 0)\
            .order("restock_date", asc=True)\
            .execute()
        
        print(f"DEBUG: Found {len(response.data) if response.data else 0} restocks with remaining stock")
        
        if not response.data:
            st.error(f"No stock available for {material_name}!")
            return False
        
        remaining_to_use = quantity_used_kg
        
        # 3. Deduct from restocks using FIFO
        for restock in response.data:
            if remaining_to_use <= 0:
                break
            
            available = restock['remaining_kg']
            use_from_this = min(remaining_to_use, available)
            new_remaining = available - use_from_this
            
            print(f"DEBUG: Using {use_from_this}kg from restock {restock['id']} (date: {restock['restock_date']})")
            
            # Update remaining in this restock
            supabase.table("STOCK_RESTOCK")\
                .update({"remaining_kg": new_remaining})\
                .eq("id", restock['id'])\
                .execute()
            
            remaining_to_use -= use_from_this
        
        # 4. Record material usage
        usage_id = str(uuid.uuid4())
        usage_data = {
            "id": usage_id,
            "batch_id": batch_id,
            "material_name": material_name,
            "quantity_used_kg": quantity_used_kg,
            "usage_date": usage_date_str
        }
        supabase.table("MATERIAL_USAGE").insert(usage_data).execute()
        print(f"DEBUG: Recorded usage in MATERIAL_USAGE table")
        
        # 5. Update RAW_MATERIALS_INVENTORY
        inv_response = supabase.table("RAW_MATERIALS_INVENTORY").select("*").eq("material_name", material_name).execute()
        if inv_response.data:
            current = inv_response.data[0]
            new_used = current.get('total_used_kg', 0) + quantity_used_kg
            new_stock = current.get('current_stock_kg', 0) - quantity_used_kg
            
            supabase.table("RAW_MATERIALS_INVENTORY").update({
                "total_used_kg": new_used,
                "current_stock_kg": new_stock
            }).eq("material_name", material_name).execute()
            print(f"DEBUG: Updated RAW_MATERIALS_INVENTORY - new stock: {new_stock}")
        
        # 6. Record in INVENTORY_BALANCE
        current_balance = get_current_material_balance(material_name)
        new_balance = current_balance - quantity_used_kg
        
        balance_data = {
            "id": str(uuid.uuid4()),
            "material_name": material_name,
            "transaction_date": usage_date_str,
            "transaction_type": "USAGE",
            "quantity_kg": -quantity_used_kg,
            "running_balance_kg": new_balance,
            "reference_id": batch_id,
            "notes": f"Used {quantity_used_kg}kg in batch {batch_id}"
        }
        supabase.table("INVENTORY_BALANCE").insert(balance_data).execute()
        print(f"DEBUG: Recorded in INVENTORY_BALANCE")
        
        return True
        
    except Exception as e:
        print(f"ERROR in record_material_usage_with_balance: {str(e)}")
        st.error(f"Error recording usage: {str(e)}")
        return False

def get_current_material_balance(material_name: str):
    """Get current balance for a material from RAW_MATERIALS_INVENTORY"""
    try:
        response = supabase.table("RAW_MATERIALS_INVENTORY")\
            .select("current_stock_kg")\
            .eq("material_name", material_name)\
            .execute()
        
        if response.data:
            return float(response.data[0]['current_stock_kg'])
        return 0.0
    except Exception as e:
        print(f"Error getting balance: {str(e)}")
        return 0.0

def update_raw_material_inventory(material_name: str, purchased_kg: float = 0, used_kg: float = 0):
    """Update the raw materials inventory table"""
    try:
        response = supabase.table("RAW_MATERIALS_INVENTORY")\
            .select("*")\
            .eq("material_name", material_name)\
            .execute()
        
        if response.data:
            current = response.data[0]
            new_purchased = current.get('total_purchased_kg', 0) + purchased_kg
            new_used = current.get('total_used_kg', 0) + used_kg
            new_stock = new_purchased - new_used
            
            supabase.table("RAW_MATERIALS_INVENTORY")\
                .update({
                    "total_purchased_kg": new_purchased,
                    "total_used_kg": new_used,
                    "current_stock_kg": new_stock
                })\
                .eq("material_name", material_name)\
                .execute()
        return True
    except Exception as e:
        print(f"Error updating inventory: {str(e)}")
        return False

def get_material_restock_history(material_name: str):
    """Get all restock history for a material"""
    try:
        response = supabase.table("STOCK_RESTOCK")\
            .select("*")\
            .eq("material_name", material_name)\
            .order("restock_date", desc=True)\
            .execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def get_inventory_balance_history(material_name: str):
    """Get the balance history over time"""
    try:
        response = supabase.table("INVENTORY_BALANCE")\
            .select("*")\
            .eq("material_name", material_name)\
            .order("transaction_date", asc=True)\
            .execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def update_finished_goods_production(product_type: str, quantity_produced: int):
    """Increase finished goods stock when production is made"""
    try:
        response = supabase.table("FINISHED_GOODS_INVENTORY")\
            .select("*")\
            .eq("product_type", product_type)\
            .execute()
        
        if response.data:
            current = response.data[0]
            new_stock = current.get('current_stock', 0) + quantity_produced
            new_produced = current.get('total_produced', 0) + quantity_produced
            
            supabase.table("FINISHED_GOODS_INVENTORY").update({
                "current_stock": new_stock,
                "total_produced": new_produced,
                "last_updated": datetime.now().isoformat()
            }).eq("product_type", product_type).execute()
        else:
            # Create new entry if doesn't exist
            supabase.table("FINISHED_GOODS_INVENTORY").insert({
                "product_type": product_type,
                "current_stock": quantity_produced,
                "total_produced": quantity_produced,
                "total_sold": 0,
                "unit_price": get_price_for_product(product_type),
                "reorder_level": 100
            }).execute()
        
        return True
    except Exception as e:
        st.error(f"Error updating finished goods: {str(e)}")
        return False

def update_finished_goods_sale(product_type: str, quantity_sold: int):
    """Decrease finished goods stock when a sale is made"""
    try:
        response = supabase.table("FINISHED_GOODS_INVENTORY")\
            .select("*")\
            .eq("product_type", product_type)\
            .execute()
        
        if response.data:
            current = response.data[0]
            new_stock = current.get('current_stock', 0) - quantity_sold
            new_sold = current.get('total_sold', 0) + quantity_sold
            
            supabase.table("FINISHED_GOODS_INVENTORY").update({
                "current_stock": new_stock,
                "total_sold": new_sold,
                "last_updated": datetime.now().isoformat()
            }).eq("product_type", product_type).execute()
            
            # Show low stock warning
            reorder_level = current.get('reorder_level', 100)
            if new_stock <= reorder_level:
                st.warning(f"⚠️ Low stock alert: {product_type} has only {new_stock} units left!")
        
        return True
    except Exception as e:
        st.error(f"Error updating finished goods: {str(e)}")
        return False

def get_price_for_product(product_type: str):
    """Get the selling price for a product type"""
    prices = {
        "Sachet 5": 5,
        "Sachet 30": 30,
        "Bottle 100g": 150,
        "Refill 120g": 120
    }
    return prices.get(product_type, 0)

# -------------------------------
# FINISHED GOODS FUNCTIONS (ADD THIS)
# -------------------------------

def update_finished_goods_production(product_type: str, quantity_produced: int):
    """Increase finished goods stock when production is made"""
    try:
        from datetime import datetime
        
        response = supabase.table("FINISHED_GOODS_INVENTORY")\
            .select("*")\
            .eq("product_type", product_type)\
            .execute()
        
        # Price mapping
        prices = {
            "Sachet 5": 5,
            "Sachet 30": 30,
            "Bottle 100g": 150,
            "Refill 120g": 120
        }
        reorder_levels = {
            "Sachet 5": 500,
            "Sachet 30": 200,
            "Bottle 100g": 100,
            "Refill 120g": 50
        }
        
        if response.data:
            current = response.data[0]
            new_stock = current.get('current_stock', 0) + quantity_produced
            new_produced = current.get('total_produced', 0) + quantity_produced
            
            supabase.table("FINISHED_GOODS_INVENTORY").update({
                "current_stock": new_stock,
                "total_produced": new_produced,
                "last_updated": datetime.now().isoformat()
            }).eq("product_type", product_type).execute()
        else:
            # Create new entry
            supabase.table("FINISHED_GOODS_INVENTORY").insert({
                "product_type": product_type,
                "current_stock": quantity_produced,
                "total_produced": quantity_produced,
                "total_sold": 0,
                "unit_price": prices.get(product_type, 0),
                "reorder_level": reorder_levels.get(product_type, 100)
            }).execute()
        
        return True
    except Exception as e:
        print(f"Error updating finished goods: {str(e)}")
        return False

def update_finished_goods_sale(product_type: str, quantity_sold: int):
    """Decrease finished goods stock when a sale is made"""
    try:
        from datetime import datetime
        
        response = supabase.table("FINISHED_GOODS_INVENTORY")\
            .select("*")\
            .eq("product_type", product_type)\
            .execute()
        
        if response.data:
            current = response.data[0]
            new_stock = current.get('current_stock', 0) - quantity_sold
            new_sold = current.get('total_sold', 0) + quantity_sold
            
            supabase.table("FINISHED_GOODS_INVENTORY").update({
                "current_stock": new_stock,
                "total_sold": new_sold,
                "last_updated": datetime.now().isoformat()
            }).eq("product_type", product_type).execute()
            
            # Show warning if low stock
            reorder_level = current.get('reorder_level', 100)
            if new_stock <= reorder_level:
                print(f"⚠️ Low stock alert: {product_type} has only {new_stock} units left!")
        
        return True
    except Exception as e:
        print(f"Error updating finished goods: {str(e)}")
        return False

# -------------------------------
# INVENTORY TRACKING FUNCTIONS (ADD THIS)
# -------------------------------

def record_restock_with_balance(material_name: str, quantity_kg: float, cost_per_kg: float, supplier: str, restock_date, notes: str = ""):
    """Record a restock and update inventory balance"""
    try:
        from datetime import date
        
        # Convert date if needed
        if hasattr(restock_date, 'strftime'):
            restock_date_str = restock_date.strftime('%Y-%m-%d')
        else:
            restock_date_str = str(restock_date)
        
        restock_id = str(uuid.uuid4())
        
        # Record restock
        restock_data = {
            "id": restock_id,
            "material_name": material_name,
            "quantity_kg": quantity_kg,
            "cost_per_kg": cost_per_kg,
            "total_cost": quantity_kg * cost_per_kg,
            "supplier": supplier,
            "restock_date": restock_date_str,
            "remaining_kg": quantity_kg,
            "notes": notes
        }
        supabase.table("STOCK_RESTOCK").insert(restock_data).execute()
        
        # Update raw materials inventory
        inv_response = supabase.table("RAW_MATERIALS_INVENTORY").select("*").eq("material_name", material_name).execute()
        
        if inv_response.data:
            current = inv_response.data[0]
            new_purchased = current.get('total_purchased_kg', 0) + quantity_kg
            new_stock = current.get('current_stock_kg', 0) + quantity_kg
            
            supabase.table("RAW_MATERIALS_INVENTORY").update({
                "total_purchased_kg": new_purchased,
                "current_stock_kg": new_stock,
                "last_restock_date": restock_date_str
            }).eq("material_name", material_name).execute()
        else:
            supabase.table("RAW_MATERIALS_INVENTORY").insert({
                "material_name": material_name,
                "total_purchased_kg": quantity_kg,
                "current_stock_kg": quantity_kg,
                "unit_cost": cost_per_kg,
                "reorder_level": 10,
                "last_restock_date": restock_date_str
            }).execute()
        
        return True
    except Exception as e:
        print(f"Error recording restock: {str(e)}")
        return False

def record_material_usage_with_balance(batch_id: str, material_name: str, quantity_used_kg: float, usage_date):
    """Record material usage and update inventory balance (FIFO method)"""
    try:
        # Convert date if needed
        if hasattr(usage_date, 'strftime'):
            usage_date_str = usage_date.strftime('%Y-%m-%d')
        else:
            usage_date_str = str(usage_date)
        
        # Check if enough stock is available
        current_stock = get_current_material_balance(material_name)
        st.write(f"DEBUG: Current stock for {material_name}: {current_stock}kg")
        
        if current_stock < quantity_used_kg:
            st.error(f"Insufficient {material_name}! Need {quantity_used_kg:.2f}kg, have {current_stock:.2f}kg")
            return False
        
        # Get restocks with remaining stock (oldest first for FIFO)
        # FIXED: Use .order() with column name, then .asc() for ascending order
        response = supabase.table("STOCK_RESTOCK")\
            .select("*")\
            .eq("material_name", material_name)\
            .gt("remaining_kg", 0)\
            .order("restock_date")\
            .execute()
        
        if not response.data:
            st.error(f"No stock available for {material_name}!")
            return False
        
        remaining_to_use = quantity_used_kg
        
        # Deduct from restocks using FIFO
        for restock in response.data:
            if remaining_to_use <= 0:
                break
            
            available = restock['remaining_kg']
            use_from_this = min(remaining_to_use, available)
            new_remaining = available - use_from_this
            
            st.write(f"DEBUG: Using {use_from_this}kg from restock dated {restock['restock_date']}")
            
            # Update remaining in this restock
            supabase.table("STOCK_RESTOCK")\
                .update({"remaining_kg": new_remaining})\
                .eq("id", restock['id'])\
                .execute()
            
            remaining_to_use -= use_from_this
        
        # Record material usage
        usage_data = {
            "id": str(uuid.uuid4()),
            "batch_id": batch_id,
            "material_name": material_name,
            "quantity_used_kg": quantity_used_kg,
            "usage_date": usage_date_str
        }
        supabase.table("MATERIAL_USAGE").insert(usage_data).execute()
        st.write(f"DEBUG: Recorded usage in MATERIAL_USAGE table")
        
        # Update raw materials inventory
        inv_response = supabase.table("RAW_MATERIALS_INVENTORY").select("*").eq("material_name", material_name).execute()
        if inv_response.data:
            current = inv_response.data[0]
            new_used = current.get('total_used_kg', 0) + quantity_used_kg
            new_stock = current.get('current_stock_kg', 0) - quantity_used_kg
            
            supabase.table("RAW_MATERIALS_INVENTORY").update({
                "total_used_kg": new_used,
                "current_stock_kg": new_stock
            }).eq("material_name", material_name).execute()
            st.write(f"DEBUG: Updated RAW_MATERIALS_INVENTORY - new stock: {new_stock}kg")
        
        return True
        
    except Exception as e:
        st.error(f"Error recording usage: {str(e)}")
        return False

def get_current_material_balance(material_name: str):
    """Get current balance for a material"""
    try:
        response = supabase.table("RAW_MATERIALS_INVENTORY")\
            .select("current_stock_kg")\
            .eq("material_name", material_name)\
            .execute()
        
        if response.data:
            return float(response.data[0]['current_stock_kg'])
        return 0.0
    except Exception as e:
        print(f"Error getting balance: {str(e)}")
        return 0.0

def get_material_restock_history(material_name: str):
    """Get all restock history for a material"""
    try:
        response = supabase.table("STOCK_RESTOCK")\
            .select("*")\
            .eq("material_name", material_name)\
            .order("restock_date", desc=True)\
            .execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def get_inventory_balance_history(material_name: str):
    """Get the balance history over time"""
    try:
        response = supabase.table("INVENTORY_BALANCE")\
            .select("*")\
            .eq("material_name", material_name)\
            .order("transaction_date", asc=True)\
            .execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error: {str(e)}")
        return []
    
# -------------------------------
# ASSETS FUNCTIONS
# -------------------------------

def save_asset(asset_data: dict):
    """Save an asset to the ASSETS table"""
    try:
        asset_data["id"] = str(uuid.uuid4())
        response = supabase.table("ASSETS").insert(asset_data).execute()
        if hasattr(response, 'error') and response.error:
            st.error(f"Error saving asset: {response.error.message}")
            return None
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        st.error(f"Error saving asset: {str(e)}")
        return None

def get_assets():
    """Get all assets"""
    try:
        response = supabase.table("ASSETS").select("*").order("purchase_date", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching assets: {str(e)}")
        return []

def delete_asset(asset_id: str):
    """Delete an asset"""
    try:
        response = supabase.table("ASSETS").delete().eq("id", asset_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting asset: {str(e)}")
        return False

def update_asset(asset_id: str, updates: dict):
    """Update an asset"""
    try:
        response = supabase.table("ASSETS").update(updates).eq("id", asset_id).execute()
        return True
    except Exception as e:
        st.error(f"Error updating asset: {str(e)}")
        return False

# -------------------------------
# DAILY STOCK RECONCILIATION FUNCTIONS
# -------------------------------

def save_daily_stock_reconciliation(record: dict):
    """Save daily stock reconciliation record"""
    try:
        record["id"] = str(uuid.uuid4())
        response = supabase.table("DAILY_STOCK_RECONCILIATION").insert(record).execute()
        if hasattr(response, 'error') and response.error:
            st.error(f"Error saving stock reconciliation: {response.error.message}")
            return None
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        st.error(f"Error saving stock reconciliation: {str(e)}")
        return None

def get_daily_stock_reconciliation(date_filter=None, product_filter=None):
    """Get daily stock reconciliation records"""
    try:
        query = supabase.table("DAILY_STOCK_RECONCILIATION").select("*").order("reconciliation_date", desc=True)
        if date_filter:
            query = query.eq("reconciliation_date", str(date_filter))
        if product_filter:
            query = query.eq("product_name", product_filter)
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching stock reconciliation: {str(e)}")
        return []

def get_daily_summary(date):
    """Get summary for a specific date"""
    try:
        response = supabase.table("DAILY_STOCK_RECONCILIATION").select("*").eq("reconciliation_date", str(date)).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            summary = {
                'total_sold': df['sold_quantity'].sum(),
                'total_revenue': df['total_revenue'].sum(),
                'total_given_free': df['given_free'].sum(),
                'products': len(df)
            }
            return summary
        return None
    except Exception as e:
        return None

# -------------------------------
# HOTEL TRACKING FUNCTIONS
# -------------------------------

def save_hotel(hotel_data: dict):
    """Save a new hotel"""
    try:
        hotel_data["id"] = str(uuid.uuid4())
        response = supabase.table("HOTELS").insert(hotel_data).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        st.error(f"Error saving hotel: {str(e)}")
        return None

def get_all_hotels():
    """Get all hotels"""
    try:
        response = supabase.table("HOTELS").select("*").order("hotel_name").execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def save_hotel_refill(refill_data: dict):
    """Record a hotel refill"""
    try:
        refill_data["id"] = str(uuid.uuid4())
        response = supabase.table("HOTEL_REFILLS").insert(refill_data).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        st.error(f"Error saving refill: {str(e)}")
        return None

def get_hotel_refills(hotel_id: str = None):
    """Get refill history for a hotel or all"""
    try:
        query = supabase.table("HOTEL_REFILLS").select("*, HOTELS(*)").order("refill_date", desc=True)
        if hotel_id:
            query = query.eq("hotel_id", hotel_id)
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def get_hotel_refill_summary():
    """Get summary of refills by hotel"""
    try:
        response = supabase.table("HOTEL_REFILLS").select("*, HOTELS(*)").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            summary = df.groupby('HOTELS').agg({
                'quantity': 'sum',
                'amount_paid': 'sum',
                'refill_date': 'count'
            }).reset_index()
            summary.columns = ['Hotel', 'Total Quantity', 'Total Revenue', 'Number of Refills']
            return summary
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()



def get_hotel_territory_analysis():
    """
    Real territory/velocity analysis using actual HOTELS + HOTEL_REFILLS tables.
    Returns a DataFrame with one row per hotel: visit count, total units,
    avg days between restocks, days since last restock, tier, and due_for_visit.
    """
    try:
        hotels = get_all_hotels()
        refills = get_hotel_refills()  # all refills, joined with HOTELS(*)

        if not hotels:
            return pd.DataFrame()

        hotels_df = pd.DataFrame(hotels)
        refills_df = pd.DataFrame(refills)

        if refills_df.empty:
            # No refills yet - everything is New/Unknown
            hotels_df['visit_count'] = 0
            hotels_df['total_units'] = 0
            hotels_df['avg_days_between_restocks'] = None
            hotels_df['days_since_last_restock'] = None
            hotels_df['tier'] = 'New/Unknown'
            hotels_df['due_for_visit'] = True
            return hotels_df

        refills_df['refill_date'] = pd.to_datetime(refills_df['refill_date'])

        agg = refills_df.groupby('hotel_id').agg(
            visit_count=('id', 'count'),
            total_units=('quantity', 'sum'),
            last_restock=('refill_date', 'max'),
            first_restock=('refill_date', 'min')
        ).reset_index()

        agg['span_days'] = (agg['last_restock'] - agg['first_restock']).dt.days
        # avoid divide-by-zero when there's only 1 visit
        agg['avg_days_between_restocks'] = agg['span_days'] / (agg['visit_count'] - 1).clip(lower=1)

        today = pd.Timestamp(date.today())
        agg['days_since_last_restock'] = (today - agg['last_restock']).dt.days

        merged = hotels_df.merge(agg, left_on='id', right_on='hotel_id', how='left')

        def tier(row):
            if pd.isna(row.get('visit_count')) or row['visit_count'] < 2:
                return 'New/Unknown'
            d = row['avg_days_between_restocks']
            if d <= 10:
                return 'High'
            elif d <= 21:
                return 'Medium'
            else:
                return 'Low'

        merged['tier'] = merged.apply(tier, axis=1)

        def is_due(row):
            if pd.isna(row.get('avg_days_between_restocks')) or pd.isna(row.get('days_since_last_restock')):
                return True  # never refilled or unknown pattern = worth a visit
            return row['days_since_last_restock'] > row['avg_days_between_restocks']

        merged['due_for_visit'] = merged.apply(is_due, axis=1)

        return merged

    except Exception as e:
        st.error(f"Error running territory analysis: {str(e)}")
        return pd.DataFrame()

# -------------------------------
# MAMA MBOGAS TRACKING FUNCTIONS
# -------------------------------

def save_mama_mboga(mama_data: dict):
    """Save a new Mama Mboga shop"""
    try:
        mama_data["id"] = str(uuid.uuid4())
        response = supabase.table("MAMA_MBOGAS").insert(mama_data).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        st.error(f"Error saving Mama Mboga: {str(e)}")
        return None

def get_all_mama_mbogas():
    """Get all Mama Mboga shops"""
    try:
        response = supabase.table("MAMA_MBOGAS").select("*").order("shop_name").execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def save_mama_purchase(purchase_data: dict):
    """Record a Mama Mboga purchase"""
    try:
        purchase_data["id"] = str(uuid.uuid4())
        response = supabase.table("MAMA_MBOGAS_PURCHASES").insert(purchase_data).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        st.error(f"Error saving purchase: {str(e)}")
        return None

def get_mama_purchases(mama_id: str = None):
    """Get purchase history for a Mama Mboga or all"""
    try:
        query = supabase.table("MAMA_MBOGAS_PURCHASES").select("*, MAMA_MBOGAS(*)").order("purchase_date", desc=True)
        if mama_id:
            query = query.eq("mama_id", mama_id)
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        return []


# -------------------------------
# MAMA MBOGAS TRACKING FUNCTIONS
# -------------------------------

def save_mama_mboga(mama_data: dict):
    """Save a new Mama Mboga shop"""
    try:
        mama_data["id"] = str(uuid.uuid4())
        response = supabase.table("MAMA_MBOGAS").insert(mama_data).execute()
        if hasattr(response, 'error') and response.error:
            st.error(f"Error saving Mama Mboga: {response.error.message}")
            return None
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        st.error(f"Error saving Mama Mboga: {str(e)}")
        return None

def get_all_mama_mbogas():
    """Get all Mama Mboga shops"""
    try:
        response = supabase.table("MAMA_MBOGAS").select("*").order("shop_name").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching Mama Mbogas: {str(e)}")
        return []

def save_mama_purchase(purchase_data: dict):
    """Record a Mama Mboga purchase"""
    try:
        purchase_data["id"] = str(uuid.uuid4())
        response = supabase.table("MAMA_MBOGAS_PURCHASES").insert(purchase_data).execute()
        if hasattr(response, 'error') and response.error:
            st.error(f"Error saving purchase: {response.error.message}")
            return None
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        st.error(f"Error saving purchase: {str(e)}")
        return None

def get_mama_purchases(mama_id: str = None):
    """Get purchase history for a Mama Mboga or all"""
    try:
        query = supabase.table("MAMA_MBOGAS_PURCHASES").select("*, MAMA_MBOGAS(*)").order("purchase_date", desc=True)
        if mama_id:
            query = query.eq("mama_id", mama_id)
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching purchases: {str(e)}")
        return []
    
# -------------------------------
# FREE ITEMS / GIVEAWAYS FUNCTIONS
# -------------------------------

def save_free_item(giveaway_data: dict):
    """Record a free item giveaway"""
    try:
        giveaway_data["id"] = str(uuid.uuid4())
        response = supabase.table("FREE_ITEMS").insert(giveaway_data).execute()
        if hasattr(response, 'error') and response.error:
            st.error(f"Error saving giveaway: {response.error.message}")
            return None
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        st.error(f"Error saving giveaway: {str(e)}")
        return None

def get_free_items(start_date=None, end_date=None):
    """Get all free items giveaways"""
    try:
        query = supabase.table("FREE_ITEMS").select("*").order("giveaway_date", desc=True)
        if start_date:
            query = query.gte("giveaway_date", str(start_date))
        if end_date:
            query = query.lte("giveaway_date", str(end_date))
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching giveaways: {str(e)}")
        return []

def get_free_items_summary():
    """Get summary of giveaways by product and reason"""
    try:
        response = supabase.table("FREE_ITEMS").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            summary = df.groupby(['product_type', 'reason']).agg({
                'quantity': 'sum',
                'total_value': 'sum'
            }).reset_index()
            return summary
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame() 

# -------------------------------
# ROUTE & REFILL OPTIMIZATION FUNCTIONS
# -------------------------------

def save_location(location_data: dict):
    """Save a location for mapping"""
    try:
        location_data["id"] = str(uuid.uuid4())
        response = supabase.table("LOCATIONS").insert(location_data).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        st.error(f"Error saving location: {str(e)}")
        return None

def get_all_locations():
    """Get all locations"""
    try:
        response = supabase.table("LOCATIONS").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def save_refill_schedule(schedule_data: dict):
    """Save a refill schedule for a customer"""
    try:
        schedule_data["id"] = str(uuid.uuid4())
        response = supabase.table("REFILL_SCHEDULES").insert(schedule_data).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        st.error(f"Error saving schedule: {str(e)}")
        return None

def get_refill_schedules():
    """Get all refill schedules"""
    try:
        response = supabase.table("REFILL_SCHEDULES").select("*").order("next_refill_date", asc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def get_today_refills():
    """Get customers due for refill today"""
    try:
        today = date.today().isoformat()
        response = supabase.table("REFILL_SCHEDULES").select("*").lte("next_refill_date", today).execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def update_refill_schedule(customer_name: str, refill_date: date, quantity: int):
    """Update refill schedule after a refill"""
    try:
        # Get current schedule
        response = supabase.table("REFILL_SCHEDULES").select("*").eq("customer_name", customer_name).execute()
        if response.data:
            avg_days = response.data[0]['average_refill_days']
            next_refill = refill_date + timedelta(days=avg_days)
            
            supabase.table("REFILL_SCHEDULES").update({
                "last_refill_date": str(refill_date),
                "next_refill_date": str(next_refill),
                "estimated_quantity": quantity
            }).eq("customer_name", customer_name).execute()
        return True
    except Exception as e:
        return False

# -------------------------------
# COMMISSION TRACKING FUNCTIONS
# -------------------------------

def get_commission_rate(product_name: str):
    """Get commission rate for a product"""
    try:
        response = supabase.table("COMMISSION_RATES").select("*").eq("product_name", product_name).eq("is_active", True).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error getting commission rate: {str(e)}")
        return None

def save_sale_commission(commission_data: dict):
    """Save commission for a sale"""
    try:
        commission_data["id"] = str(uuid.uuid4())
        response = supabase.table("SALES_COMMISSIONS").insert(commission_data).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        print(f"Error saving commission: {str(e)}")
        return None

def get_salesperson_commission(sales_person_id: str, start_date=None, end_date=None):
    """Get total commission for a salesperson"""
    try:
        query = supabase.table("SALES_COMMISSIONS").select("*").eq("sales_person_id", sales_person_id)
        if start_date:
            query = query.gte("created_at", str(start_date))
        if end_date:
            query = query.lte("created_at", str(end_date))
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def get_all_commissions_pending():
    """Get all unpaid commissions"""
    try:
        response = supabase.table("SALES_COMMISSIONS").select("*, SALES_PEOPLE(full_name)").eq("commission_paid", False).execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def mark_commission_paid(commission_id: str, payment_date: date):
    """Mark commission as paid"""
    try:
        supabase.table("SALES_COMMISSIONS").update({
            "commission_paid": True,
            "payment_date": str(payment_date)
        }).eq("id", commission_id).execute()
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def get_commission_summary():
    """Get summary of all commissions"""
    try:
        response = supabase.table("SALES_COMMISSIONS").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            summary = {
                'total_commission': df['commission_amount'].sum(),
                'paid_commission': df[df['commission_paid'] == True]['commission_amount'].sum(),
                'pending_commission': df[df['commission_paid'] == False]['commission_amount'].sum(),
                'total_transactions': len(df)
            }
            return summary
        return {'total_commission': 0, 'paid_commission': 0, 'pending_commission': 0, 'total_transactions': 0}
    except Exception as e:
        return {'total_commission': 0, 'paid_commission': 0, 'pending_commission': 0, 'total_transactions': 0}
       

# -------------------------------
# HOTEL SUCCESS & RETENTION FUNCTIONS
# -------------------------------

def save_hotel_consumption(data: dict):
    try:
        data["id"] = str(uuid.uuid4())
        response = supabase.table("HOTEL_CONSUMPTION").insert(data).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def save_hotel_reorder(data: dict):
    try:
        data["id"] = str(uuid.uuid4())
        response = supabase.table("HOTEL_REORDERS").insert(data).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def save_hotel_chef(data: dict):
    try:
        data["id"] = str(uuid.uuid4())
        response = supabase.table("HOTEL_CHEFS").insert(data).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def get_hotel_consumption(hotel_id: str):
    try:
        response = supabase.table("HOTEL_CONSUMPTION").select("*").eq("hotel_id", hotel_id).execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def get_hotel_reorders(hotel_id: str = None):
    try:
        query = supabase.table("HOTEL_REORDERS").select("*")
        if hotel_id:
            query = query.eq("hotel_id", hotel_id)
        response = query.order("reorder_date", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def get_hotel_chefs(hotel_id: str = None):
    try:
        query = supabase.table("HOTEL_CHEFS").select("*")
        if hotel_id:
            query = query.eq("hotel_id", hotel_id)
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def get_hotel_retention_metrics():
    """Get key retention metrics"""
    try:
        # Get all hotels
        hotels = get_all_hotels()
        if not hotels:
            return None
        
        total_hotels = len(hotels)
        
        # Get reorder data
        reorders = get_hotel_reorders()
        reorder_count = len(reorders)
        
        # Get unique hotels that reordered
        reorder_hotels = set([r['hotel_id'] for r in reorders])
        reordering_hotels = len(reorder_hotels)
        
        # Calculate retention rate
        retention_rate = (reordering_hotels / total_hotels * 100) if total_hotels > 0 else 0
        
        # Get proactive vs prompted reorders
        proactive = len([r for r in reorders if r.get('was_proactive', False)])
        prompted = len([r for r in reorders if r.get('was_prompted', True)])
        
        return {
            'total_hotels': total_hotels,
            'reordering_hotels': reordering_hotels,
            'retention_rate': retention_rate,
            'proactive_reorders': proactive,
            'prompted_reorders': prompted,
            'total_reorders': reorder_count
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# -------------------------------
# HOTEL SUCCESS & RETENTION FUNCTIONS
# -------------------------------

def get_hotel_retention_metrics():
    """Get key retention metrics for hotels"""
    try:
        # Get all hotels
        hotels = get_all_hotels()
        if not hotels:
            return {
                'total_hotels': 0,
                'reordering_hotels': 0,
                'retention_rate': 0,
                'proactive_reorders': 0,
                'prompted_reorders': 0,
                'total_reorders': 0
            }
        
        total_hotels = len(hotels)
        
        # Get reorder data
        reorders = get_hotel_reorders()
        reorder_count = len(reorders)
        
        # Get unique hotels that reordered
        reorder_hotels = set([r['hotel_id'] for r in reorders])
        reordering_hotels = len(reorder_hotels)
        
        # Calculate retention rate
        retention_rate = (reordering_hotels / total_hotels * 100) if total_hotels > 0 else 0
        
        # Get proactive vs prompted reorders
        proactive = len([r for r in reorders if r.get('was_proactive', False)])
        prompted = len([r for r in reorders if r.get('was_prompted', True)])
        
        return {
            'total_hotels': total_hotels,
            'reordering_hotels': reordering_hotels,
            'retention_rate': retention_rate,
            'proactive_reorders': proactive,
            'prompted_reorders': prompted,
            'total_reorders': reorder_count
        }
    except Exception as e:
        print(f"Error getting retention metrics: {str(e)}")
        return {
            'total_hotels': 0,
            'reordering_hotels': 0,
            'retention_rate': 0,
            'proactive_reorders': 0,
            'prompted_reorders': 0,
            'total_reorders': 0
        }

def save_hotel_consumption(data: dict):
    """Save hotel consumption pattern"""
    try:
        data["id"] = str(uuid.uuid4())
        response = supabase.table("HOTEL_CONSUMPTION").insert(data).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def get_hotel_consumption(hotel_id: str):
    """Get consumption patterns for a hotel"""
    try:
        response = supabase.table("HOTEL_CONSUMPTION").select("*").eq("hotel_id", hotel_id).execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def save_hotel_reorder(data: dict):
    """Record a hotel reorder"""
    try:
        data["id"] = str(uuid.uuid4())
        response = supabase.table("HOTEL_REORDERS").insert(data).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def get_hotel_reorders(hotel_id: str = None):
    """Get reorder history for a hotel or all hotels"""
    try:
        query = supabase.table("HOTEL_REORDERS").select("*")
        if hotel_id:
            query = query.eq("hotel_id", hotel_id)
        response = query.order("reorder_date", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def save_hotel_chef(data: dict):
    """Save chef relationship"""
    try:
        data["id"] = str(uuid.uuid4())
        response = supabase.table("HOTEL_CHEFS").insert(data).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def get_hotel_chefs(hotel_id: str = None):
    """Get chefs for a hotel or all hotels"""
    try:
        query = supabase.table("HOTEL_CHEFS").select("*")
        if hotel_id:
            query = query.eq("hotel_id", hotel_id)
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        return []
    
# -------------------------------
# CUSTOMER ENGAGEMENT FUNCTIONS
# -------------------------------

def save_customer_contact(customer_name: str, phone_number: str, customer_type: str, location: str = "", notes: str = ""):
    """Save a customer contact. Returns dict with status/message for app.py to check."""
    try:
        formatted_phone = format_phone(phone_number)
        existing = supabase.table("CUSTOMER_CONTACTS").select("*").eq("phone_number", formatted_phone).execute()
        if existing.data:
            return {"status": "exists", "message": f"Contact with phone {phone_number} already exists"}

        data = {
            "id": str(uuid.uuid4()),
            "customer_name": customer_name,
            "phone_number": formatted_phone,
            "customer_type": customer_type,
            "location": location,
            "notes": notes,
            "status": "Active"
        }
        response = supabase.table("CUSTOMER_CONTACTS").insert(data).execute()
        if response.data:
            return {"status": "success", "message": f"Saved {customer_name}"}
        return {"status": "error", "message": "No data returned from insert"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_customer_contacts(customer_type: str = None):
    """Get customer contacts, optionally filtered by type"""
    try:
        query = supabase.table("CUSTOMER_CONTACTS").select("*").eq("status", "Active")
        if customer_type:
            query = query.eq("customer_type", customer_type)
        response = query.order("customer_name").execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error getting contacts: {str(e)}")
        return []

def save_customer_contact(data: dict):
    """Save a customer contact"""
    try:
        data["id"] = str(uuid.uuid4())
        response = supabase.table("CUSTOMER_CONTACTS").insert(data).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def delete_customer_contact(contact_id: str):
    """Delete a customer contact"""
    try:
        supabase.table("CUSTOMER_CONTACTS").delete().eq("id", contact_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting contact: {str(e)}")
        return False
    

def save_automated_message(message_name: str, message_content: str, customer_type: str, schedule_type: str, schedule_day: str, schedule_time: str):
    """Save an automated message template. Returns dict with status/message."""
    try:
        data = {
            "id": str(uuid.uuid4()),
            "message_name": message_name,
            "message_content": message_content,
            "customer_type": None if customer_type == "All" else customer_type,
            "schedule_type": schedule_type,
            "schedule_day": schedule_day,
            "schedule_time": schedule_time,
            "is_active": True
        }
        response = supabase.table("AUTOMATED_MESSAGES").insert(data).execute()
        if response.data:
            return {"status": "success", "message": f"Saved message '{message_name}'"}
        return {"status": "error", "message": "No data returned from insert"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_automated_messages():
    """Get all automated messages"""
    try:
        response = supabase.table("AUTOMATED_MESSAGES").select("*").eq("is_active", True).execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def get_todays_messages():
    """Get messages scheduled for today"""
    try:
        today = date.today().strftime('%A')  # Monday, Tuesday, etc.
        response = supabase.table("AUTOMATED_MESSAGES").select("*").eq("schedule_day", today).eq("is_active", True).execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def save_message_history(data: dict):
    """Save message history"""
    try:
        data["id"] = str(uuid.uuid4())
        response = supabase.table("MESSAGE_HISTORY").insert(data).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def get_message_history(customer_id: str = None):
    """Get message history for a customer"""
    try:
        query = supabase.table("MESSAGE_HISTORY").select("*")
        if customer_id:
            query = query.eq("customer_id", customer_id)
        response = query.order("sent_date", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def update_customer_last_contact(customer_id: str):
    """Update last contact date for a customer"""
    try:
        supabase.table("CUSTOMER_CONTACTS").update({
            "last_contact_date": str(date.today())
        }).eq("id", customer_id).execute()
        return True
    except Exception as e:
        return False

# -------------------------------
# SMS FUNCTIONS (AFRICA'S TALKING)
# -------------------------------

def send_sms_africastalking(phone_number, message):
    """Send SMS via Africa's Talking API"""
    try:
        api_key = st.secrets["AFRICASTALKING_API_KEY"]
        username = st.secrets.get("AFRICASTALKING_USERNAME", "sandbox")
        sender_id = st.secrets.get("AFRICASTALKING_SENDER_ID", "SpiseUp")
        
        phone = phone_number.strip().replace(" ", "").replace("+", "")
        if phone.startswith("0"):
            phone = "254" + phone[1:]
        elif phone.startswith("7") and len(phone) == 9:
            phone = "254" + phone
        
        url = "https://api.africastalking.com/version1/messaging"
        headers = {
            "apiKey": api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "username": username,
            "to": phone,
            "message": message,
            "from": sender_id
        }
        
        response = requests.post(url, headers=headers, data=data, timeout=15)
        result = response.json()
        
        if response.status_code == 200 and 'SMSMessageData' in result:
            if result['SMSMessageData']['Recipients'][0]['status'] == 'Success':
                return {"status": "success", "result": result}
        
        return {"status": "error", "http_status": response.status_code, "result": result}
        
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Request timed out after 15s — Africa's Talking API may be unreachable"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def send_bulk_sms(phone_numbers, message):
    """Send SMS to multiple recipients"""
    try:
        results = []
        for phone in phone_numbers:
            result = send_sms_africastalking(phone, message)
            results.append({"phone": phone, "result": result})
        return {"status": "success", "results": results}
    except Exception as e:
        print(f"Error sending bulk SMS: {str(e)}")
        return {"status": "error", "message": str(e)}

def send_test_sms(phone_number, message):
    """Send a test SMS with detailed error reporting"""
    try:
        # Check if API key exists
        try:
            api_key = st.secrets["AFRICASTALKING_API_KEY"]
        except:
            return {"status": "error", "message": "AFRICASTALKING_API_KEY not found in secrets"}
        
        # Format phone
        phone = phone_number.strip().replace(" ", "").replace("+", "")
        if phone.startswith("0"):
            phone = "254" + phone[1:]
        
        url = "https://api.africastalking.com/version1/messaging"
        headers = {
            "apiKey": api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "username": "sandbox",
            "to": phone,
            "message": message,
            "from": "SpiseUp"
        }
        
        response = requests.post(url, headers=headers, data=data)
        result = response.json()
        
        # Return detailed result for debugging
        return {
            "status": "success" if response.status_code == 200 else "error",
            "response_code": response.status_code,
            "result": result,
            "phone": phone,
            "message": message
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

def send_scheduled_messages():
    """Send all scheduled messages for today"""
    try:
        today = date.today().strftime('%A')
        
        # Get today's scheduled messages
        response = supabase.table("AUTOMATED_MESSAGES")\
            .select("*")\
            .eq("schedule_day", today)\
            .eq("is_active", True)\
            .execute()
        
        messages = response.data if response.data else []
        sent_count = 0
        
        for msg in messages:
            # Get recipients
            customer_type = msg.get('customer_type')
            recipients = get_customer_contacts(customer_type)
            
            for customer in recipients:
                phone = customer.get('phone_number')
                if phone:
                    result = send_sms_africastalking(phone, msg['message_content'])
                    if result.get('status') == 'success':
                        sent_count += 1
                        
                        # Save to history
                        history_data = {
                            "customer_id": customer['id'],
                            "message_id": msg['id'],
                            "phone_number": phone,
                            "message_content": msg['message_content'],
                            "sent_date": str(datetime.now()),
                            "was_delivered": True
                        }
                        save_message_history(history_data)
            
            # Update last sent date
            supabase.table("AUTOMATED_MESSAGES")\
                .update({"last_sent_date": str(date.today())})\
                .eq("id", msg['id'])\
                .execute()
        
        return {"status": "success", "sent_count": sent_count}
    except Exception as e:
        print(f"Error sending scheduled messages: {str(e)}")
        return {"status": "error", "message": str(e)}
    

# -------------------------------
# SMS HELPER FUNCTIONS
# -------------------------------

def verify_api_key():
    """Check if API key exists and is valid"""
    try:
        api_key = st.secrets["AFRICASTALKING_API_KEY"]
        username = st.secrets.get("AFRICASTALKING_USERNAME", "sandbox")
        
        if not api_key.startswith("atsk_"):
            return "❌ API key should start with 'atsk_'"
        
        url = f"https://api.africastalking.com/version1/user?username={username}"
        response = requests.get(url, headers={"apiKey": api_key})
        
        if response.status_code == 200:
            return "✅ API key is valid"
        else:
            return f"❌ API key invalid: {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ API key not found in secrets: {str(e)}"

def check_at_balance():
    """Check Africa's Talking balance"""
    try:
        api_key = st.secrets["AFRICASTALKING_API_KEY"]
        username = st.secrets.get("AFRICASTALKING_USERNAME", "sandbox")
        
        url = f"https://api.africastalking.com/version1/user?username={username}"
        headers = {"apiKey": api_key}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            balance = data.get('UserData', {}).get('balance', '0')
            return f"💰 Balance: {balance}"
        return f"Could not check balance: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error checking balance: {str(e)}"

def format_phone(phone):
    """Format phone number correctly for Africa's Talking"""
    # Remove all non-digits
    phone = ''.join(filter(str.isdigit, str(phone)))
    
    # Remove leading 0 and add 254
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    elif len(phone) == 9:  # 712345678
        phone = '254' + phone
    elif len(phone) == 12 and phone.startswith('254'):
        pass  # Already correct
    else:
        phone = '254' + phone[-9:]  # Take last 9 digits
    
    return phone

def sanitize_message(message):
    """Remove problematic characters from message"""
    # Remove % characters
    message = message.replace('%', '')
    # Remove other problematic characters
    message = message.replace('&', 'and')
    return message[:160]  # Max 160 characters