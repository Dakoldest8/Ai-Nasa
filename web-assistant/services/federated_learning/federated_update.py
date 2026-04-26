import numpy as np


# -----------------------------
# Initialize Global Model
# -----------------------------
def initialize_global():
    """
    Create an empty global model state.
    """
    return {
        "coef": None,
        "intercept": None,
        "n_samples": 0
    }


# -----------------------------
# Federated Averaging (FedAvg)
# -----------------------------
def aggregate(global_model, update):
    """
    Perform Federated Averaging (FedAvg).

    update = {
        "coef_delta": [[...]],
        "intercept_delta": [...],
        "n_samples": int
    }
    """

    coef_delta = np.array(update["coef_delta"])
    intercept_delta = np.array(update["intercept_delta"])
    n_samples = update["n_samples"]

    # First update initializes model
    if global_model["coef"] is None:
        global_model["coef"] = coef_delta
        global_model["intercept"] = intercept_delta
        global_model["n_samples"] = n_samples
        return global_model

    # Weighted average
    total_samples = global_model["n_samples"] + n_samples

    global_model["coef"] = (
        global_model["coef"] * global_model["n_samples"] +
        coef_delta * n_samples
    ) / total_samples

    global_model["intercept"] = (
        global_model["intercept"] * global_model["n_samples"] +
        intercept_delta * n_samples
    ) / total_samples

    global_model["n_samples"] = total_samples

    return global_model
