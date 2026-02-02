from schema import FIELDS

def validate_record(record: dict):
    missing_fields = []
    for field in FIELDS:
        if field not in record or record[field] in ["", None]:
            missing_fields.append(field)
    return missing_fields
