import joblib
import numpy as np
try:
    from ..memory import save_memory
except ImportError:
    from memory import save_memory
import os

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "../central_server/models/mental_health_classifier.joblib")
VECTORIZER_PATH = os.path.join(BASE_DIR, "../central_server/models/global_vectorizer.joblib")

# Load model and vectorizer
model_data = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

def handle(user_id: str, text: str, memory: dict, llm) -> dict:
    """
    Predict depression risk from user text and update memory.
    """
    X = vectorizer.transform([text])
    coef = model_data.get("coef")
    intercept = model_data.get("intercept")

    if coef is not None and intercept is not None:
        pred = X.dot(coef.T) + intercept
        pred_label = int(pred[0][0] > 0.5)
        response = "Depression risk detected" if pred_label else "No immediate risk detected"
    else:
        pred_label = None
        response = "Model not trained yet"

    if memory is None:
        memory = {}
    memory["mental_health"] = {
        "last_text": text,
        "risk_detected": bool(pred_label) if pred_label is not None else None
    }

    save_memory("users", user_id, memory)

    return {"response": response, "memory": memory}
