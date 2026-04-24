"""
Phase 7: Federated Learning
Privacy-preserving collaborative model training across devices
"""

import os
import json
import logging
import hashlib
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import threading
import time

logger = logging.getLogger(__name__)

class FederatedCoordinator:
    """Coordinates federated learning across multiple devices"""

    def __init__(self, min_participants: int = 3, max_rounds: int = 10,
                 aggregation_strategy: str = "fedavg"):
        self.min_participants = min_participants
        self.max_rounds = max_rounds
        self.aggregation_strategy = aggregation_strategy
        self.current_round = 0
        self.participants = {}  # device_id -> participant info
        self.global_model = None
        self.rounds_history = []

    def register_participant(self, device_id: str, device_info: Dict) -> str:
        """Register a device as a federated learning participant"""
        participant_id = f"participant_{len(self.participants) + 1}"

        self.participants[device_id] = {
            "participant_id": participant_id,
            "device_info": device_info,
            "registered_at": datetime.now().isoformat(),
            "status": "registered",
            "contributions": []
        }

        logger.info(f"Registered participant {participant_id} for device {device_id}")
        return participant_id

    def start_federated_round(self) -> bool:
        """Start a new federated learning round"""
        if len(self.participants) < self.min_participants:
            logger.warning(f"Not enough participants: {len(self.participants)} < {self.min_participants}")
            return False

        self.current_round += 1
        round_id = f"round_{self.current_round}"

        # Reset participant statuses for new round
        for participant in self.participants.values():
            participant["status"] = "waiting"
            participant["current_round"] = round_id

        self.rounds_history.append({
            "round_id": round_id,
            "started_at": datetime.now().isoformat(),
            "participants": list(self.participants.keys()),
            "status": "active"
        })

        logger.info(f"Started federated learning round {round_id}")
        return True

    def submit_model_update(self, device_id: str, model_update: Dict) -> bool:
        """Submit a model update from a participant"""
        if device_id not in self.participants:
            logger.error(f"Unknown participant: {device_id}")
            return False

        participant = self.participants[device_id]

        # Validate update
        if not self._validate_model_update(model_update):
            logger.error(f"Invalid model update from {device_id}")
            return False

        # Store contribution
        contribution = {
            "round_id": participant.get("current_round"),
            "submitted_at": datetime.now().isoformat(),
            "model_update": model_update,
            "status": "submitted"
        }

        participant["contributions"].append(contribution)
        participant["status"] = "contributed"

        logger.info(f"Received model update from {device_id}")
        return True

    def aggregate_updates(self) -> Optional[Dict]:
        """Aggregate model updates from all participants"""
        active_participants = [p for p in self.participants.values() if p["status"] == "contributed"]

        if len(active_participants) < self.min_participants:
            logger.warning(f"Not enough contributions: {len(active_participants)} < {self.min_participants}")
            return None

        # Extract model updates
        updates = []
        for participant in active_participants:
            latest_contribution = participant["contributions"][-1]
            updates.append(latest_contribution["model_update"])

        # Aggregate based on strategy
        if self.aggregation_strategy == "fedavg":
            aggregated = self._federated_average(updates)
        elif self.aggregation_strategy == "median":
            aggregated = self._median_aggregation(updates)
        else:
            logger.error(f"Unknown aggregation strategy: {self.aggregation_strategy}")
            return None

        # Update global model
        self.global_model = aggregated

        # Update round status
        current_round = self.rounds_history[-1]
        current_round["status"] = "completed"
        current_round["completed_at"] = datetime.now().isoformat()
        current_round["aggregated_model"] = aggregated

        logger.info(f"Successfully aggregated updates from {len(updates)} participants")
        return aggregated

    def _federated_average(self, updates: List[Dict]) -> Dict:
        """Federated averaging aggregation"""
        if not updates:
            return {}

        # Simple weighted average (equal weights for demo)
        aggregated = {}
        num_updates = len(updates)

        for key in updates[0].keys():
            if isinstance(updates[0][key], (int, float)):
                # Numerical aggregation
                values = [update.get(key, 0) for update in updates]
                aggregated[key] = sum(values) / num_updates
            elif isinstance(updates[0][key], list):
                # List/vector aggregation
                values = [np.array(update.get(key, [])) for update in updates]
                aggregated[key] = np.mean(values, axis=0).tolist()
            else:
                # Keep first value for non-numerical
                aggregated[key] = updates[0][key]

        return aggregated

    def _median_aggregation(self, updates: List[Dict]) -> Dict:
        """Median-based aggregation (more robust to outliers)"""
        if not updates:
            return {}

        aggregated = {}

        for key in updates[0].keys():
            if isinstance(updates[0][key], (int, float)):
                values = [update.get(key, 0) for update in updates]
                aggregated[key] = np.median(values)
            else:
                # Keep first value for non-numerical
                aggregated[key] = updates[0][key]

        return aggregated

    def _validate_model_update(self, update: Dict) -> bool:
        """Validate a model update"""
        required_fields = ["model_version", "update_data"]
        return all(field in update for field in required_fields)

    def get_federated_status(self) -> Dict:
        """Get current federated learning status"""
        return {
            "current_round": self.current_round,
            "total_participants": len(self.participants),
            "active_participants": len([p for p in self.participants.values() if p["status"] == "contributed"]),
            "min_participants": self.min_participants,
            "aggregation_strategy": self.aggregation_strategy,
            "rounds_completed": len([r for r in self.rounds_history if r["status"] == "completed"]),
            "global_model_available": self.global_model is not None
        }

