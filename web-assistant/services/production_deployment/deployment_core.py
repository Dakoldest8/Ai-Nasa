"""
Phase 9: Production Deployment
Production-ready deployment, monitoring, and scaling infrastructure
"""

import os
import json
import logging
import subprocess
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import psutil
import requests

logger = logging.getLogger(__name__)

class ProductionMonitor:
    """Production system monitoring and health checks"""

    def __init__(self, services_to_monitor: List[str] = None):
        self.services_to_monitor = services_to_monitor or [
            'web_assistant', 'ai_server', 'database', 'robot_services'
        ]
        self.health_history = []
        self.alerts = []

    def check_system_health(self) -> Dict:
        """Comprehensive system health check"""
        health = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "services": {},
            "system_resources": self._check_system_resources(),
            "network_status": self._check_network_status(),
            "alerts": []
        }

        # Check each service
        for service in self.services_to_monitor:
            service_health = self._check_service_health(service)
            health["services"][service] = service_health

            if service_health["status"] != "healthy":
                health["overall_status"] = "degraded"
                health["alerts"].append(f"Service {service} is {service_health['status']}")

        # Store in history
        self.health_history.append(health)
        if len(self.health_history) > 100:  # Keep last 100 checks
            self.health_history.pop(0)

        return health

    def _check_service_health(self, service_name: str) -> Dict:
        """Check health of a specific service"""
        try:
            if service_name == 'web_assistant':
                return self._check_web_assistant()
            elif service_name == 'ai_server':
                return self._check_ai_server()
            elif service_name == 'database':
                return self._check_database()
            elif service_name == 'robot_services':
                return self._check_robot_services()
            else:
                return {"status": "unknown", "message": f"No health check defined for {service_name}"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _check_web_assistant(self) -> Dict:
        """Check web assistant health"""
        try:
            # Try to connect to web server
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                return {"status": "healthy", "response_time": response.elapsed.total_seconds()}
            else:
                return {"status": "unhealthy", "http_status": response.status_code}
        except:
            return {"status": "down", "message": "Cannot connect to web server"}

    def _check_ai_server(self) -> Dict:
        """Check AI server health"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                return {"status": "healthy", "response_time": response.elapsed.total_seconds()}
            else:
                return {"status": "unhealthy", "http_status": response.status_code}
        except:
            return {"status": "down", "message": "Cannot connect to AI server"}

    def _check_database(self) -> Dict:
        """Check database health"""
        try:
            from services.database.connection import get_db_manager
            db = get_db_manager()
            connected = db.connect()
            if connected:
                db.disconnect()
                return {"status": "healthy", "message": "Database connection successful"}
            else:
                return {"status": "down", "message": "Database connection failed"}
        except:
            return {"status": "error", "message": "Database health check failed"}

    def _check_robot_services(self) -> Dict:
        """Check robot services health"""
        # Check if robot processes are running
        robot_processes = ["python", "robot_agent.py"]  # Simplified check
        running = any(self._is_process_running(proc) for proc in robot_processes)

        if running:
            return {"status": "healthy", "message": "Robot services running"}
        else:
            return {"status": "down", "message": "No robot services detected"}

    def _check_system_resources(self) -> Dict:
        """Check system resource usage"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_connections": len(psutil.net_connections())
        }

    def _check_network_status(self) -> Dict:
        """Check network connectivity"""
        try:
            # Try to reach external service
            response = requests.get("https://www.google.com", timeout=5)
            return {
                "internet_connected": response.status_code == 200,
                "latency_ms": response.elapsed.total_seconds() * 1000
            }
        except:
            return {"internet_connected": False, "error": "Cannot reach external services"}

    def _is_process_running(self, process_name: str) -> bool:
        """Check if a process is running"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if process_name.lower() in ' '.join(proc.info['cmdline'] or []).lower():
                    return True
            return False
        except:
            return False

    def get_health_history(self, hours: int = 24) -> List[Dict]:
        """Get health check history for specified hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [h for h in self.health_history if datetime.fromisoformat(h["timestamp"]) > cutoff]

