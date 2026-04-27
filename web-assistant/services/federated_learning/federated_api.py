"""
Phase 7: Federated Learning API
REST endpoints for federated learning coordination and participation
"""

from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Any
import time

logger = logging.getLogger(__name__)

# Import federated learning components
try:
    from services.federated_learning.federated_core import (
        get_federated_coordinator,
        get_privacy_engine,
        FederatedParticipant
    )
    from services.federated_learning.metrics import get_metrics
except ImportError:
    logger.warning("Federated learning modules not available")
    get_federated_coordinator = None
    get_privacy_engine = None
    FederatedParticipant = None
    get_metrics = None

fed_bp = Blueprint('federated', __name__, url_prefix='/federated')

@fed_bp.route('/register', methods=['POST'])
def register_participant():
    """Register a device as a federated learning participant"""
    if not get_federated_coordinator:
        return jsonify({"error": "Federated learning not available"}), 503

    try:
        data = request.get_json()
        if not data or 'device_id' not in data:
            return jsonify({"error": "device_id required"}), 400

        device_id = data['device_id']
        device_info = data.get('device_info', {})

        coordinator = get_federated_coordinator()
        participant_id = coordinator.register_participant(device_id, device_info)

        return jsonify({
            "status": "success",
            "participant_id": participant_id,
            "message": f"Device {device_id} registered as participant {participant_id}"
        })

    except Exception as e:
        logger.error(f"Participant registration failed: {e}")
        return jsonify({"error": str(e)}), 500

@fed_bp.route('/round/start', methods=['POST'])
def start_round():
    """Start a new federated learning round"""
    if not get_federated_coordinator:
        return jsonify({"error": "Federated learning not available"}), 503

    try:
        coordinator = get_federated_coordinator()
        success = coordinator.start_federated_round()

        if success:
            return jsonify({
                "status": "success",
                "round_number": coordinator.current_round,
                "message": f"Started federated learning round {coordinator.current_round}"
            })
        else:
            return jsonify({"error": "Failed to start round - not enough participants"}), 400

    except Exception as e:
        logger.error(f"Round start failed: {e}")
        return jsonify({"error": str(e)}), 500

@fed_bp.route('/update/submit', methods=['POST'])
def submit_update():
    """Submit a model update from a participant"""
    if not get_federated_coordinator:
        return jsonify({"error": "Federated learning not available"}), 503

    try:
        data = request.get_json()
        if not data or 'device_id' not in data or 'model_update' not in data:
            return jsonify({"error": "device_id and model_update required"}), 400

        device_id = data['device_id']
        model_update = data['model_update']

        coordinator = get_federated_coordinator()
        success = coordinator.submit_model_update(device_id, model_update)

        if success:
            return jsonify({
                "status": "success",
                "message": f"Model update accepted from {device_id}"
            })
        else:
            return jsonify({"error": "Update submission failed"}), 400

    except Exception as e:
        logger.error(f"Update submission failed: {e}")
        return jsonify({"error": str(e)}), 500

@fed_bp.route('/round/aggregate', methods=['POST'])
def aggregate_updates():
    """Aggregate model updates and create new global model"""
    if not get_federated_coordinator:
        return jsonify({"error": "Federated learning not available"}), 503

    try:
        coordinator = get_federated_coordinator()
        aggregated_model = coordinator.aggregate_updates()

        if aggregated_model:
            return jsonify({
                "status": "success",
                "aggregated_model": aggregated_model,
                "round_number": coordinator.current_round,
                "message": "Model updates aggregated successfully"
            })
        else:
            return jsonify({"error": "Aggregation failed - not enough contributions"}), 400

    except Exception as e:
        logger.error(f"Aggregation failed: {e}")
        return jsonify({"error": str(e)}), 500

@fed_bp.route('/status', methods=['GET'])
def get_status():
    """Get current federated learning status"""
    if not get_federated_coordinator:
        return jsonify({"error": "Federated learning not available"}), 503

    try:
        coordinator = get_federated_coordinator()
        status = coordinator.get_federated_status()

        return jsonify({
            "status": "success",
            "federated_status": status
        })

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return jsonify({"error": str(e)}), 500

