from transformers import AutoTokenizer, AutoModelForCausalLM
from app.ollama_handler import summarize_with_ollama
import torch
import re

# ✅ IBM Granite 7B (Hugging Face model)
MODEL_ID = "ibm-granite/granite-7b-base"
print("📥 [INIT] Loading IBM Granite 7B model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID)


def summarize_review(review: str) -> dict:
    """
    Attempts to summarize a review and predict a rating using Granite.
    Falls back to Ollama if Granite fails or is disabled.
    """
    prompt = f"""
You are an AI assistant that summarizes customer reviews and predicts a star rating (1–5).

Review: "{review}"

Give your response in this format:
Summary: <summary>
Predicted Rating: <1–5>
"""

    try:
        # ❌ Temporarily disable Granite and force fallback to Ollama
        raise RuntimeError("Granite enabled merging with Ollama fallback.")

        # ✅ Uncomment to enable Granite execution later:
        """
        inputs = tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.7,
                top_k=50,
                top_p=0.9,
                repetition_penalty=1.2,
                pad_token_id=tokenizer.eos_token_id
            )

        full_output = tokenizer.decode(output[0], skip_special_tokens=True)
        return parse_granite_output(full_output)
        """

    except Exception as e:
        print("⚠️ Parsing Granite review :", str(e))
        result = summarize_with_ollama(review)

        # ✅ Safe rating extraction
        result["predicted_rating"] = try_parse_rating(str(result.get("predicted_rating", "")))

        # ✅ Ensure summary is present
        result["summary"] = result.get("summary", "Summary not found")

        return result


def parse_granite_output(output: str) -> dict:
    """
    Extracts structured summary and rating from Granite raw output.
    """
    summary = "Could not extract summary"
    rating = "N/A"

    for line in output.splitlines():
        if line.lower().startswith("summary:"):
            summary = line.split(":", 1)[1].strip()
        elif "predicted rating" in line.lower():
            rating = line.split(":", 1)[1].strip()

    return {
        "summary": summary,
        "predicted_rating": try_parse_rating(rating),
        "engine_used": "granite"
    }


def try_parse_rating(value: str):
    """
    Safely extracts a float rating from strings like '3', '4.5', 'Rating: 3.0', etc.
    """
    if not isinstance(value, str):
        value = str(value)

    match = re.search(r"\d+(\.\d+)?", value)
    if match:
        try:
            return round(float(match.group()), 1)
        except:
            return "N/A"
    return "N/A"
