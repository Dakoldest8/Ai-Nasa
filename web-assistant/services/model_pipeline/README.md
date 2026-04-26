# Phase 1: Core Model Pipeline

This phase establishes the foundation for model training, versioning, and transfer between the web assistant and Pi robot.

## Overview

The pipeline consists of three main components:

1. **Model Trainer** (`trainer.py`) - Trains AI models using interaction data
2. **Model Exporter** (`exporter.py`) - Packages trained models for transfer
3. **Pi Model Loader** (`pi_model_loader.py`) - Loads models on Raspberry Pi

## Directory Structure

```
web-assistant/services/model_pipeline/
├── __init__.py
├── trainer.py          # Model training logic
├── exporter.py         # Model export/packaging
├── sample_data.py      # Generate test data
└── test_pipeline.py    # End-to-end test

be-more-agent-main/
└── pi_model_loader.py  # Pi-side model loading
```

## Quick Start

### 1. Install Dependencies

```bash
# On web assistant (Windows)
pip install transformers torch accelerate

# On Pi (if testing locally)
pip install transformers torch
```

### 2. Generate Sample Data

```python
from sample_data import save_sample_data
save_sample_data("interactions.json", 100)
```

### 3. Train a Model

```python
from trainer import train_model
model_path = train_model("interactions.json")
```

### 4. Export for Pi Transfer

```python
from exporter import export_latest_model
result = export_latest_model()
print(f"Model exported to: {result['zip_path']}")
```

### 5. Load on Pi

```python
# On Raspberry Pi
from pi_model_loader import check_for_model_updates
success = check_for_model_updates()
```

## Manual Transfer Process

1. **Web Assistant**: Run export to create model package
2. **Transfer**: Copy the `.zip` file to USB drive
3. **Pi Robot**: Insert USB, run loader to import model
4. **Verification**: Check that Pi is using new model version

## Files Created

### Training Output
- `models/model_v1/` - First trained model
- `models/model_v2/` - Second trained model (etc.)

### Export Output
- `exports/model_v1/` - Export directory with model files
- `exports/model_v1.zip` - Compressed archive for transfer

### Pi Loading
- `/home/pi/models/model_v1/` - Loaded model on Pi

## Configuration

### Model Trainer
```python
trainer = ModelTrainer(
    base_model="microsoft/DialoGPT-small",  # Base model to fine-tune
    output_dir="./models"                   # Where to save trained models
)
```

### Model Exporter
```python
exporter = ModelExporter(
    models_dir="./models",    # Source of trained models
    export_dir="../exports"   # Export destination
)
```

### Pi Model Loader
```python
loader = PiModelLoader(
    export_mount="/mnt/usb",  # USB mount point
    models_dir="./models"     # Local Pi model storage
)
```

## Testing

Run the complete pipeline test:

```bash
cd web-assistant/services/model_pipeline
python test_pipeline.py
```

This will:
- Generate sample data
- Train a model
- Export it
- Simulate Pi loading
- Clean up test files

## Next Steps

After Phase 1 is working:
- **Phase 2**: Add MySQL database to track models and interactions
- **Phase 3**: Implement smart training triggers
- **Phase 4**: Enhanced export system with metadata
- **Phase 5**: Pi-side update logic with backups

## Troubleshooting

### Training Issues
- Ensure `transformers` and `torch` are installed
- Check available disk space (models can be several GB)
- Use smaller `batch_size` if running out of memory

### Export Issues
- Ensure write permissions to export directory
- Check that model files exist before exporting

### Pi Loading Issues
- Verify USB mount path is correct
- Ensure Pi has read/write access to model directory
- Check that exported model files are intact