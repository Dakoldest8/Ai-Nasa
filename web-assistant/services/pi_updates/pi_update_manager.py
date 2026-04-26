"""
Phase 5: Pi Robot Update Logic
Handles automatic model updates and validation on Pi robot
"""

import os
import json
import logging
import requests
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import time

logger = logging.getLogger(__name__)

class PiUpdateManager:
    """Manages model updates on Pi robot"""

    def __init__(self, web_server_url: str = "http://localhost:8000",
                 model_dir: str = "models", backup_dir: str = "models/backup"):
        self.web_server_url = web_server_url
        self.model_dir = Path(model_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.current_model_version = self._get_current_version()

    def check_for_updates(self) -> Optional[Dict]:
        """Check web server for available model updates"""
        try:
            response = requests.get(f"{self.web_server_url}/sync/status", timeout=10)
            if response.status_code == 200:
                status = response.json()
                if status.get("sync_status", {}).get("pending_exports", 0) > 0:
                    # Get latest export info
                    exports_response = requests.get(f"{self.web_server_url}/sync/exports", timeout=10)
                    if exports_response.status_code == 200:
                        exports_data = exports_response.json()
                        exports = exports_data.get("exports", [])
                        if exports:
                            latest_export = max(exports, key=lambda x: x["metadata"].get("model_version", 0))
                            return latest_export
            return None
        except Exception as e:
            logger.error(f"Update check failed: {e}")
            return None

    def download_update(self, export_info: Dict) -> Optional[str]:
        """Download model update from web server"""
        try:
            # For now, simulate download - in real implementation would use scp/rsync
            # or direct file transfer from web server
            export_path = export_info["path"]
            local_path = self.model_dir / "downloads" / Path(export_path).name
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Simulate download
            logger.info(f"Simulating download of {export_path} to {local_path}")
            time.sleep(1)  # Simulate network delay

            # In real implementation:
            # - Use requests to download from web server endpoint
            # - Or use scp/rsync for direct file transfer
            # - Or use WebSocket for real-time transfer

            return str(local_path)

        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None

    def validate_update(self, download_path: str) -> bool:
        """Validate downloaded model update"""
        try:
            download_path = Path(download_path)

            # Check if download directory exists
            if not download_path.exists():
                logger.error(f"Download path does not exist: {download_path}")
                return False

            # Check metadata
            metadata_file = download_path / "metadata.json"
            if not metadata_file.exists():
                logger.error("Metadata file missing")
                return False

            with open(metadata_file, "r") as f:
                metadata = json.load(f)

            # Verify checksum
            checksum_file = download_path / "checksum.sha256"
            if checksum_file.exists():
                with open(checksum_file, "r") as f:
                    expected_checksum = f.read().strip()

                calculated_checksum = self._calculate_checksum(download_path)
                if expected_checksum != calculated_checksum:
                    logger.error("Checksum verification failed")
                    return False

            # Check model version
            new_version = metadata.get("model_version", 0)
            if new_version <= self.current_model_version:
                logger.info(f"Model version {new_version} not newer than current {self.current_model_version}")
                return False

            logger.info(f"Update validation successful for model v{new_version}")
            return True

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False

    def apply_update(self, download_path: str) -> bool:
        """Apply the model update"""
        try:
            download_path = Path(download_path)

            # Load metadata
            with open(download_path / "metadata.json", "r") as f:
                metadata = json.load(f)

            new_version = metadata["model_version"]

            # Create backup of current model
            self._backup_current_model()

            # Copy new model files
            model_source = download_path / "model.bin"
            if model_source.exists():
                target_path = self.model_dir / f"model_v{new_version}.bin"
                import shutil
                shutil.copy2(model_source, target_path)
            else:
                model_source = download_path / "model"
                if model_source.exists():
                    target_path = self.model_dir / f"model_v{new_version}"
                    shutil.copytree(model_source, target_path, dirs_exist_ok=True)

            # Update current version
            self.current_model_version = new_version
            self._save_version_info(new_version, metadata)

            logger.info(f"Update applied successfully: model v{new_version}")
            return True

        except Exception as e:
            logger.error(f"Update application failed: {e}")
            # Attempt rollback
            self._rollback_update()
            return False

    def _backup_current_model(self):
        """Create backup of current model"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_v{self.current_model_version}_{timestamp}"

            # Copy current model files
            for item in self.model_dir.glob("model_*"):
                if item.is_file() or item.is_dir():
                    import shutil
                    if item.is_file():
                        shutil.copy2(item, backup_path / item.name)
                    else:
                        shutil.copytree(item, backup_path / item.name, dirs_exist_ok=True)

            logger.info(f"Backup created: {backup_path}")

        except Exception as e:
            logger.error(f"Backup failed: {e}")

    def _rollback_update(self):
        """Rollback to previous model version"""
        try:
            # Find latest backup
            backups = list(self.backup_dir.glob("backup_*"))
            if backups:
                latest_backup = max(backups, key=lambda x: x.stat().st_mtime)

                # Restore from backup
                import shutil
                for item in latest_backup.iterdir():
                    target = self.model_dir / item.name
                    if item.is_file():
                        shutil.copy2(item, target)
                    else:
                        shutil.copytree(item, target, dirs_exist_ok=True)

                logger.info(f"Rolled back to backup: {latest_backup}")
                return True

        except Exception as e:
            logger.error(f"Rollback failed: {e}")

        return False

    def _get_current_version(self) -> int:
        """Get current model version"""
        try:
            version_file = self.model_dir / "current_version.json"
            if version_file.exists():
                with open(version_file, "r") as f:
                    data = json.load(f)
                    return data.get("version", 0)
        except Exception:
            pass
        return 0

    def _save_version_info(self, version: int, metadata: Dict):
        """Save current version information"""
        try:
            version_file = self.model_dir / "current_version.json"
            data = {
                "version": version,
                "updated_at": datetime.now().isoformat(),
                "metadata": metadata
            }
            with open(version_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save version info: {e}")

    def _calculate_checksum(self, path: Path) -> str:
        """Calculate SHA256 checksum"""
        sha256 = hashlib.sha256()

        for file_path in sorted(path.rglob("*")):
            if file_path.is_file() and file_path.name != "checksum.sha256":
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256.update(chunk)

        return sha256.hexdigest()

    def get_update_status(self) -> Dict:
        """Get current update status"""
        return {
            "current_version": self.current_model_version,
            "last_check": getattr(self, '_last_check', None),
            "update_available": self.check_for_updates() is not None,
            "backups_available": len(list(self.backup_dir.glob("backup_*"))) > 0
        }

class AutoUpdateService:
    """Background service for automatic model updates"""

    def __init__(self, update_manager: PiUpdateManager, check_interval_hours: int = 6):
        self.update_manager = update_manager
        self.check_interval = timedelta(hours=check_interval_hours)
        self.last_check = None
        self.running = False

    def start_auto_updates(self):
        """Start automatic update checking"""
        self.running = True
        logger.info("Auto-update service started")

        while self.running:
            try:
                now = datetime.now()

                # Check if it's time for update check
                if self.last_check is None or (now - self.last_check) > self.check_interval:
                    self._check_and_apply_updates()
                    self.last_check = now

                # Wait before next check
                time.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Auto-update error: {e}")
                time.sleep(60)  # Wait 1 minute on error

    def stop_auto_updates(self):
        """Stop automatic update checking"""
        self.running = False
        logger.info("Auto-update service stopped")

    def _check_and_apply_updates(self):
        """Check for and apply updates"""
        try:
            update_info = self.update_manager.check_for_updates()
            if update_info:
                logger.info("Update available, starting download...")

                download_path = self.update_manager.download_update(update_info)
                if download_path and self.update_manager.validate_update(download_path):
                    logger.info("Update validated, applying...")

                    if self.update_manager.apply_update(download_path):
                        logger.info("Update applied successfully")
                    else:
                        logger.error("Update application failed")
                else:
                    logger.error("Update validation failed")
            else:
                logger.debug("No updates available")

        except Exception as e:
            logger.error(f"Update check/apply failed: {e}")

# Global instances
update_manager = PiUpdateManager()
auto_update_service = AutoUpdateService(update_manager)

def get_pi_update_manager() -> PiUpdateManager:
    """Get the global Pi update manager instance"""
    return update_manager

def get_auto_update_service() -> AutoUpdateService:
    """Get the global auto-update service instance"""
    return auto_update_service