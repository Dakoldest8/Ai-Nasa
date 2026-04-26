"""
Phase 4: Export + Sync System
Handles model export/import and synchronization between devices
"""

import os
import json
import shutil
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelExporter:
    """Handles AI model export operations"""

    def __init__(self, export_dir: str = "exports"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)

    def export_model(self, model_path: str, model_version: int, metadata: Dict) -> str:
        """Export a trained model with metadata"""
        try:
            # Create export directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_name = f"model_v{model_version}_{timestamp}"
            export_path = self.export_dir / export_name
            export_path.mkdir(exist_ok=True)

            # Copy model files
            if os.path.isfile(model_path):
                shutil.copy2(model_path, export_path / "model.bin")
            elif os.path.isdir(model_path):
                shutil.copytree(model_path, export_path / "model", dirs_exist_ok=True)

            # Create metadata file
            metadata.update({
                "export_timestamp": timestamp,
                "model_version": model_version,
                "export_format": "phase4_sync_v1"
            })

            with open(export_path / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2, default=str)

            # Create checksum
            checksum = self._calculate_checksum(export_path)
            with open(export_path / "checksum.sha256", "w") as f:
                f.write(checksum)

            logger.info(f"Model exported to {export_path}")
            return str(export_path)

        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise

    def _calculate_checksum(self, path: Path) -> str:
        """Calculate SHA256 checksum of export directory"""
        sha256 = hashlib.sha256()

        for file_path in sorted(path.rglob("*")):
            if file_path.is_file() and file_path.name != "checksum.sha256":
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256.update(chunk)

        return sha256.hexdigest()

class ModelImporter:
    """Handles AI model import operations"""

    def __init__(self, import_dir: str = "imports"):
        self.import_dir = Path(import_dir)
        self.import_dir.mkdir(exist_ok=True)

    def import_model(self, export_path: str, target_dir: str) -> Dict:
        """Import a model from export package"""
        try:
            export_path = Path(export_path)
            target_path = Path(target_dir)

            # Verify checksum
            if not self._verify_checksum(export_path):
                raise ValueError("Checksum verification failed")

            # Load metadata
            with open(export_path / "metadata.json", "r") as f:
                metadata = json.load(f)

            # Copy model files
            model_source = export_path / "model.bin"
            if model_source.exists():
                target_path.mkdir(parents=True, exist_ok=True)
                shutil.copy2(model_source, target_path / "model.bin")
            else:
                model_source = export_path / "model"
                if model_source.exists():
                    shutil.copytree(model_source, target_path, dirs_exist_ok=True)

            logger.info(f"Model imported to {target_path}")
            return metadata

        except Exception as e:
            logger.error(f"Import failed: {e}")
            raise

    def _verify_checksum(self, path: Path) -> bool:
        """Verify SHA256 checksum of import package"""
        checksum_file = path / "checksum.sha256"
        if not checksum_file.exists():
            return False

        with open(checksum_file, "r") as f:
            expected_checksum = f.read().strip()

        calculated_checksum = self._calculate_checksum(path)
        return expected_checksum == calculated_checksum

    def _calculate_checksum(self, path: Path) -> str:
        """Calculate SHA256 checksum"""
        sha256 = hashlib.sha256()

        for file_path in sorted(path.rglob("*")):
            if file_path.is_file() and file_path.name != "checksum.sha256":
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256.update(chunk)

        return sha256.hexdigest()

class SyncManager:
    """Manages synchronization between web assistant and Pi robot"""

    def __init__(self, web_export_dir: str = "exports", pi_import_dir: str = "pi_imports"):
        self.exporter = ModelExporter(web_export_dir)
        self.importer = ModelImporter(pi_import_dir)
        self.sync_log = []

    def sync_to_pi(self, model_path: str, model_version: int, pi_address: str = "raspberrypi.local") -> bool:
        """Sync latest model to Pi robot"""
        try:
            # Export model
            export_path = self.exporter.export_model(
                model_path=model_path,
                model_version=model_version,
                metadata={
                    "sync_type": "web_to_pi",
                    "target_device": pi_address,
                    "sync_timestamp": datetime.now().isoformat()
                }
            )

            # TODO: Implement network transfer to Pi
            # For now, just log the sync attempt
            self.sync_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "export",
                "model_version": model_version,
                "export_path": export_path,
                "target": pi_address,
                "status": "ready_for_transfer"
            })

            logger.info(f"Model v{model_version} ready for sync to Pi")
            return True

        except Exception as e:
            logger.error(f"Sync to Pi failed: {e}")
            return False

    def sync_from_pi(self, pi_export_path: str, local_import_dir: str) -> Optional[Dict]:
        """Sync model data from Pi robot"""
        try:
            # Import model from Pi
            metadata = self.importer.import_model(pi_export_path, local_import_dir)

            self.sync_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "import",
                "model_version": metadata.get("model_version"),
                "source": "pi_robot",
                "status": "completed"
            })

            logger.info(f"Model data imported from Pi: {metadata}")
            return metadata

        except Exception as e:
            logger.error(f"Sync from Pi failed: {e}")
            return None

    def get_sync_status(self) -> Dict:
        """Get current sync status and history"""
        return {
            "last_sync": self.sync_log[-1] if self.sync_log else None,
            "total_syncs": len(self.sync_log),
            "sync_history": self.sync_log[-10:],  # Last 10 syncs
            "pending_exports": len([s for s in self.sync_log if s["status"] == "ready_for_transfer"])
        }

# Global instances
exporter = ModelExporter()
importer = ModelImporter()
sync_manager = SyncManager()

def export_model_for_sync(model_path: str, model_version: int, metadata: Dict = None) -> str:
    """Convenience function to export model for synchronization"""
    if metadata is None:
        metadata = {}
    return exporter.export_model(model_path, model_version, metadata)

def import_model_from_sync(export_path: str, target_dir: str) -> Dict:
    """Convenience function to import model from synchronization"""
    return importer.import_model(export_path, target_dir)

def get_sync_manager() -> SyncManager:
    """Get the global sync manager instance"""
    return sync_manager