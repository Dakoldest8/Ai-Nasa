"""
Phase 4: Export + Sync API
REST endpoints for model export/import and device synchronization
"""

from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Any
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Import sync components
try:
    from services.export_sync.sync_manager import (
        export_model_for_sync,
        import_model_from_sync,
        get_sync_manager
    )
except ImportError:
    logger.warning("Export sync modules not available")
    export_model_for_sync = None
    import_model_from_sync = None
    get_sync_manager = None

sync_bp = Blueprint('sync', __name__, url_prefix='/sync')

@sync_bp.route('/export', methods=['POST'])
def export_model():
    """Export a model for synchronization"""
    if not export_model_for_sync:
        return jsonify({"error": "Export sync not available"}), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        model_path = data.get('model_path')
        model_version = data.get('model_version')
        metadata = data.get('metadata', {})

        if not model_path or not model_version:
            return jsonify({"error": "model_path and model_version required"}), 400

        if not os.path.exists(model_path):
            return jsonify({"error": f"Model path does not exist: {model_path}"}), 404

        export_path = export_model_for_sync(model_path, model_version, metadata)

        return jsonify({
            "status": "success",
            "export_path": export_path,
            "model_version": model_version,
            "message": f"Model v{model_version} exported successfully"
        })

    except Exception as e:
        logger.error(f"Export failed: {e}")
        return jsonify({"error": str(e)}), 500

@sync_bp.route('/import', methods=['POST'])
def import_model():
    """Import a model from synchronization package"""
    if not import_model_from_sync:
        return jsonify({"error": "Import sync not available"}), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        export_path = data.get('export_path')
        target_dir = data.get('target_dir', 'models/imported')

        if not export_path:
            return jsonify({"error": "export_path required"}), 400

        if not os.path.exists(export_path):
            return jsonify({"error": f"Export path does not exist: {export_path}"}), 404

        metadata = import_model_from_sync(export_path, target_dir)

        return jsonify({
            "status": "success",
            "metadata": metadata,
            "target_dir": target_dir,
            "message": "Model imported successfully"
        })

    except Exception as e:
        logger.error(f"Import failed: {e}")
        return jsonify({"error": str(e)}), 500

@sync_bp.route('/sync-to-pi', methods=['POST'])
def sync_to_pi():
    """Sync model to Pi robot"""
    if not get_sync_manager:
        return jsonify({"error": "Sync manager not available"}), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        model_path = data.get('model_path')
        model_version = data.get('model_version')
        pi_address = data.get('pi_address', 'raspberrypi.local')

        if not model_path or not model_version:
            return jsonify({"error": "model_path and model_version required"}), 400

        sync_mgr = get_sync_manager()
        success = sync_mgr.sync_to_pi(model_path, model_version, pi_address)

        if success:
            return jsonify({
                "status": "success",
                "message": f"Model v{model_version} queued for sync to {pi_address}",
                "pi_address": pi_address
            })
        else:
            return jsonify({"error": "Sync to Pi failed"}), 500

    except Exception as e:
        logger.error(f"Sync to Pi failed: {e}")
        return jsonify({"error": str(e)}), 500

@sync_bp.route('/sync-from-pi', methods=['POST'])
def sync_from_pi():
    """Sync model data from Pi robot"""
    if not get_sync_manager:
        return jsonify({"error": "Sync manager not available"}), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        pi_export_path = data.get('pi_export_path')
        local_import_dir = data.get('local_import_dir', 'models/from_pi')

        if not pi_export_path:
            return jsonify({"error": "pi_export_path required"}), 400

        sync_mgr = get_sync_manager()
        metadata = sync_mgr.sync_from_pi(pi_export_path, local_import_dir)

        if metadata:
            return jsonify({
                "status": "success",
                "metadata": metadata,
                "import_dir": local_import_dir,
                "message": "Model data synced from Pi successfully"
            })
        else:
            return jsonify({"error": "Sync from Pi failed"}), 500

    except Exception as e:
        logger.error(f"Sync from Pi failed: {e}")
        return jsonify({"error": str(e)}), 500

@sync_bp.route('/status', methods=['GET'])
def get_sync_status():
    """Get current synchronization status"""
    if not get_sync_manager:
        return jsonify({"error": "Sync manager not available"}), 503

    try:
        sync_mgr = get_sync_manager()
        status = sync_mgr.get_sync_status()

        return jsonify({
            "status": "success",
            "sync_status": status
        })

    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return jsonify({"error": str(e)}), 500

@sync_bp.route('/exports', methods=['GET'])
def list_exports():
    """List available model exports"""
    try:
        export_dir = Path("exports")
        if not export_dir.exists():
            return jsonify({"exports": []})

        exports = []
        for export_path in export_dir.iterdir():
            if export_path.is_dir():
                metadata_file = export_path / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, "r") as f:
                            metadata = json.load(f)
                        exports.append({
                            "path": str(export_path),
                            "name": export_path.name,
                            "metadata": metadata
                        })
                    except:
                        pass

        return jsonify({
            "status": "success",
            "exports": exports
        })

    except Exception as e:
        logger.error(f"List exports failed: {e}")
        return jsonify({"error": str(e)}), 500

def register_sync_endpoints(app):
    """Register sync endpoints with Flask app"""
    try:
        app.register_blueprint(sync_bp)
        logger.info("Sync endpoints registered")
    except Exception as e:
        logger.error(f"Failed to register sync endpoints: {e}")

# Export for external use
__all__ = ['register_sync_endpoints']