import re

def clean_text(text):
    """
    Basic text cleaning: lowercase, remove special chars
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text

def is_crisis(text):
    """
    Detect crisis keywords in text
    """
    keywords = ["suicide", "harm", "hurt myself", "kill"]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)
