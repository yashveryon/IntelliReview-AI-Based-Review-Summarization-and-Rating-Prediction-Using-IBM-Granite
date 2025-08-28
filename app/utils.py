import re

def validate_review(text: str) -> bool:
    """
    Validates a single review text.
    Returns True if the text is valid (non-empty and meaningful), else False.
    """
    if not text or len(text.strip()) < 10:
        return False
    return True

def clean_text(text: str) -> str:
    """
    Cleans and standardizes review text by removing extra spaces,
    unwanted characters, and line breaks.
    """
    # Remove multiple spaces and newlines
    cleaned = re.sub(r'\s+', ' ', text)
    cleaned = cleaned.strip()
    return cleaned