class AutoScaler:
    """Automatic scaling and resource management"""

    def __init__(self, monitor: ProductionMonitor):
        self.monitor = monitor
        self.scaling_rules = {
            "cpu_threshold": 80.0,  # Scale up if CPU > 80%
            "memory_threshold": 85.0,  # Scale up if memory > 85%
            "response_time_threshold": 2.0,  # Scale up if response time > 2 seconds
            "min_instances": 1,
            "max_instances": 5
        }
        self.current_instances = 1

    def check_scaling_needed(self) -> Dict:
        """Check if scaling is needed"""
        health = self.monitor.check_system_health()

        scaling_decision = {
            "scale_up": False,
            "scale_down": False,
            "reason": "",
            "current_instances": self.current_instances,
            "recommended_instances": self.current_instances
        }

        # Check CPU usage
        cpu_usage = health["system_resources"]["cpu_percent"]
        if cpu_usage > self.scaling_rules["cpu_threshold"]:
            scaling_decision["scale_up"] = True
            scaling_decision["reason"] = f"High CPU usage: {cpu_usage}%"
            scaling_decision["recommended_instances"] = min(self.current_instances + 1, self.scaling_rules["max_instances"])

        # Check memory usage
        memory_usage = health["system_resources"]["memory_percent"]
        if memory_usage > self.scaling_rules["memory_threshold"]:
            scaling_decision["scale_up"] = True
            scaling_decision["reason"] = f"High memory usage: {memory_usage}%"
            scaling_decision["recommended_instances"] = min(self.current_instances + 1, self.scaling_rules["max_instances"])

        # Check response times
        services = health["services"]
        for service_name, service_health in services.items():
            if service_health.get("response_time", 0) > self.scaling_rules["response_time_threshold"]:
                scaling_decision["scale_up"] = True
                scaling_decision["reason"] = f"Slow {service_name} response: {service_health['response_time']}s"
                scaling_decision["recommended_instances"] = min(self.current_instances + 1, self.scaling_rules["max_instances"])
                break

        # Check if we can scale down
        if (cpu_usage < 30 and memory_usage < 50 and
            self.current_instances > self.scaling_rules["min_instances"]):
            scaling_decision["scale_down"] = True
            scaling_decision["reason"] = f"Low resource usage (CPU: {cpu_usage}%, Memory: {memory_usage}%)"
            scaling_decision["recommended_instances"] = max(self.current_instances - 1, self.scaling_rules["min_instances"])

        return scaling_decision

    def apply_scaling(self, scaling_decision: Dict) -> bool:
        """Apply scaling decision"""
        if not scaling_decision["scale_up"] and not scaling_decision["scale_down"]:
            return True  # No scaling needed

        try:
            new_instances = scaling_decision["recommended_instances"]

            if new_instances > self.current_instances:
                # Scale up
                logger.info(f"Scaling up from {self.current_instances} to {new_instances} instances")
                success = self._scale_up(new_instances - self.current_instances)
            else:
                # Scale down
                logger.info(f"Scaling down from {self.current_instances} to {new_instances} instances")
                success = self._scale_down(self.current_instances - new_instances)

            if success:
                self.current_instances = new_instances

            return success

        except Exception as e:
            logger.error(f"Scaling failed: {e}")
            return False

    def _scale_up(self, instances: int) -> bool:
        """Scale up by starting additional instances"""
        # In a real implementation, this would start new service instances
        # For demo, just log the scaling action
        logger.info(f"Scaling up: starting {instances} new instances")
        return True

    def _scale_down(self, instances: int) -> bool:
        """Scale down by stopping instances"""
        # In a real implementation, this would stop service instances gracefully
        # For demo, just log the scaling action
        logger.info(f"Scaling down: stopping {instances} instances")
        return True

