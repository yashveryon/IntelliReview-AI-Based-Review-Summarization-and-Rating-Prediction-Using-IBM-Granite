from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import csv
import os
from datetime import date

from app.file_upload import save_and_parse_csv  # ✅ Returns list of dicts with review + date
from app.input_handler import validate_single_review
from app.ibm_sentiment import analyze_sentiment_ibm
from app.summarizer import summarize_review  # ✅ Uses Granite + fallback

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Mount static and output folders
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/output", StaticFiles(directory="output"), name="output")

# ✅ Set up Jinja2 Templates for frontend rendering
templates = Jinja2Templates(directory="templates")

# ✅ Home route
@app.get("/", response_class=HTMLResponse)
def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ✅ Single review summarization
@app.post("/summarize")
def summarize_text(review: str = Form(...)):
    try:
        cleaned = validate_single_review(review)
        sentiment = analyze_sentiment_ibm(cleaned)
        granite_result = summarize_review(cleaned)

        return {
            "original_review": cleaned,
            "summary": granite_result["summary"],
            "predicted_rating": granite_result["predicted_rating"],
            "sentiment": sentiment,
            "rating_stars": "⭐" * int(round(granite_result["predicted_rating"]))
        }

    except Exception as e:
        print("❌ Error in /summarize:", str(e))
        raise HTTPException(status_code=500, detail="Summarization failed.")


# ✅ Bulk summarization from uploaded CSV
@app.post("/upload/summarize_all")
async def summarize_all_reviews(file: UploadFile = File(...)):
    try:
        print(f"📁 File received: {file.filename}")
        parsed_reviews = save_and_parse_csv(file)  # List of dicts with 'review' and 'date'

        if not parsed_reviews:
            raise ValueError("No valid reviews found in the uploaded file.")

        result = []
        for i, entry in enumerate(parsed_reviews, start=1):
            review = entry["review"]
            review_date = entry.get("date")

            # ✅ Fallback to today's date if missing
            if not review_date or review_date.strip() == "":
                review_date = str(date.today())

            print(f"🔍 Processing review {i}/{len(parsed_reviews)}")
            sentiment = analyze_sentiment_ibm(review)
            granite_result = summarize_review(review)

            result.append({
                "original_review": review,
                "summary": granite_result["summary"],
                "predicted_rating": granite_result["predicted_rating"],
                "rating_stars": "⭐" * int(round(granite_result["predicted_rating"])),
                "sentiment": sentiment,
                "date": review_date  # ✅ key renamed to 'date'
            })

        # ✅ Save to output CSV
        os.makedirs("output", exist_ok=True)
        output_path = os.path.join("output", "summaries.csv")

        with open(output_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["original_review", "summary", "predicted_rating", "rating_stars", "sentiment", "date"])
            writer.writeheader()
            writer.writerows(result)

        print(f"✅ Summarization complete. Output saved to: {output_path}")

        return {
            "status": "success",
            "total_reviews": len(result),
            "data": result
        }

    except Exception as e:
        print("❌ Error in /upload/summarize_all:", str(e))
        raise HTTPException(status_code=500, detail=f"Batch summarization failed: {str(e)}")
