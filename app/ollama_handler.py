import requests
import re

def summarize_with_ollama(review: str) -> dict:
    """
    Uses Ollama REST API (localhost:11434) to summarize and rate a review.
    """

    prompt = f"""
Summarize the following customer review and predict a star rating (1–5):

Review: "{review}"

Respond in this format:
Summary: <summary>
Predicted Rating: <1–5>
"""

    print("⚙️ [Ollama] Sending prompt to REST API...")

    try:
        response = requests.post(
            url="http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            },
            timeout=90  # ⏱️ Handles cold start or large input
        )

        response.raise_for_status()
        raw = response.json()["response"]
        print("📤 Ollama and Granite response:\n", raw)

        # ✅ Extract summary using flexible regex (robust across line formats)
        summary_match = re.search(r"summary:\s*(.+?)(?:\n|$)", raw, re.IGNORECASE | re.DOTALL)
        rating_match = re.search(r"predicted rating:\s*([0-9.]+)", raw, re.IGNORECASE)

        summary = summary_match.group(1).strip() if summary_match else "Summary not found"
        rating = rating_match.group(1).strip() if rating_match else "N/A"

        return {
            "original_review": review,
            "summary": summary,
            "predicted_rating": try_parse_rating(rating),
            "engine_used": "ollama"
        }

    except requests.exceptions.Timeout:
        print("⏱️ Ollama timed out after 90 seconds.")
        return {
            "original_review": review,
            "summary": "Timed out while generating response from Ollama.",
            "predicted_rating": "N/A",
            "engine_used": "ollama"
        }

    except Exception as e:
        print("❌ Ollama REST API error:", str(e))
        return {
            "original_review": review,
            "summary": "Error from Ollama API.",
            "predicted_rating": "N/A",
            "engine_used": "ollama",
            "error": str(e)
        }

# ✅ Rating parser helper
def try_parse_rating(value: str):
    """
    Safely extracts numeric rating from strings like:
    '4.5', '3/5', 'Rating: 4.0', 'Predicted Rating: 5'
    """
    if not value or not isinstance(value, str):
        return "N/A"

    match = re.search(r"\d+(\.\d+)?", value)
    if match:
        try:
            return round(float(match.group()), 1)
        except:
            return "N/A"

    return "N/A"