@fed_bp.route('/model/global', methods=['GET'])
def get_global_model():
    """Get the current global model"""
    if not get_federated_coordinator:
        return jsonify({"error": "Federated learning not available"}), 503

    try:
        coordinator = get_federated_coordinator()

        if coordinator.global_model:
            return jsonify({
                "status": "success",
                "global_model": coordinator.global_model,
                "round_number": coordinator.current_round
            })
        else:
            return jsonify({"error": "No global model available"}), 404

    except Exception as e:
        logger.error(f"Global model retrieval failed: {e}")
        return jsonify({"error": str(e)}), 500

@fed_bp.route('/participants', methods=['GET'])
def list_participants():
    """List all registered participants"""
    if not get_federated_coordinator:
        return jsonify({"error": "Federated learning not available"}), 503

    try:
        coordinator = get_federated_coordinator()
        participants = {}

        for device_id, participant in coordinator.participants.items():
            participants[device_id] = {
                "participant_id": participant["participant_id"],
                "status": participant["status"],
                "registered_at": participant["registered_at"],
                "contributions_count": len(participant["contributions"])
            }

        return jsonify({
            "status": "success",
            "participants": participants
        })

    except Exception as e:
        logger.error(f"Participants list failed: {e}")
        return jsonify({"error": str(e)}), 500

@fed_bp.route('/privacy/test', methods=['POST'])
def test_privacy():
    """Test privacy-preserving techniques"""
    if not get_privacy_engine:
        return jsonify({"error": "Privacy engine not available"}), 503

    try:
        data = request.get_json()
        if not data or 'gradients' not in data:
            return jsonify({"error": "gradients required"}), 400

        gradients = data['gradients']
        privacy_engine = get_privacy_engine()

        # Apply privacy techniques
        clipped = privacy_engine.clip_gradients(gradients)
        privatized = privacy_engine.add_differential_privacy(clipped)

        return jsonify({
            "status": "success",
            "original_gradients": gradients,
            "clipped_gradients": clipped,
            "privatized_gradients": privatized,
            "message": "Privacy techniques applied successfully"
        })

    except Exception as e:
        logger.error(f"Privacy test failed: {e}")
        return jsonify({"error": str(e)}), 500

@fed_bp.route('/participant/simulate', methods=['POST'])
def simulate_participant():
    """Simulate a federated learning participant (for testing)"""
    if not FederatedParticipant:
        return jsonify({"error": "Federated participant not available"}), 503

    try:
        data = request.get_json()
        device_id = data.get('device_id', f'simulated_device_{int(time.time())}')
        coordinator_url = data.get('coordinator_url', 'http://localhost:8000')

        # Create simulated participant
        participant = FederatedParticipant(device_id, coordinator_url)

        # Register with coordinator
        registered = participant.register_with_coordinator()
        if not registered:
            return jsonify({"error": "Participant registration failed"}), 500

        # Get global model (simulated)
        global_model = {"version": 1, "weights": [0.1, 0.2, 0.3]}

        # Train local model
        model_update = participant.train_local_model(global_model)

        # Submit update
        submitted = participant.submit_update(model_update)

        return jsonify({
            "status": "success",
            "device_id": device_id,
            "participant_id": participant.participant_id,
            "registered": registered,
            "trained": bool(model_update),
            "submitted": submitted,
            "message": "Participant simulation completed"
        })

    except Exception as e:
        logger.error(f"Participant simulation failed: {e}")
        return jsonify({"error": str(e)}), 500

# Metrics Endpoints
@fed_bp.route('/metrics/all', methods=['GET'])
def get_all_metrics():
    """Get all federated learning metrics and visualizations"""
    if not get_metrics:
        return jsonify({"error": "Metrics not available"}), 503

    try:
        metrics = get_metrics()
        all_metrics = metrics.get_all_metrics()

        return jsonify({
            "status": "success",
            "metrics": all_metrics
        })

    except Exception as e:
        logger.error(f"Failed to retrieve metrics: {e}")
        return jsonify({"error": str(e)}), 500

