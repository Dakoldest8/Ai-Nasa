"""
Phase 1: Model Exporter
Creates export packages for model transfer to Pi robot
"""

import os
import json
import shutil
import zipfile
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ModelExporter:
    """Handles exporting trained models for Pi transfer"""

    def __init__(self, models_dir="./models", export_dir="../exports"):
        self.models_dir = models_dir
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)

    def get_latest_model(self):
        """Find the latest trained model"""
        if not os.path.exists(self.models_dir):
            return None

        model_dirs = []
        for item in os.listdir(self.models_dir):
            if item.startswith("model_v") and os.path.isdir(os.path.join(self.models_dir, item)):
                model_dirs.append(item)

        if not model_dirs:
            return None

        # Sort by version number
        model_dirs.sort(key=lambda x: int(x.replace("model_v", "")), reverse=True)
        return os.path.join(self.models_dir, model_dirs[0])

    def export_model(self, model_path=None):
        """Export a model for Pi transfer"""

        if model_path is None:
            model_path = self.get_latest_model()

        if not model_path or not os.path.exists(model_path):
            logger.error(f"Model path does not exist: {model_path}")
            return None

        # Load metadata
        metadata_file = os.path.join(model_path, "metadata.json")
        if not os.path.exists(metadata_file):
            logger.error(f"No metadata found for model: {model_path}")
            return None

        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        version = metadata["version"]
        export_name = f"model_v{version}"
        export_path = os.path.join(self.export_dir, export_name)

        # Create export directory
        os.makedirs(export_path, exist_ok=True)

        # Copy model files
        model_files = ["pytorch_model.bin", "config.json", "tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt", "special_tokens_map.json"]

        for file in model_files:
            src = os.path.join(model_path, file)
            if os.path.exists(src):
                shutil.copy2(src, export_path)

        # Copy safetensors if available (newer format)
        safetensors_files = [f for f in os.listdir(model_path) if f.endswith('.safetensors')]
        for file in safetensors_files:
            shutil.copy2(os.path.join(model_path, file), export_path)

        # Create export metadata
        export_metadata = {
            **metadata,
            "export_date": datetime.now().isoformat(),
            "export_format": "huggingface",
            "target_platform": "raspberry_pi",
            "transfer_method": "usb_storage"
        }

        with open(os.path.join(export_path, "export_metadata.json"), 'w') as f:
            json.dump(export_metadata, f, indent=2)

        # Create zip archive for easy transfer
        zip_path = os.path.join(self.export_dir, f"{export_name}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(export_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.export_dir)
                    zipf.write(file_path, arcname)

        logger.info(f"Model exported to: {export_path}")
        logger.info(f"Zip archive created: {zip_path}")

        return {
            "export_path": export_path,
            "zip_path": zip_path,
            "version": version,
            "metadata": export_metadata
        }

    def list_exports(self):
        """List all exported model packages"""
        if not os.path.exists(self.export_dir):
            return []

        exports = []
        for item in os.listdir(self.export_dir):
            if item.startswith("model_v") and os.path.isdir(os.path.join(self.export_dir, item)):
                metadata_file = os.path.join(self.export_dir, item, "export_metadata.json")
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    exports.append(metadata)

        return sorted(exports, key=lambda x: x["version"], reverse=True)

def export_latest_model():
    """Convenience function to export the latest model"""
    exporter = ModelExporter()
    return exporter.export_model()

if __name__ == "__main__":
    # Example usage
    exporter = ModelExporter()
    result = exporter.export_model()
    if result:
        print(f"Exported model v{result['version']} to: {result['export_path']}")
        print(f"Zip: {result['zip_path']}")
    else:
        print("No model available to export")