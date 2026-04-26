import os
import time
import requests
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

DEVICE_NAME = "device_B"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TRAIN_CSV = os.path.join(BASE_DIR, f"crew_{DEVICE_NAME[-1]}_train.csv")
VAL_CSV = os.path.join(BASE_DIR, f"crew_{DEVICE_NAME[-1]}_val.csv")

VECTOR_PATH = os.path.join(
    BASE_DIR, "..", "..", "central_server", "models", "global_vectorizer.joblib"
)

SERVER_URL = "http://127.0.0.1:5000"

def safe_request(url, data=None):
    for _ in range(5):
        try:
            if data:
                return requests.post(url, json=data, timeout=10)
            return requests.get(url, timeout=10)
        except:
            time.sleep(2)
    raise RuntimeError("Server unreachable")

def main():
    train_df = pd.read_csv(TRAIN_CSV)
    val_df = pd.read_csv(VAL_CSV)

    y_train = train_df["Depressed"].astype(int)
    y_val = val_df["Depressed"].astype(int)

    vectorizer = joblib.load(VECTOR_PATH)
    X_train = vectorizer.transform(train_df["text"].fillna(""))
    X_val = vectorizer.transform(val_df["text"].fillna(""))

    model = LogisticRegression(max_iter=300)
    model.fit(X_train, y_train)

    acc = accuracy_score(y_val, model.predict(X_val)) * 100
    print(f"[{DEVICE_NAME}] Local accuracy: {acc:.2f}%")

    payload = {
        "coef": model.coef_.tolist(),
        "intercept": model.intercept_.tolist(),
        "n_samples": len(y_train)
    }

    safe_request(f"{SERVER_URL}/federated_update", payload)
    print(f"[{DEVICE_NAME}] Update sent")

if __name__ == "__main__":
    main()
