"""
Phase 5: Pi Update API
REST endpoints for Pi robot model updates and status monitoring
"""

from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Import Pi update components
try:
    from services.pi_updates.pi_update_manager import (
        get_pi_update_manager,
        get_auto_update_service
    )
except ImportError:
    logger.warning("Pi update modules not available")
    get_pi_update_manager = None
    get_auto_update_service = None

pi_bp = Blueprint('pi', __name__, url_prefix='/pi')

@pi_bp.route('/status', methods=['GET'])
def get_pi_status():
    """Get Pi robot update status"""
    if not get_pi_update_manager:
        return jsonify({"error": "Pi update manager not available"}), 503

    try:
        manager = get_pi_update_manager()
        status = manager.get_update_status()

        return jsonify({
            "status": "success",
            "pi_status": status
        })

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return jsonify({"error": str(e)}), 500

@pi_bp.route('/check-updates', methods=['POST'])
def check_for_updates():
    """Manually check for model updates"""
    if not get_pi_update_manager:
        return jsonify({"error": "Pi update manager not available"}), 503

    try:
        manager = get_pi_update_manager()
        update_info = manager.check_for_updates()

        if update_info:
            return jsonify({
                "status": "success",
                "update_available": True,
                "update_info": update_info
            })
        else:
            return jsonify({
                "status": "success",
                "update_available": False,
                "message": "No updates available"
            })

    except Exception as e:
        logger.error(f"Update check failed: {e}")
        return jsonify({"error": str(e)}), 500

@pi_bp.route('/download-update', methods=['POST'])
def download_update():
    """Download available model update"""
    if not get_pi_update_manager:
        return jsonify({"error": "Pi update manager not available"}), 503

    try:
        data = request.get_json()
        if not data or 'update_info' not in data:
            return jsonify({"error": "update_info required"}), 400

        manager = get_pi_update_manager()
        download_path = manager.download_update(data['update_info'])

        if download_path:
            return jsonify({
                "status": "success",
                "download_path": download_path,
                "message": "Update downloaded successfully"
            })
        else:
            return jsonify({"error": "Download failed"}), 500

    except Exception as e:
        logger.error(f"Download failed: {e}")
        return jsonify({"error": str(e)}), 500

@pi_bp.route('/validate-update', methods=['POST'])
def validate_update():
    """Validate downloaded update"""
    if not get_pi_update_manager:
        return jsonify({"error": "Pi update manager not available"}), 503

    try:
        data = request.get_json()
        if not data or 'download_path' not in data:
            return jsonify({"error": "download_path required"}), 400

        manager = get_pi_update_manager()
        is_valid = manager.validate_update(data['download_path'])

        return jsonify({
            "status": "success",
            "valid": is_valid,
            "message": "Update is valid" if is_valid else "Update validation failed"
        })

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return jsonify({"error": str(e)}), 500

@pi_bp.route('/apply-update', methods=['POST'])
def apply_update():
    """Apply validated model update"""
    if not get_pi_update_manager:
        return jsonify({"error": "Pi update manager not available"}), 503

    try:
        data = request.get_json()
        if not data or 'download_path' not in data:
            return jsonify({"error": "download_path required"}), 400

        manager = get_pi_update_manager()
        success = manager.apply_update(data['download_path'])

        if success:
            return jsonify({
                "status": "success",
                "message": "Update applied successfully",
                "new_version": manager.current_model_version
            })
        else:
            return jsonify({"error": "Update application failed"}), 500

    except Exception as e:
        logger.error(f"Update application failed: {e}")
        return jsonify({"error": str(e)}), 500

@pi_bp.route('/auto-update/start', methods=['POST'])
def start_auto_updates():
    """Start automatic update service"""
    if not get_auto_update_service:
        return jsonify({"error": "Auto-update service not available"}), 503

    try:
        service = get_auto_update_service()
        # Note: In real implementation, this would start a background thread
        # For demo purposes, we just mark it as started
        service.running = True

        return jsonify({
            "status": "success",
            "message": "Auto-update service started"
        })

    except Exception as e:
        logger.error(f"Start auto-update failed: {e}")
        return jsonify({"error": str(e)}), 500

@pi_bp.route('/auto-update/stop', methods=['POST'])
def stop_auto_updates():
    """Stop automatic update service"""
    if not get_auto_update_service:
        return jsonify({"error": "Auto-update service not available"}), 503

    try:
        service = get_auto_update_service()
        service.stop_auto_updates()

        return jsonify({
            "status": "success",
            "message": "Auto-update service stopped"
        })

    except Exception as e:
        logger.error(f"Stop auto-update failed: {e}")
        return jsonify({"error": str(e)}), 500

@pi_bp.route('/auto-update/status', methods=['GET'])
def get_auto_update_status():
    """Get automatic update service status"""
    if not get_auto_update_service:
        return jsonify({"error": "Auto-update service not available"}), 503

    try:
        service = get_auto_update_service()
        status = {
            "running": service.running,
            "check_interval_hours": service.check_interval.total_seconds() / 3600,
            "last_check": service.last_check.isoformat() if service.last_check else None
        }

        return jsonify({
            "status": "success",
            "auto_update_status": status
        })

    except Exception as e:
        logger.error(f"Auto-update status check failed: {e}")
        return jsonify({"error": str(e)}), 500

@pi_bp.route('/full-update', methods=['POST'])
def full_update_cycle():
    """Perform complete update cycle: check → download → validate → apply"""
    if not get_pi_update_manager:
        return jsonify({"error": "Pi update manager not available"}), 503

    try:
        manager = get_pi_update_manager()
        results = {}

        # Step 1: Check for updates
        update_info = manager.check_for_updates()
        results["check"] = {"success": update_info is not None, "update_info": update_info}

        if not update_info:
            return jsonify({
                "status": "success",
                "message": "No updates available",
                "results": results
            })

        # Step 2: Download update
        download_path = manager.download_update(update_info)
        results["download"] = {"success": download_path is not None, "path": download_path}

        if not download_path:
            return jsonify({
                "status": "partial_success",
                "message": "Download failed",
                "results": results
            })

        # Step 3: Validate update
        is_valid = manager.validate_update(download_path)
        results["validate"] = {"success": is_valid}

        if not is_valid:
            return jsonify({
                "status": "partial_success",
                "message": "Validation failed",
                "results": results
            })

        # Step 4: Apply update
        applied = manager.apply_update(download_path)
        results["apply"] = {"success": applied, "new_version": manager.current_model_version if applied else None}

        if applied:
            return jsonify({
                "status": "success",
                "message": f"Full update cycle completed successfully to v{manager.current_model_version}",
                "results": results
            })
        else:
            return jsonify({
                "status": "partial_success",
                "message": "Update application failed",
                "results": results
            })

    except Exception as e:
        logger.error(f"Full update cycle failed: {e}")
        return jsonify({"error": str(e)}), 500

def register_pi_endpoints(app):
    """Register Pi update endpoints with Flask app"""
    try:
        app.register_blueprint(pi_bp)
        logger.info("Pi update endpoints registered")
    except Exception as e:
        logger.error(f"Failed to register Pi endpoints: {e}")

# Export for external use
__all__ = ['register_pi_endpoints']