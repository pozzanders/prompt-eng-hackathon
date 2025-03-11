def format_profanity_classification_template(text: str) -> str:
    return f"""
    You are an expert classifier, and your mission is to analyze a give text for profanity content.
    Your answer must be in the following Json format:
    {{
        result: bool,
        reason: str,
    }}
    In the result field you either return true or false depending if the given text contains profanity or not.
    In the reason field you provide a short explanation of the profanity, if the result is true.
    
    The given text:
    {text}
    """