# granite_handler.py — IBM Granite 3.3-2B Instruct (Public, CPU-friendly)

import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# ✅ Public Granite model for summarization + rating
model_id = model_id = "ibm-granite/granite-7b-base"
local_dir = "./models/granite7b-base"

# ✅ Download and cache model from Hugging Face
from huggingface_hub import snapshot_download
print("📥 Checking model cache or downloading Granite 3.3-2B shards...")
model_path = snapshot_download(
    repo_id=model_id,
    local_dir=local_dir,
    resume_download=True,
    max_workers=2
)

# ✅ Load tokenizer and model from cache
print("🧠 Loading Granite model on CPU...")
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

# ✅ Summarize and rate function
def summarize_and_rate_with_granite(review: str) -> dict:
    """
    Generates a summary and rating prediction for a customer review using Granite 3.3-2B locally.
    """
    prompt = f"""
You are an AI assistant that summarizes customer reviews and predicts a star rating (1–5).

Review: "{review}"

Give your response in this format:
Summary: <summary here>
Predicted Rating: <1–5>
"""

    try:
        print("📝 Generating response from Granite model...")
        inputs = tokenizer(prompt, return_tensors="pt")

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=True,
                temperature=0.7,
                top_k=50,
                top_p=0.9,
                repetition_penalty=1.2,
                early_stopping=True
            )

        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        generated = decoded.replace(prompt.strip(), "").strip()

        # Extract summary and rating from response
        summary_line, rating_line = "Summary not found.", "N/A"
        for line in generated.split("\n"):
            if "summary" in line.lower():
                summary_line = line.split(":", 1)[1].strip()
            elif "rating" in line.lower():
                rating_line = line.split(":", 1)[1].strip()

        return {
            "original_review": review,
            "summary": summary_line,
            "predicted_rating": rating_line
        }

    except Exception as e:
        print("❌ Error during Granite inference:", str(e))
        return {
            "original_review": review,
            "summary": "Error occurred.",
            "predicted_rating": "N/A",
            "error": str(e)
        }
