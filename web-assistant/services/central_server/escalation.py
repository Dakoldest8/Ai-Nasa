KEYWORDS = [
    "suicide", "kill myself", "self harm",
    "hopeless", "end it", "worthless"
]

def needs_escalation(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in KEYWORDS)

def escalation_message():
    return (
        "I'm really glad you reached out. I can't help with self-harm, "
        "but you are not alone. Please contact local emergency services "
        "or a trusted person right now."
    )
