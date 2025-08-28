import csv
import os
from fastapi import UploadFile
from typing import List, Dict

# ✅ Create upload directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_and_parse_csv(file: UploadFile) -> List[Dict[str, str]]:
    """
    Save the uploaded CSV file and extract 'review' and 'date' (if present).
    Falls back to dummy 'date' if no date or timestamp column is found.
    """
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    # ✅ Save uploaded file to disk
    with open(file_location, "wb+") as f:
        f.write(file.file.read())

    reviews = []
    fallback_date = "2025-06-10"  # Used if no valid date field is found

    try:
        with open(file_location, "r", encoding="utf-8") as csvfile:
            # ✅ Auto-detect delimiter (comma or tab)
            sample = csvfile.read(2048)
            delimiter = "," if sample.count(",") >= sample.count("\t") else "\t"
            csvfile.seek(0)

            reader = csv.DictReader(csvfile, delimiter=delimiter)
            original_fields = reader.fieldnames or []

            # ✅ Normalize headers (case-insensitive)
            field_map = {field.lower().strip(): field for field in original_fields}
            review_key = field_map.get("review")
            date_key = field_map.get("date") or field_map.get("timestamp")  # allow either

            if not review_key:
                raise ValueError("CSV must contain a 'review' column.")

            # ✅ Read and process each row
            for row in reader:
                print("🧾 Raw Row:", row)  # Debugging log

                review_text = row.get(review_key, "").strip()
                date_value = row.get(date_key, "").strip() if date_key else ""

                if review_text:
                    reviews.append({
                        "review": review_text,
                        "date": date_value if date_value else fallback_date
                    })

    except Exception as e:
        print(f"❌ Error while parsing CSV: {e}")
        raise ValueError("Invalid CSV format or encoding issue.")

    if not reviews:
        raise ValueError("No valid reviews found.")

    print(f"✅ Parsed {len(reviews)} reviews with actual or fallback dates.")
    return reviews