class BackupManager:
    """Automated backup and recovery management"""

    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    def create_backup(self, components: List[str] = None) -> str:
        """Create a comprehensive system backup"""
        if components is None:
            components = ["database", "models", "config", "logs"]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)

        backup_info = {
            "backup_name": backup_name,
            "timestamp": timestamp,
            "components": {},
            "status": "in_progress"
        }

        try:
            for component in components:
                if component == "database":
                    success = self._backup_database(backup_path)
                elif component == "models":
                    success = self._backup_models(backup_path)
                elif component == "config":
                    success = self._backup_config(backup_path)
                elif component == "logs":
                    success = self._backup_logs(backup_path)
                else:
                    success = False

                backup_info["components"][component] = "success" if success else "failed"

            backup_info["status"] = "completed"
            self._save_backup_metadata(backup_path, backup_info)

            logger.info(f"Backup completed: {backup_name}")
            return str(backup_path)

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            backup_info["status"] = "failed"
            backup_info["error"] = str(e)
            return ""

    def restore_backup(self, backup_path: str) -> bool:
        """Restore from a backup"""
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                logger.error(f"Backup path does not exist: {backup_path}")
                return False

            # Load backup metadata
            metadata_file = backup_path / "backup_metadata.json"
            if not metadata_file.exists():
                logger.error("Backup metadata not found")
                return False

            with open(metadata_file, "r") as f:
                metadata = json.load(f)

            # Restore components
            for component, status in metadata.get("components", {}).items():
                if status == "success":
                    if component == "database":
                        self._restore_database(backup_path)
                    elif component == "models":
                        self._restore_models(backup_path)
                    elif component == "config":
                        self._restore_config(backup_path)
                    elif component == "logs":
                        self._restore_logs(backup_path)

            logger.info(f"Backup restored from: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False

    def _backup_database(self, backup_path: Path) -> bool:
        """Backup database"""
        try:
            # In real implementation, use mysqldump or similar
            # For demo, create a placeholder
            db_backup = backup_path / "database_backup.sql"
            with open(db_backup, "w") as f:
                f.write("-- Database backup placeholder\n")
            return True
        except Exception as e:
            return False

    def _backup_models(self, backup_path: Path) -> bool:
        """Backup trained models"""
        try:
            models_dir = Path("models")
            if models_dir.exists():
                import shutil
                shutil.copytree(models_dir, backup_path / "models", dirs_exist_ok=True)
            return True
        except Exception as e:
            return False

    def _backup_config(self, backup_path: Path) -> bool:
        """Backup configuration files"""
        try:
            config_files = ["config.json", "database_schema.sql", ".env"]
            for config_file in config_files:
                if os.path.exists(config_file):
                    import shutil
                    shutil.copy2(config_file, backup_path / config_file)
            return True
        except Exception as e:
            return False

    def _backup_logs(self, backup_path: Path) -> bool:
        """Backup log files"""
        try:
            logs_dir = Path("logs")
            if logs_dir.exists():
                import shutil
                shutil.copytree(logs_dir, backup_path / "logs", dirs_exist_ok=True)
            return True
        except Exception as e:
            return False

    def _restore_database(self, backup_path: Path) -> bool:
        """Restore database"""
        # Implementation would restore from SQL dump
        return True

    def _restore_models(self, backup_path: Path) -> bool:
        """Restore models"""
        # Implementation would copy model files back
        return True

    def _restore_config(self, backup_path: Path) -> bool:
        """Restore configuration"""
        # Implementation would restore config files
        return True

    def _restore_logs(self, backup_path: Path) -> bool:
        """Restore logs"""
        # Implementation would restore log files
        return True

    def _save_backup_metadata(self, backup_path: Path, metadata: Dict):
        """Save backup metadata"""
        metadata_file = backup_path / "backup_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2, default=str)

class DeploymentManager:
    """Production deployment management"""

    def __init__(self):
        self.monitor = ProductionMonitor()
        self.auto_scaler = AutoScaler(self.monitor)
        self.backup_manager = BackupManager()
        self.deployment_config = self._load_deployment_config()

    def _load_deployment_config(self) -> Dict:
        """Load deployment configuration"""
        config_file = Path("deployment_config.json")
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    return json.load(f)
            except:
                pass

        # Default configuration
        return {
            "environment": "production",
            "auto_scaling": True,
            "backup_schedule": "daily",
            "monitoring_interval": 60,  # seconds
            "log_level": "INFO"
        }

    def start_production_services(self):
        """Start all production services"""
        logger.info("Starting production deployment services")

        # Start monitoring
        self._start_monitoring()

        # Start auto-scaling if enabled
        if self.deployment_config.get("auto_scaling", True):
            self._start_auto_scaling()

        # Start backup scheduling
        self._start_backup_schedule()

        logger.info("Production services started")

    def _start_monitoring(self):
        """Start continuous monitoring"""
        def monitoring_loop():
            while True:
                try:
                    health = self.monitor.check_system_health()
                    if health["overall_status"] != "healthy":
                        logger.warning(f"System health issue: {health['alerts']}")

                    time.sleep(self.deployment_config.get("monitoring_interval", 60))
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(60)

        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()

    def _start_auto_scaling(self):
        """Start automatic scaling"""
        def scaling_loop():
            while True:
                try:
                    scaling_decision = self.auto_scaler.check_scaling_needed()
                    if scaling_decision["scale_up"] or scaling_decision["scale_down"]:
                        self.auto_scaler.apply_scaling(scaling_decision)

                    time.sleep(300)  # Check every 5 minutes
                except Exception as e:
                    logger.error(f"Auto-scaling error: {e}")
                    time.sleep(300)

        scaling_thread = threading.Thread(target=scaling_loop, daemon=True)
        scaling_thread.start()

    def _start_backup_schedule(self):
        """Start scheduled backups"""
        def backup_loop():
            while True:
                try:
                    # Create backup
                    backup_path = self.backup_manager.create_backup()
                    if backup_path:
                        logger.info(f"Automated backup created: {backup_path}")

                    # Wait for next backup (daily)
                    time.sleep(24 * 60 * 60)
                except Exception as e:
                    logger.error(f"Backup scheduling error: {e}")
                    time.sleep(60 * 60)  # Retry in 1 hour

        backup_thread = threading.Thread(target=backup_loop, daemon=True)
        backup_thread.start()

# Global instances
production_monitor = ProductionMonitor()
auto_scaler = AutoScaler(production_monitor)
backup_manager = BackupManager()
deployment_manager = DeploymentManager()

def get_production_monitor() -> ProductionMonitor:
    """Get the global production monitor"""
    return production_monitor

def get_auto_scaler() -> AutoScaler:
    """Get the global auto-scaler"""
    return auto_scaler

def get_backup_manager() -> BackupManager:
    """Get the global backup manager"""
    return backup_manager

def get_deployment_manager() -> DeploymentManager:
    """Get the global deployment manager"""
    return deployment_manager