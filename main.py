import json
import sys
from validator import validate_record
from storage import save_record

print("=== SpiseUp Field Bookkeeper Agent (V1) ===")

while True:
    print("\nPaste full JSON (type END on a new line when done, or type EXIT to quit):")
    lines = []
    while True:
        line = sys.stdin.readline()
        if line.strip().upper() == "END":
            break
        if line.strip().upper() == "EXIT":
            exit(0)
        lines.append(line)
    raw = "".join(lines)

    try:
        record = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON. Error: {e}\n")
        continue

    missing = validate_record(record)

    if missing:
        print("❓ Missing fields:", ", ".join(missing))
        print("Please clarify and re-run.\n")
    else:
        save_record(record)
        print("✅ Record saved successfully.\n")
