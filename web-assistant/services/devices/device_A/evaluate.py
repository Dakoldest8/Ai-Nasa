import joblib, pandas as pd
from federated_learning.evaluation_metrics import metrics

model = joblib.load("../../central_server/models/mental_health_classifier.joblib")
df = pd.read_csv("crew_A.csv")

X = df.drop(columns=["Depressed"])
y = df["Depressed"]

pred = model.predict(X)
print(metrics(y, pred))
