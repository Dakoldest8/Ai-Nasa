import pandas as pd
import random
import os

# -----------------------------
# Original small crew data template
# -----------------------------
template_data = [
    {"text": "I feel exhausted after long mission tasks", "Depressed": 1, "sleep_hours": 5, "mood": 2, "workload": 8},
    {"text": "Hard to focus today, very tired", "Depressed": 1, "sleep_hours": 4, "mood": 2, "workload": 9},
    {"text": "Completed tasks but feeling worn out", "Depressed": 1, "sleep_hours": 5, "mood": 3, "workload": 7},
    {"text": "Mission was productive but draining", "Depressed": 0, "sleep_hours": 6, "mood": 3, "workload": 7},
    {"text": "Short rest helped a little", "Depressed": 0, "sleep_hours": 6, "mood": 4, "workload": 6},
    {"text": "Energy improving after better sleep", "Depressed": 0, "sleep_hours": 7, "mood": 4, "workload": 5},
    {"text": "Good focus during system checks", "Depressed": 0, "sleep_hours": 7, "mood": 5, "workload": 5},
    {"text": "Feeling stable and alert today", "Depressed": 0, "sleep_hours": 8, "mood": 5, "workload": 4},
]

# -----------------------------
# Function to create synthetic text variations
# -----------------------------
def augment_text(text):
    variations = [
        text,
        text.replace("feeling", "feels"),
        text.replace("today", "this morning"),
        text.replace("tasks", "duties"),
        text.replace("after", "following"),
        text.replace("short rest", "quick nap"),
    ]
    return random.choice(variations)

# -----------------------------
# Generate dataset function
# -----------------------------
def generate_dataset(template, n_rows=8000, val_rows_count=2000, crew_name="A"):
    train_data = []
    val_data = []

    # Generate training rows
    for _ in range(n_rows):
        row = random.choice(template).copy()
        row["text"] = augment_text(row["text"])
        row["sleep_hours"] = max(3, min(10, row["sleep_hours"] + random.randint(-1,1)))
        row["mood"] = max(1, min(5, row["mood"] + random.randint(-1,1)))
        row["workload"] = max(1, min(10, row["workload"] + random.randint(-2,2)))
        train_data.append(row)

    # Generate validation rows
    for _ in range(val_rows_count):
        row = random.choice(template).copy()
        row["text"] = augment_text(row["text"])
        row["sleep_hours"] = max(3, min(10, row["sleep_hours"] + random.randint(-1,1)))
        row["mood"] = max(1, min(5, row["mood"] + random.randint(-1,1)))
        row["workload"] = max(1, min(10, row["workload"] + random.randint(-2,2)))
        val_data.append(row)

    # Create DataFrames
    train_df = pd.DataFrame(train_data)
    val_df = pd.DataFrame(val_data)

    # Save CSVs
    os.makedirs("datasets", exist_ok=True)
    train_path = os.path.join("datasets", f"crew_{crew_name}_train.csv")
    val_path = os.path.join("datasets", f"crew_{crew_name}_val.csv")
    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)

    print(f"Generated {train_path} ({len(train_df)} rows)")
    print(f"Generated {val_path} ({len(val_df)} rows)")

# -----------------------------
# Generate datasets for Crew A, B, C
# -----------------------------
for crew in ["A", "B", "C"]:
    generate_dataset(template_data, n_rows=8000, val_rows_count=2000, crew_name=crew)
