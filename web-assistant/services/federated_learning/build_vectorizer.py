# federated_learning/build_vectorizer.py
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# Combine all device train CSVs
csv_files = [
    os.path.join(BASE_DIR, "../devices/device_A/crew_A_train.csv"),
    os.path.join(BASE_DIR, "../devices/device_B/crew_B_train.csv"),
    os.path.join(BASE_DIR, "../devices/device_C/crew_C_train.csv")
]

all_texts = []
for f in csv_files:
    df = pd.read_csv(f)
    all_texts.extend(df["text"].fillna(""))

vectorizer = TfidfVectorizer(max_features=5000)
vectorizer.fit(all_texts)

joblib.dump(vectorizer, os.path.join(MODEL_DIR, "global_vectorizer.joblib"))
print("[Global] Vectorizer built and saved.")
