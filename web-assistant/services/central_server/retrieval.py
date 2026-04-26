import pandas as pd

DATASETS = {
    "mental": "datasets/medical_records_train_8000.csv",
    "fitness": "datasets/space_exercise_train_8000.csv",
    "nutrition": "datasets/iss_nutrition_train.csv"
}

def retrieve(domain, n=3):
    if domain not in DATASETS:
        return ""
    df = pd.read_csv(DATASETS[domain])
    return "\n".join(df.head(n).astype(str).agg(" ".join, axis=1))
