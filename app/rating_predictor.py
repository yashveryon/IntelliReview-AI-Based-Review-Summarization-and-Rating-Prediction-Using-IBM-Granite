def predict_rating(text: str) -> int:
    """
    Heuristic-based placeholder for rating prediction.
    Simulates star ratings (1 to 5) based on review sentiment keywords.
    Intended for replacement with AI model or IBM Granite output.
    """

    text_lower = text.lower()

    # Positive sentiment indicators
    positive_keywords = ["excellent", "amazing", "perfect", "great", "fantastic", "loved", "wonderful", "outstanding", "superb"]
    negative_keywords = ["terrible", "horrible", "bad", "poor", "worst", "disappointed", "awful", "unacceptable"]
    neutral_keywords = ["okay", "average", "fine", "decent", "mediocre"]

    score = 3  # Default neutral score

    # Adjust score based on keyword matches
    if any(word in text_lower for word in positive_keywords):
        score += 1
    if any(word in text_lower for word in negative_keywords):
        score -= 1
    if any(word in text_lower for word in neutral_keywords):
        score = 3

    # Bound the score within 1 to 5
    return max(1, min(5, score))
