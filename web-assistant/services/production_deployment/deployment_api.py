"""
Phase 9: Production Deployment API
REST endpoints for production monitoring, scaling, and management
"""

from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Import production deployment components
try:
    from services.production_deployment.deployment_core import (
        get_production_monitor,
        get_auto_scaler,
        get_backup_manager,
        get_deployment_manager
    )
except ImportError:
    logger.warning("Production deployment modules not available")
    get_production_monitor = None
    get_auto_scaler = None
    get_backup_manager = None
    get_deployment_manager = None

deploy_bp = Blueprint('deploy', __name__, url_prefix='/deploy')

@deploy_bp.route('/health', methods=['GET'])
def get_system_health():
    """Get comprehensive system health status"""
    if not get_production_monitor:
        return jsonify({"error": "Production monitor not available"}), 503

    try:
        monitor = get_production_monitor()
        health = monitor.check_system_health()

        return jsonify({
            "status": "success",
            "health": health
        })

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"error": str(e)}), 500

@deploy_bp.route('/health/history', methods=['GET'])
def get_health_history():
    """Get health check history"""
    if not get_production_monitor:
        return jsonify({"error": "Production monitor not available"}), 503

    try:
        hours = int(request.args.get('hours', 24))
        monitor = get_production_monitor()
        history = monitor.get_health_history(hours)

        return jsonify({
            "status": "success",
            "history": history,
            "hours": hours,
            "total_checks": len(history)
        })

    except Exception as e:
        logger.error(f"Health history retrieval failed: {e}")
        return jsonify({"error": str(e)}), 500

