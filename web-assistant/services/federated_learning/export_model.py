import requests, joblib, numpy as np, os, time

os.makedirs("central_server/models", exist_ok=True)
url = "http://127.0.0.1:5000/global_model"

for i in range(20):
    try:
        m = requests.get(url).json()
        break
    except requests.exceptions.ConnectionError:
        print("Federated server not ready, retrying in 2s...")
        time.sleep(2)
else:
    raise RuntimeError("Cannot connect to federated server.")

joblib.dump(
    {"coef": np.array(m["coef"]), "intercept": np.array(m["intercept"])},
    "central_server/models/mental_health_classifier.joblib"
)
print("Global model exported to central_server/models/mental_health_classifier.joblib")
