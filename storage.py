import csv
import os
from schema import FIELDS

# Create a folder called 'data' inside your project
DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_FOLDER, exist_ok=True)  # creates folder if it doesn't exist

# Save CSV inside 'data' folder
FILE_NAME = os.path.join(DATA_FOLDER, "spiseup_sales.csv")

def save_record(record: dict):
    file_exists = os.path.isfile(FILE_NAME)

    with open(FILE_NAME, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)

        if not file_exists:
            writer.writeheader()

        writer.writerow(record)
