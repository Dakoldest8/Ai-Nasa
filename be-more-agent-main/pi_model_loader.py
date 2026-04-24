"""
Phase 1: Pi Model Loader
Loads exported models from web assistant on Raspberry Pi
"""

import os
import json
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PiModelLoader:
    """Loads models exported from web assistant"""

    def __init__(self, export_mount="/mnt/usb", models_dir="./models"):
        self.export_mount = Path(export_mount)  # USB mount point
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)

        # Current loaded model info
        self.current_version = None
        self.current_model_path = None

    def find_exported_models(self):
        """Scan for exported model packages on USB"""
        if not self.export_mount.exists():
            logger.warning(f"USB mount not found: {self.export_mount}")
            return []

        models_found = []

        # Look for model directories
        for item in self.export_mount.iterdir():
            if item.is_dir() and item.name.startswith("model_v"):
                metadata_file = item / "export_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        models_found.append({
                            "path": item,
                            "metadata": metadata
                        })
                    except Exception as e:
                        logger.warning(f"Failed to read metadata for {item}: {e}")

        # Also check for zip files
        for item in self.export_mount.iterdir():
            if item.is_file() and item.name.startswith("model_v") and item.suffix == ".zip":
                models_found.append({
                    "path": item,
                    "is_zip": True,
                    "version": self._extract_version_from_name(item.name)
                })

        # Sort by version (highest first)
        models_found.sort(key=lambda x: x["metadata"]["version"] if "metadata" in x else x["version"], reverse=True)

        return models_found

    def _extract_version_from_name(self, name):
        """Extract version number from filename like 'model_v5.zip'"""
        try:
            return int(name.replace("model_v", "").replace(".zip", ""))
        except ValueError:
            return 0

    def load_latest_model(self):
        """Load the latest available model from USB"""
        models = self.find_exported_models()

        if not models:
            logger.info("No exported models found on USB")
            return False

        latest_model = models[0]

        if latest_model.get("is_zip"):
            # Extract zip
            success = self._extract_zip_model(latest_model["path"])
            if not success:
                return False
            model_path = self._get_extracted_path(latest_model["path"])
        else:
            # Copy directory
            model_path = self._copy_model_directory(latest_model["path"])

        if model_path:
            self.current_version = latest_model["metadata"]["version"]
            self.current_model_path = model_path
            logger.info(f"Loaded model v{self.current_version} from {model_path}")
            return True

        return False

    def _extract_zip_model(self, zip_path):
        """Extract a zipped model package"""
        try:
            import zipfile

            extract_dir = self.models_dir / f"model_v{self._extract_version_from_name(zip_path.name)}"
            extract_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            logger.info(f"Extracted {zip_path} to {extract_dir}")
            return True

        except Exception as e:
            logger.error(f"Failed to extract {zip_path}: {e}")
            return False

    def _copy_model_directory(self, source_path):
        """Copy a model directory to local models folder"""
        try:
            version = source_path.name.replace("model_v", "")
            dest_path = self.models_dir / f"model_v{version}"

            if dest_path.exists():
                shutil.rmtree(dest_path)

            shutil.copytree(source_path, dest_path)
            logger.info(f"Copied model from {source_path} to {dest_path}")
            return dest_path

        except Exception as e:
            logger.error(f"Failed to copy model directory: {e}")
            return None

    def _get_extracted_path(self, zip_path):
        """Get path where zip was extracted"""
        version = self._extract_version_from_name(zip_path.name)
        return self.models_dir / f"model_v{version}"

    def get_current_model_info(self):
        """Get info about currently loaded model"""
        if not self.current_model_path:
            return None

        metadata_file = self.current_model_path / "export_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "version": self.current_version,
            "path": str(self.current_model_path),
            "status": "loaded"
        }

    def list_local_models(self):
        """List models stored locally on Pi"""
        if not self.models_dir.exists():
            return []

        models = []
        for item in self.models_dir.iterdir():
            if item.is_dir() and item.name.startswith("model_v"):
                metadata_file = item / "export_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        models.append(metadata)
                    except Exception:
                        models.append({
                            "version": self._extract_version_from_name(item.name),
                            "path": str(item),
                            "status": "local_only"
                        })

        return sorted(models, key=lambda x: x["version"], reverse=True)

def check_for_model_updates():
    """Convenience function to check and load latest model"""
    loader = PiModelLoader()
    return loader.load_latest_model()

if __name__ == "__main__":
    # Example usage
    loader = PiModelLoader()

    print("Scanning for exported models...")
    models = loader.find_exported_models()
    print(f"Found {len(models)} exported models")

    if models:
        print(f"Loading latest model (v{models[0]['metadata']['version']})...")
        success = loader.load_latest_model()
        if success:
            info = loader.get_current_model_info()
            print(f"Loaded: {info}")
        else:
            print("Failed to load model")
    else:
        print("No models found to load")