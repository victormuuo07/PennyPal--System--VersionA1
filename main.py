import json
import sys
from validator import validate_record
from supabase_client import save_record

print("=== SpiseUp Field Bookkeeper Agent (Supabase CLI) ===")

while True:
    print("\nPaste full JSON (type END on a new line when done, or type EXIT to quit):")
    lines = []

    # Collect multi-line JSON
    while True:
        line = sys.stdin.readline()
        if line.strip().upper() == "END":
            break
        if line.strip().upper() == "EXIT":
            print("Exiting...")
            exit(0)
        lines.append(line)

    raw_json = "".join(lines)

    # Parse JSON
    try:
        record = json.loads(raw_json)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON. Error: {e}\n")
        continue

    # Validate required fields
    missing = validate_record(record)
    if missing:
        print("❗ Missing fields:", ", ".join(missing))
        print("Please clarify and re-run.\n")
        continue

    # Save to Supabase
    try:
        inserted = save_record(record)
        print("✅ Record saved to Supabase!")
        print("Inserted row:", inserted)
    except Exception as e:
        print(f"❌ Failed to save record: {e}\n")
