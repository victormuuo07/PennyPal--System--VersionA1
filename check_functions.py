# check_functions.py
import sys
import inspect

try:
    import supabase_client
    
    # List all functions in supabase_client
    print("Functions in supabase_client.py:")
    for name, obj in inspect.getmembers(supabase_client):
        if inspect.isfunction(obj):
            print(f"  - {name}")
except ImportError as e:
    print(f"Error importing: {e}")