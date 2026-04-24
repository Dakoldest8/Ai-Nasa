"""
Phase 1: Complete Pipeline Test
Demonstrates the full model training → export → load cycle
"""

import os
import sys
import json
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.dirname(__file__))

from trainer import ModelTrainer
from exporter import ModelExporter
from sample_data import generate_sample_interactions

def test_phase1_pipeline():
    """Test the complete Phase 1 pipeline"""

    print("🚀 Phase 1: Core Model Pipeline Test")
    print("=" * 50)

    # Step 1: Generate sample training data
    print("\n📊 Step 1: Generating sample interaction data...")
    interactions = generate_sample_interactions(20)  # Small dataset for quick testing

    # Save to file
    with open("test_interactions.json", 'w') as f:
        json.dump(interactions, f, indent=2)

    print(f"✅ Generated {len(interactions)} sample interactions")

    # Step 2: Train model
    print("\n🤖 Step 2: Training model...")
    try:
        trainer = ModelTrainer(
            base_model="microsoft/DialoGPT-small",  # Small model for testing
            output_dir="./test_models"
        )

        model_path = trainer.train(
            interactions=interactions,
            num_epochs=1,  # Quick training for demo
            batch_size=2,
            learning_rate=1e-4
        )

        if model_path:
            print(f"✅ Model trained and saved to: {model_path}")
        else:
            print("❌ Model training failed")
            return False

    except Exception as e:
        print(f"❌ Training error: {e}")
        print("Note: This requires transformers and torch to be installed")
        return False

    # Step 3: Export model
    print("\n📦 Step 3: Exporting model for Pi transfer...")
    try:
        exporter = ModelExporter(
            models_dir="./test_models",
            export_dir="./test_exports"
        )

        export_result = exporter.export_model(model_path)

        if export_result:
            print(f"✅ Model exported to: {export_result['export_path']}")
            print(f"✅ Zip archive: {export_result['zip_path']}")
            print(f"✅ Version: {export_result['version']}")
        else:
            print("❌ Model export failed")
            return False

    except Exception as e:
        print(f"❌ Export error: {e}")
        return False

    # Step 4: Simulate Pi loading
    print("\n🔄 Step 4: Simulating Pi model loading...")
    try:
        # Import Pi loader (would normally be on Pi)
        sys.path.append("../../be-more-agent-main")
        from pi_model_loader import PiModelLoader

        # Create a mock USB mount by copying export to a temp location
        import shutil
        mock_usb = "./mock_usb"
        os.makedirs(mock_usb, exist_ok=True)

        # Copy the exported model to mock USB
        export_name = os.path.basename(export_result['export_path'])
        mock_model_path = os.path.join(mock_usb, export_name)
        shutil.copytree(export_result['export_path'], mock_model_path)

        # Load model as Pi would
        loader = PiModelLoader(export_mount=mock_usb, models_dir="./test_pi_models")
        success = loader.load_latest_model()

        if success:
            model_info = loader.get_current_model_info()
            print(f"✅ Pi successfully loaded model v{model_info['version']}")
            print(f"✅ Model path: {model_info['path']}")
        else:
            print("❌ Pi model loading failed")
            return False

    except Exception as e:
        print(f"❌ Pi loading error: {e}")
        return False

    # Cleanup
    print("\n🧹 Cleaning up test files...")
    import shutil
    for dir_path in ["./test_models", "./test_exports", "./test_pi_models", "./mock_usb"]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)

    if os.path.exists("test_interactions.json"):
        os.remove("test_interactions.json")

    print("✅ Cleanup complete")

    print("\n🎉 Phase 1 Pipeline Test: SUCCESS!")
    print("\nSummary:")
    print("- ✅ Model training works")
    print("- ✅ Model export works")
    print("- ✅ Pi model loading works")
    print("- ✅ Version tracking works")
    print("\nReady for Phase 2: MySQL Brain Integration")

    return True

if __name__ == "__main__":
    success = test_phase1_pipeline()
    sys.exit(0 if success else 1)