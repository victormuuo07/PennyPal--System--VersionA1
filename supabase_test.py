from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test inserting a sample record
record = {
    "Date": "2026-02-02",
    "Name": "Test Shop",
    "Phone": "0712345678",
    "Location": "Test Location",
    "Product": "SpiseUp Chilli Sachet",
    "Quantity": 10,
    "Price_per_Unit": 5,
    "Total": 50,
    "Feedback": "Test feedback",
    "Follow_Up": "Call back"
}

response = supabase.table("SALES").insert(record).execute()

# In Supabase v2, check response like this:
print("✅ Inserted data:", response.data)
print("Raw response object:", response)