class PrivacyEngine:
    """Handles privacy-preserving techniques for federated learning"""

    def __init__(self, noise_multiplier: float = 0.1, max_grad_norm: float = 1.0):
        self.noise_multiplier = noise_multiplier
        self.max_grad_norm = max_grad_norm

    def add_differential_privacy(self, gradients: Dict[str, Any]) -> Dict[str, Any]:
        """Add differential privacy noise to gradients"""
        privatized = {}

        for key, grad in gradients.items():
            if isinstance(grad, (int, float)):
                # Add Gaussian noise
                noise = np.random.normal(0, self.noise_multiplier)
                privatized[key] = grad + noise
            elif isinstance(grad, list):
                # Add noise to vector
                grad_array = np.array(grad)
                noise = np.random.normal(0, self.noise_multiplier, size=grad_array.shape)
                privatized[key] = (grad_array + noise).tolist()
            else:
                privatized[key] = grad

        return privatized

    def clip_gradients(self, gradients: Dict[str, Any]) -> Dict[str, Any]:
        """Clip gradients to prevent information leakage"""
        clipped = {}

        for key, grad in gradients.items():
            if isinstance(grad, (int, float)):
                # Clip scalar
                clipped[key] = np.clip(grad, -self.max_grad_norm, self.max_grad_norm)
            elif isinstance(grad, list):
                # Clip vector
                grad_array = np.array(grad)
                grad_norm = np.linalg.norm(grad_array)
                if grad_norm > self.max_grad_norm:
                    grad_array = grad_array * (self.max_grad_norm / grad_norm)
                clipped[key] = grad_array.tolist()
            else:
                clipped[key] = grad

        return clipped

class FederatedParticipant:
    """Represents a device participating in federated learning"""

    def __init__(self, device_id: str, coordinator_url: str, local_data_size: int = 100):
        self.device_id = device_id
        self.coordinator_url = coordinator_url
        self.local_data_size = local_data_size
        self.participant_id = None
        self.local_model = None
        self.privacy_engine = PrivacyEngine()

    def register_with_coordinator(self) -> bool:
        """Register with the federated learning coordinator"""
        try:
            # Simulate registration request
            device_info = {
                "device_type": "raspberry_pi",
                "data_size": self.local_data_size,
                "capabilities": ["training", "inference"]
            }

            # In real implementation, make HTTP request to coordinator
            # For demo, simulate successful registration
            self.participant_id = f"participant_{hash(self.device_id) % 1000}"

            logger.info(f"Registered with coordinator as {self.participant_id}")
            return True

        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return False

    def train_local_model(self, global_model: Dict) -> Dict:
        """Train local model on private data"""
        try:
            # Initialize with global model
            self.local_model = global_model.copy()

            # Simulate local training
            # In real implementation: train on local dataset
            gradients = self._simulate_local_training()

            # Apply privacy techniques
            private_gradients = self.privacy_engine.clip_gradients(gradients)
            private_gradients = self.privacy_engine.add_differential_privacy(private_gradients)

            model_update = {
                "participant_id": self.participant_id,
                "model_version": global_model.get("version", 1),
                "update_data": private_gradients,
                "data_size": self.local_data_size,
                "training_rounds": 1
            }

            return model_update

        except Exception as e:
            logger.error(f"Local training failed: {e}")
            return {}

    def _simulate_local_training(self) -> Dict:
        """Simulate local training gradients"""
        # Generate mock gradients
        return {
            "layer1_weights": np.random.normal(0, 0.1, 100).tolist(),
            "layer1_bias": np.random.normal(0, 0.1, 10).tolist(),
            "layer2_weights": np.random.normal(0, 0.1, 50).tolist(),
            "layer2_bias": np.random.normal(0, 0.1, 5).tolist(),
            "learning_rate": 0.01,
            "loss": 0.5 + np.random.normal(0, 0.1)
        }

    def submit_update(self, model_update: Dict) -> bool:
        """Submit model update to coordinator"""
        try:
            # In real implementation, make HTTP request to coordinator
            # For demo, simulate successful submission
            logger.info(f"Submitted model update to coordinator")
            return True

        except Exception as e:
            logger.error(f"Update submission failed: {e}")
            return False

# Global instances
federated_coordinator = FederatedCoordinator()
privacy_engine = PrivacyEngine()

def get_federated_coordinator() -> FederatedCoordinator:
    """Get the global federated learning coordinator"""
    return federated_coordinator

def get_privacy_engine() -> PrivacyEngine:
    """Get the global privacy engine"""
    return privacy_engine