@fed_bp.route('/metrics/summary', methods=['GET'])
def get_metrics_summary():
    """Get summary statistics for federated learning"""
    if not get_metrics:
        return jsonify({"error": "Metrics not available"}), 503

    try:
        metrics = get_metrics()
        summary = metrics.get_summary_stats()

        return jsonify({
            "status": "success",
            "summary": summary
        })

    except Exception as e:
        logger.error(f"Failed to retrieve summary: {e}")
        return jsonify({"error": str(e)}), 500

@fed_bp.route('/metrics/accuracy', methods=['GET'])
def get_accuracy_metrics():
    """Get accuracy history for visualization"""
    if not get_metrics:
        return jsonify({"error": "Metrics not available"}), 503

    try:
        metrics = get_metrics()
        accuracy_history = metrics.get_accuracy_history()

        return jsonify({
            "status": "success",
            "accuracy_history": accuracy_history
        })

    except Exception as e:
        logger.error(f"Failed to retrieve accuracy metrics: {e}")
        return jsonify({"error": str(e)}), 500

@fed_bp.route('/metrics/convergence', methods=['GET'])
def get_convergence_metrics():
    """Get convergence data for loss curve visualization"""
    if not get_metrics:
        return jsonify({"error": "Metrics not available"}), 503

    try:
        metrics = get_metrics()
        convergence_data = metrics.get_convergence_history()

        return jsonify({
            "status": "success",
            "convergence_data": convergence_data
        })

    except Exception as e:
        logger.error(f"Failed to retrieve convergence metrics: {e}")
        return jsonify({"error": str(e)}), 500

@fed_bp.route('/metrics/heatmap', methods=['GET'])
def get_heatmap_metrics():
    """Get heatmap data showing participant accuracy across rounds"""
    if not get_metrics:
        return jsonify({"error": "Metrics not available"}), 503

    try:
        metrics = get_metrics()
        heatmap_data = metrics.get_heatmap_data()

        return jsonify({
            "status": "success",
            "heatmap": heatmap_data
        })

    except Exception as e:
        logger.error(f"Failed to retrieve heatmap data: {e}")
        return jsonify({"error": str(e)}), 500

@fed_bp.route('/metrics/record-round', methods=['POST'])
def record_round_metrics():
    """Record metrics for a completed federated learning round"""
    if not get_metrics:
        return jsonify({"error": "Metrics not available"}), 503

    try:
        data = request.get_json()
        round_number = data.get('round_number')
        accuracy = data.get('accuracy')
        loss = data.get('loss')
        convergence_rate = data.get('convergence_rate')

        if round_number is None or accuracy is None:
            return jsonify({"error": "round_number and accuracy required"}), 400

        metrics = get_metrics()
        metrics.record_round_complete(round_number, accuracy, loss, convergence_rate)

        return jsonify({
            "status": "success",
            "message": f"Metrics recorded for round {round_number}"
        })

    except Exception as e:
        logger.error(f"Failed to record round metrics: {e}")
        return jsonify({"error": str(e)}), 500

@fed_bp.route('/metrics/record-participant', methods=['POST'])
def record_participant_metrics():
    """Record metrics for a participant in a round"""
    if not get_metrics:
        return jsonify({"error": "Metrics not available"}), 503

    try:
        data = request.get_json()
        device_id = data.get('device_id')
        round_number = data.get('round_number')
        accuracy = data.get('accuracy')
        loss = data.get('loss')
        samples = data.get('samples', 0)

        if not device_id or round_number is None or accuracy is None:
            return jsonify({"error": "device_id, round_number, and accuracy required"}), 400

        metrics = get_metrics()
        metrics.record_participant_metrics(device_id, round_number, accuracy, loss, samples)

        return jsonify({
            "status": "success",
            "message": f"Metrics recorded for {device_id} in round {round_number}"
        })

    except Exception as e:
        logger.error(f"Failed to record participant metrics: {e}")
        return jsonify({"error": str(e)}), 500
    """Register federated learning endpoints with Flask app"""
    try:
        app.register_blueprint(fed_bp)
        logger.info("Federated learning endpoints registered")
    except Exception as e:
        logger.error(f"Failed to register federated endpoints: {e}")

# Export for external use
__all__ = ['register_federated_endpoints']