@deploy_bp.route('/scaling/status', methods=['GET'])
def get_scaling_status():
    """Get current auto-scaling status"""
    if not get_auto_scaler:
        return jsonify({"error": "Auto-scaler not available"}), 503

    try:
        scaler = get_auto_scaler()
        scaling_decision = scaler.check_scaling_needed()

        return jsonify({
            "status": "success",
            "scaling_status": scaling_decision,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Scaling status check failed: {e}")
        return jsonify({"error": str(e)}), 500

@deploy_bp.route('/scaling/apply', methods=['POST'])
def apply_scaling():
    """Manually apply scaling decision"""
    if not get_auto_scaler:
        return jsonify({"error": "Auto-scaler not available"}), 503

    try:
        scaler = get_auto_scaler()
        scaling_decision = scaler.check_scaling_needed()

        if scaling_decision["scale_up"] or scaling_decision["scale_down"]:
            success = scaler.apply_scaling(scaling_decision)

            return jsonify({
                "status": "success" if success else "failed",
                "scaling_applied": success,
                "scaling_decision": scaling_decision,
                "message": f"Scaling {'applied' if success else 'failed'}"
            })
        else:
            return jsonify({
                "status": "success",
                "scaling_applied": False,
                "message": "No scaling needed"
            })

    except Exception as e:
        logger.error(f"Scaling application failed: {e}")
        return jsonify({"error": str(e)}), 500

@deploy_bp.route('/backup/create', methods=['POST'])
def create_backup():
    """Create a system backup"""
    if not get_backup_manager:
        return jsonify({"error": "Backup manager not available"}), 503

    try:
        data = request.get_json() or {}
        components = data.get('components', ["database", "models", "config", "logs"])

        backup_mgr = get_backup_manager()
        backup_path = backup_mgr.create_backup(components)

        if backup_path:
            return jsonify({
                "status": "success",
                "backup_path": backup_path,
                "components": components,
                "message": f"Backup created successfully with components: {', '.join(components)}"
            })
        else:
            return jsonify({"error": "Backup creation failed"}), 500

    except Exception as e:
        logger.error(f"Backup creation failed: {e}")
        return jsonify({"error": str(e)}), 500

@deploy_bp.route('/backup/restore', methods=['POST'])
def restore_backup():
    """Restore from a backup"""
    if not get_backup_manager:
        return jsonify({"error": "Backup manager not available"}), 503

    try:
        data = request.get_json()
        if not data or 'backup_path' not in data:
            return jsonify({"error": "backup_path required"}), 400

        backup_path = data['backup_path']
        backup_mgr = get_backup_manager()
        success = backup_mgr.restore_backup(backup_path)

        return jsonify({
            "status": "success" if success else "failed",
            "backup_restored": success,
            "backup_path": backup_path,
            "message": f"Backup {'restored' if success else 'restore failed'}"
        })

    except Exception as e:
        logger.error(f"Backup restore failed: {e}")
        return jsonify({"error": str(e)}), 500

@deploy_bp.route('/backups', methods=['GET'])
def list_backups():
    """List available backups"""
    if not get_backup_manager:
        return jsonify({"error": "Backup manager not available"}), 503

    try:
        backup_mgr = get_backup_manager()
        backup_dir = backup_mgr.backup_dir

        backups = []
        if backup_dir.exists():
            for backup_path in backup_dir.iterdir():
                if backup_path.is_dir():
                    metadata_file = backup_path / "backup_metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, "r") as f:
                                metadata = json.load(f)
                            backups.append({
                                "path": str(backup_path),
                                "name": backup_path.name,
                                "metadata": metadata
                            })
                        except:
                            pass

        return jsonify({
            "status": "success",
            "backups": backups,
            "total_backups": len(backups)
        })

    except Exception as e:
        logger.error(f"Backup listing failed: {e}")
        return jsonify({"error": str(e)}), 500

@deploy_bp.route('/services/start', methods=['POST'])
def start_production_services():
    """Start all production services"""
    if not get_deployment_manager:
        return jsonify({"error": "Deployment manager not available"}), 503

    try:
        deployment_mgr = get_deployment_manager()
        deployment_mgr.start_production_services()

        return jsonify({
            "status": "success",
            "message": "Production services started",
            "services": ["monitoring", "auto_scaling", "backup_schedule"]
        })

    except Exception as e:
        logger.error(f"Production services start failed: {e}")
        return jsonify({"error": str(e)}), 500

@deploy_bp.route('/services/status', methods=['GET'])
def get_services_status():
    """Get status of all production services"""
    try:
        services_status = {
            "monitoring": get_production_monitor() is not None,
            "auto_scaling": get_auto_scaler() is not None,
            "backup_manager": get_backup_manager() is not None,
            "deployment_manager": get_deployment_manager() is not None
        }

        overall_status = "healthy" if all(services_status.values()) else "degraded"

        return jsonify({
            "status": "success",
            "services_status": services_status,
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Services status check failed: {e}")
        return jsonify({"error": str(e)}), 500

@deploy_bp.route('/config', methods=['GET'])
def get_deployment_config():
    """Get current deployment configuration"""
    if not get_deployment_manager:
        return jsonify({"error": "Deployment manager not available"}), 503

    try:
        deployment_mgr = get_deployment_manager()
        config = deployment_mgr.deployment_config

        return jsonify({
            "status": "success",
            "config": config
        })

    except Exception as e:
        logger.error(f"Config retrieval failed: {e}")
        return jsonify({"error": str(e)}), 500

@deploy_bp.route('/config', methods=['POST'])
def update_deployment_config():
    """Update deployment configuration"""
    if not get_deployment_manager:
        return jsonify({"error": "Deployment manager not available"}), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Configuration data required"}), 400

        deployment_mgr = get_deployment_manager()

        # Update configuration
        deployment_mgr.deployment_config.update(data)

        # Save to file
        config_file = Path("deployment_config.json")
        with open(config_file, "w") as f:
            json.dump(deployment_mgr.deployment_config, f, indent=2)

        return jsonify({
            "status": "success",
            "message": "Deployment configuration updated",
            "config": deployment_mgr.deployment_config
        })

    except Exception as e:
        logger.error(f"Config update failed: {e}")
        return jsonify({"error": str(e)}), 500

@deploy_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get current system alerts"""
    if not get_production_monitor:
        return jsonify({"error": "Production monitor not available"}), 503

    try:
        monitor = get_production_monitor()
        health = monitor.check_system_health()
        alerts = health.get("alerts", [])

        return jsonify({
            "status": "success",
            "alerts": alerts,
            "alert_count": len(alerts),
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Alerts retrieval failed: {e}")
        return jsonify({"error": str(e)}), 500

@deploy_bp.route('/metrics', methods=['GET'])
def get_production_metrics():
    """Get comprehensive production metrics"""
    try:
        metrics = {
            "system_health": None,
            "scaling_status": None,
            "backup_count": 0,
            "services_status": None
        }

        # Get system health
        if get_production_monitor:
            monitor = get_production_monitor()
            metrics["system_health"] = monitor.check_system_health()

        # Get scaling status
        if get_auto_scaler:
            scaler = get_auto_scaler()
            metrics["scaling_status"] = scaler.check_scaling_needed()

        # Get backup count
        if get_backup_manager:
            backup_mgr = get_backup_manager()
            backup_dir = backup_mgr.backup_dir
            if backup_dir.exists():
                metrics["backup_count"] = len(list(backup_dir.iterdir()))

        # Get services status
        services_status = get_services_status()
        if services_status[1] == 200:
            metrics["services_status"] = services_status[0].get("services_status")

        return jsonify({
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Production metrics retrieval failed: {e}")
        return jsonify({"error": str(e)}), 500

def register_deployment_endpoints(app):
    """Register production deployment endpoints with Flask app"""
    try:
        app.register_blueprint(deploy_bp)
        logger.info("Production deployment endpoints registered")
    except Exception as e:
        logger.error(f"Failed to register deployment endpoints: {e}")

# Export for external use
__all__ = ['register_deployment_endpoints']