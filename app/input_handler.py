import os
import csv
from fastapi import UploadFile, HTTPException
from typing import List


# ✅ Validate and clean a single review string
def validate_single_review(review_text: str) -> str:
    """
    Ensures a single review is valid and returns a stripped version.
    """
    if not review_text or not review_text.strip():
        raise HTTPException(status_code=400, detail="Review text cannot be empty.")
    return review_text.strip()


# ✅ Process uploaded CSV for bulk review summarization
def process_bulk_reviews(file: UploadFile) -> List[str]:
    """
    Reads and validates a CSV file containing customer reviews.
    Returns a list of cleaned, non-empty reviews from the 'review' column.
    """
    filename = file.filename
    extension = os.path.splitext(filename)[1].lower()

    # 🔒 Only allow CSV files for now
    if extension != ".csv":
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    try:
        # 📥 Read file content
        content = file.file.read().decode("utf-8")
        reader = csv.DictReader(content.splitlines())

        # 🧾 Normalize header names
        fieldnames = [f.lower().strip() for f in reader.fieldnames]
        if "review" not in fieldnames:
            raise HTTPException(status_code=400, detail="CSV file must contain a 'review' column (case-insensitive).")

        reviews = []
        for row in reader:
            # 📦 Support flexible casing of the column name
            review_text = row.get("review") or row.get("Review") or ""
            review_text = review_text.strip()
            if review_text:
                reviews.append(review_text)

        if not reviews:
            raise HTTPException(status_code=400, detail="No valid reviews found in the file.")

        return reviews

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")


# 🔧 (Optional) DOCX support placeholder
def process_docx_file(file: UploadFile) -> List[str]:
    """
    Placeholder for future support of DOCX review extraction.
    """
    raise HTTPException(status_code=501, detail="DOCX support not yet implemented.")
