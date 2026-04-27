"""
Federated Learning Metrics and Visualization
Tracks accuracy, convergence, and system performance
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class FederatedMetrics:
    """Tracks metrics for federated learning rounds and models"""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path(__file__).parent / "models" / "metrics.json"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.metrics = self._load_metrics()

    def _load_metrics(self) -> Dict:
        """Load metrics from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load metrics: {e}")
                return self._init_metrics()
        return self._init_metrics()

    def _init_metrics(self) -> Dict:
        """Initialize empty metrics structure"""
        return {
            "rounds": [],
            "global_accuracy_history": [],
            "participant_accuracy": {},
            "convergence_data": [],
            "model_stats": {
                "total_rounds": 0,
                "current_round": 0,
                "average_accuracy": 0.0,
                "best_accuracy": 0.0,
                "best_round": 0
            }
        }

    def _save_metrics(self):
        """Save metrics to storage"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def record_round_start(self, round_number: int, participants_count: int):
        """Record the start of a federated learning round"""
        round_data = {
            "round_number": round_number,
            "participants_count": participants_count,
            "started_at": datetime.now().isoformat(),
            "status": "started",
            "accuracy": None,
            "loss": None,
            "convergence_rate": None
        }
        self.metrics["rounds"].append(round_data)
        self.metrics["model_stats"]["current_round"] = round_number
        self.metrics["model_stats"]["total_rounds"] = round_number
        self._save_metrics()

    def record_round_complete(self, round_number: int, accuracy: float, loss: float = None,
                             convergence_rate: float = None):
        """Record metrics for a completed round"""
        # Find and update the round
        for round_data in self.metrics["rounds"]:
            if round_data["round_number"] == round_number:
                round_data["status"] = "completed"
                round_data["accuracy"] = accuracy
                round_data["loss"] = loss
                round_data["convergence_rate"] = convergence_rate
                round_data["completed_at"] = datetime.now().isoformat()

                # Track in history
                self.metrics["global_accuracy_history"].append({
                    "round": round_number,
                    "accuracy": accuracy,
                    "timestamp": datetime.now().isoformat()
                })

                # Update global stats
                accuracies = [r["accuracy"] for r in self.metrics["rounds"] if r["accuracy"] is not None]
                if accuracies:
                    self.metrics["model_stats"]["average_accuracy"] = sum(accuracies) / len(accuracies)
                    max_acc = max(accuracies)
                    self.metrics["model_stats"]["best_accuracy"] = max_acc
                    for r in self.metrics["rounds"]:
                        if r["accuracy"] == max_acc:
                            self.metrics["model_stats"]["best_round"] = r["round_number"]

                break

        self._save_metrics()

    def record_participant_metrics(self, device_id: str, round_number: int,
                                  accuracy: float, loss: float = None, samples: int = 0):
        """Record metrics for a participant in a round"""
        if device_id not in self.metrics["participant_accuracy"]:
            self.metrics["participant_accuracy"][device_id] = []

        self.metrics["participant_accuracy"][device_id].append({
            "round": round_number,
            "accuracy": accuracy,
            "loss": loss,
            "samples": samples,
            "timestamp": datetime.now().isoformat()
        })

        self._save_metrics()

    def record_convergence_data(self, round_number: int, loss: float, gradient_norm: float):
        """Record convergence metrics"""
        self.metrics["convergence_data"].append({
            "round": round_number,
            "loss": loss,
            "gradient_norm": gradient_norm,
            "timestamp": datetime.now().isoformat()
        })
        self._save_metrics()

    def get_accuracy_history(self) -> List[Dict]:
        """Get the accuracy history across all rounds"""
        return self.metrics["global_accuracy_history"]

    def get_round_metrics(self, round_number: int) -> Optional[Dict]:
        """Get metrics for a specific round"""
        for round_data in self.metrics["rounds"]:
            if round_data["round_number"] == round_number:
                return round_data
        return None

    def get_participant_history(self, device_id: str) -> List[Dict]:
        """Get accuracy history for a specific participant"""
        return self.metrics["participant_accuracy"].get(device_id, [])

    def get_convergence_history(self) -> List[Dict]:
        """Get convergence data across all rounds"""
        return self.metrics["convergence_data"]

    def get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        completed_rounds = [r for r in self.metrics["rounds"] if r["status"] == "completed"]
        
        if not completed_rounds:
            return self.metrics["model_stats"]

        accuracies = [r["accuracy"] for r in completed_rounds if r["accuracy"] is not None]
        losses = [r["loss"] for r in completed_rounds if r["loss"] is not None]

        stats = {
            "total_rounds": len(self.metrics["rounds"]),
            "completed_rounds": len(completed_rounds),
            "current_round": self.metrics["model_stats"]["current_round"],
            "average_accuracy": sum(accuracies) / len(accuracies) if accuracies else 0.0,
            "best_accuracy": max(accuracies) if accuracies else 0.0,
            "worst_accuracy": min(accuracies) if accuracies else 0.0,
            "best_round": self.metrics["model_stats"]["best_round"],
            "average_loss": sum(losses) / len(losses) if losses else None,
            "total_participants": len(self.metrics["participant_accuracy"]),
            "timestamp": datetime.now().isoformat()
        }

        return stats

    def get_heatmap_data(self) -> Dict:
        """Get data for participant accuracy heatmap (rounds vs participants)"""
        max_rounds = max([r["round_number"] for r in self.metrics["rounds"]], default=0)
        participants = list(self.metrics["participant_accuracy"].keys())

        heatmap_data = {
            "rounds": list(range(1, max_rounds + 1)),
            "participants": participants,
            "data": []  # 2D array: rounds x participants
        }

        for device_id in participants:
            row = []
            for round_num in range(1, max_rounds + 1):
                # Find accuracy for this participant in this round
                accuracy = None
                for entry in self.metrics["participant_accuracy"][device_id]:
                    if entry["round"] == round_num:
                        accuracy = entry["accuracy"]
                        break
                row.append(accuracy)
            heatmap_data["data"].append(row)

        return heatmap_data

    def get_all_metrics(self) -> Dict:
        """Get all available metrics"""
        return {
            "summary": self.get_summary_stats(),
            "accuracy_history": self.get_accuracy_history(),
            "convergence_data": self.get_convergence_history(),
            "heatmap_data": self.get_heatmap_data(),
            "rounds": self.metrics["rounds"]
        }

# Global metrics instance
_metrics_instance = None

def get_metrics() -> FederatedMetrics:
    """Get or create the global metrics instance"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = FederatedMetrics()
    return _metrics_instance

def reset_metrics():
    """Reset metrics (for testing)"""
    global _metrics_instance
    _metrics_instance = FederatedMetrics()
    return _metrics_instance