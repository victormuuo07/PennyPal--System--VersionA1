from schema import FIELDS

def validate_record(record: dict):
    missing = [field for field in FIELDS if field not in record or record[field] == ""]
    return missing
