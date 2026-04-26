"""
Phase 6: Robot Logging API
REST endpoints for receiving robot interaction logs and feedback
"""

from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Import robot logging components
try:
    from services.robot_logging.robot_logger import RobotInteraction, RobotFeedback
    from services.database.connection import DatabaseManager
except ImportError:
    logger.warning("Robot logging modules not available")
    RobotInteraction = None
    RobotFeedback = None
    DatabaseManager = None

robot_bp = Blueprint('robot', __name__, url_prefix='/robot')

@robot_bp.route('/interactions', methods=['POST'])
def log_interactions():
    """Receive and store robot interactions"""
    if not RobotInteraction or not DatabaseManager:
        return jsonify({"error": "Robot logging not available"}), 503

    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({"error": "Expected list of interactions"}), 400

        db = DatabaseManager()
        if not db.connect():
            return jsonify({"error": "Database connection failed"}), 503

        stored_count = 0
        errors = []

        for item in data:
            try:
                # Convert to RobotInteraction object for validation
                interaction = RobotInteraction(**item)

                # Store in database
                success = db.log_robot_interaction(
                    robot_id=interaction.robot_id,
                    interaction_type=interaction.interaction_type,
                    user_input=interaction.user_input,
                    robot_response=interaction.robot_response,
                    sentiment_score=interaction.sentiment_score,
                    confidence_score=interaction.confidence_score,
                    model_version=interaction.model_version,
                    processing_time_ms=interaction.processing_time_ms,
                    success=interaction.success,
                    error_message=interaction.error_message,
                    metadata=json.dumps(interaction.metadata) if interaction.metadata else None
                )

                if success:
                    stored_count += 1
                else:
                    errors.append(f"Failed to store interaction: {item}")

            except Exception as e:
                errors.append(f"Invalid interaction data: {e}")

        db.disconnect()

        return jsonify({
            "status": "success",
            "stored": stored_count,
            "total": len(data),
            "errors": errors if errors else None
        })

    except Exception as e:
        logger.error(f"Interaction logging failed: {e}")
        return jsonify({"error": str(e)}), 500

@robot_bp.route('/feedback', methods=['POST'])
def log_feedback():
    """Receive and store robot feedback"""
    if not RobotFeedback or not DatabaseManager:
        return jsonify({"error": "Robot feedback logging not available"}), 503

    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({"error": "Expected list of feedback items"}), 400

        db = DatabaseManager()
        if not db.connect():
            return jsonify({"error": "Database connection failed"}), 503

        stored_count = 0
        errors = []

        for item in data:
            try:
                # Convert to RobotFeedback object for validation
                feedback = RobotFeedback(**item)

                # Store in database
                success = db.log_robot_feedback(
                    robot_id=feedback.robot_id,
                    feedback_type=feedback.feedback_type,
                    original_interaction_id=feedback.original_interaction_id,
                    feedback_data=json.dumps(feedback.feedback_data) if feedback.feedback_data else None,
                    improvement_suggestion=feedback.improvement_suggestion,
                    user_rating=feedback.user_rating,
                    metadata=json.dumps(feedback.metadata) if feedback.metadata else None
                )

                if success:
                    stored_count += 1
                else:
                    errors.append(f"Failed to store feedback: {item}")

            except Exception as e:
                errors.append(f"Invalid feedback data: {e}")

        db.disconnect()

        return jsonify({
            "status": "success",
            "stored": stored_count,
            "total": len(data),
            "errors": errors if errors else None
        })

    except Exception as e:
        logger.error(f"Feedback logging failed: {e}")
        return jsonify({"error": str(e)}), 500

@robot_bp.route('/status', methods=['GET'])
def get_robot_status():
    """Get robot logging system status"""
    try:
        # Get database stats
        db_stats = {"connected": False, "robot_count": 0, "total_interactions": 0}

        if DatabaseManager:
            db = DatabaseManager()
            if db.connect():
                db_stats["connected"] = True

                # Get robot statistics
                try:
                    stats = db.get_robot_statistics()
                    db_stats.update(stats)
                except Exception as e:
                    logger.error(f"Failed to get robot stats: {e}")

                db.disconnect()

        return jsonify({
            "status": "success",
            "robot_logging": {
                "available": RobotInteraction is not None and RobotFeedback is not None,
                "database": db_stats
            }
        })

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return jsonify({"error": str(e)}), 500

@robot_bp.route('/robots', methods=['GET'])
def list_robots():
    """List all robots and their recent activity"""
    if not DatabaseManager:
        return jsonify({"error": "Database not available"}), 503

    try:
        db = DatabaseManager()
        if not db.connect():
            return jsonify({"error": "Database connection failed"}), 503

        robots = db.get_robot_list()
        db.disconnect()

        return jsonify({
            "status": "success",
            "robots": robots
        })

    except Exception as e:
        logger.error(f"Robot list failed: {e}")
        return jsonify({"error": str(e)}), 500

@robot_bp.route('/robots/<robot_id>/interactions', methods=['GET'])
def get_robot_interactions(robot_id: str):
    """Get interactions for a specific robot"""
    if not DatabaseManager:
        return jsonify({"error": "Database not available"}), 503

    try:
        # Parse query parameters
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        db = DatabaseManager()
        if not db.connect():
            return jsonify({"error": "Database connection failed"}), 503

        interactions = db.get_robot_interactions(robot_id, limit=limit, offset=offset)
        db.disconnect()

        return jsonify({
            "status": "success",
            "robot_id": robot_id,
            "interactions": interactions,
            "limit": limit,
            "offset": offset
        })

    except Exception as e:
        logger.error(f"Robot interactions fetch failed: {e}")
        return jsonify({"error": str(e)}), 500

@robot_bp.route('/analytics/summary', methods=['GET'])
def get_robot_analytics():
    """Get analytics summary for all robots"""
    if not DatabaseManager:
        return jsonify({"error": "Database not available"}), 503

    try:
        db = DatabaseManager()
        if not db.connect():
            return jsonify({"error": "Database connection failed"}), 503

        analytics = db.get_robot_analytics()
        db.disconnect()

        return jsonify({
            "status": "success",
            "analytics": analytics
        })

    except Exception as e:
        logger.error(f"Robot analytics failed: {e}")
        return jsonify({"error": str(e)}), 500

def register_robot_endpoints(app):
    """Register robot logging endpoints with Flask app"""
    try:
        app.register_blueprint(robot_bp)
        logger.info("Robot logging endpoints registered")
    except Exception as e:
        logger.error(f"Failed to register robot endpoints: {e}")

# Export for external use
__all__ = ['register_robot_endpoints']