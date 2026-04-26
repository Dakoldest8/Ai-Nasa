"""
Phase 3: Training API
REST API endpoints for training triggers and automated training
"""

from flask import Blueprint, jsonify, request
import logging
from .trigger_logic import get_trigger_status, force_training_trigger
from .automated_service import get_training_service, manual_train_now
from ..database.connection import init_database_connection

logger = logging.getLogger(__name__)

# Create blueprint for training endpoints
training_bp = Blueprint('training', __name__, url_prefix='/training')

@training_bp.route('/status', methods=['GET'])
def get_training_status():
    """Get current training trigger status"""
    try:
        # Ensure database connection
        if not init_database_connection():
            return jsonify({"error": "Database connection failed"}), 500

        status = get_trigger_status()
        service_status = get_training_service().get_service_status()

        return jsonify({
            "trigger_status": status,
            "service_status": service_status
        })

    except Exception as e:
        logger.error(f"Error getting training status: {e}")
        return jsonify({"error": str(e)}), 500

@training_bp.route('/trigger', methods=['POST'])
def manual_trigger():
    """Manually trigger training"""
    try:
        # Ensure database connection
        if not init_database_connection():
            return jsonify({"error": "Database connection failed"}), 500

        data = request.json or {}
        reason = data.get('reason', 'Manual API trigger')

        success = force_training_trigger(reason)

        if success:
            return jsonify({
                "status": "success",
                "message": f"Training trigger activated: {reason}"
            })
        else:
            return jsonify({
                "status": "failed",
                "message": "Failed to activate training trigger"
            }), 500

    except Exception as e:
        logger.error(f"Error triggering training: {e}")
        return jsonify({"error": str(e)}), 500

@training_bp.route('/train-now', methods=['POST'])
def train_immediately():
    """Immediately start training (bypasses triggers)"""
    try:
        # Ensure database connection
        if not init_database_connection():
            return jsonify({"error": "Database connection failed"}), 500

        success = manual_train_now()

        if success:
            return jsonify({
                "status": "success",
                "message": "Training started successfully"
            })
        else:
            return jsonify({
                "status": "failed",
                "message": "Training failed to start"
            }), 500

    except Exception as e:
        logger.error(f"Error starting training: {e}")
        return jsonify({"error": str(e)}), 500

@training_bp.route('/service/start', methods=['POST'])
def start_service():
    """Start the automated training service"""
    try:
        service = get_training_service()
        if service.is_running:
            return jsonify({
                "status": "already_running",
                "message": "Automated training service is already running"
            })

        service.start()
        return jsonify({
            "status": "success",
            "message": "Automated training service started"
        })

    except Exception as e:
        logger.error(f"Error starting training service: {e}")
        return jsonify({"error": str(e)}), 500

@training_bp.route('/service/stop', methods=['POST'])
def stop_service():
    """Stop the automated training service"""
    try:
        service = get_training_service()
        if not service.is_running:
            return jsonify({
                "status": "not_running",
                "message": "Automated training service is not running"
            })

        service.stop()
        return jsonify({
            "status": "success",
            "message": "Automated training service stopped"
        })

    except Exception as e:
        logger.error(f"Error stopping training service: {e}")
        return jsonify({"error": str(e)}), 500

@training_bp.route('/service/status', methods=['GET'])
def service_status():
    """Get automated training service status"""
    try:
        status = get_training_service_status()
        return jsonify(status)

    except Exception as e:
        logger.error(f"Error getting service status: {e}")
        return jsonify({"error": str(e)}), 500

# Integration function to add training endpoints to existing Flask app
def register_training_endpoints(app):
    """Register training endpoints with a Flask app"""
    app.register_blueprint(training_bp)
    logger.info("Training API endpoints registered")

# Example usage in main app:
"""
from services.training_triggers.training_api import register_training_endpoints

app = Flask(__name__)
register_training_endpoints(app)
"""