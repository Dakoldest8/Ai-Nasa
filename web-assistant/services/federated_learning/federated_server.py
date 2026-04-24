from flask import Flask, request, jsonify
import numpy as np
import os
import joblib

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CENTRAL_MODEL_PATH = os.path.join(
    BASE_DIR, "..", "central_server", "models", "mental_health_classifier.joblib"
)

GLOBAL = {
    "coef": None,
    "intercept": None,
    "n_samples": 0
}

def aggregate(global_model, update):
    coef = np.array(update["coef"])
    intercept = np.array(update["intercept"])
    n = update["n_samples"]

    if global_model["coef"] is None:
        global_model["coef"] = coef
        global_model["intercept"] = intercept
        global_model["n_samples"] = n
    else:
        total = global_model["n_samples"] + n
        global_model["coef"] = (
            global_model["coef"] * global_model["n_samples"] + coef * n
        ) / total
        global_model["intercept"] = (
            global_model["intercept"] * global_model["n_samples"] + intercept * n
        ) / total
        global_model["n_samples"] = total

    return global_model

@app.route("/global_model", methods=["GET"])
def get_global_model():
    if os.path.exists(CENTRAL_MODEL_PATH):
        model = joblib.load(CENTRAL_MODEL_PATH)
        return jsonify({
            "coef": model["coef"].tolist(),
            "intercept": model["intercept"].tolist()
        })
    return jsonify({"coef": None, "intercept": None})

@app.route("/federated_update", methods=["POST"])
def federated_update():
    global GLOBAL
    update = request.json

    GLOBAL = aggregate(GLOBAL, update)

    os.makedirs(os.path.dirname(CENTRAL_MODEL_PATH), exist_ok=True)
    joblib.dump(
        {"coef": GLOBAL["coef"], "intercept": GLOBAL["intercept"]},
        CENTRAL_MODEL_PATH
    )

    print("[Federated] Global model updated & saved")

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000)
