"""
Phase 1: Model Trainer
Trains AI models using interaction data from the web assistant
"""

import os
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
import numpy as np
from datetime import datetime
import logging

# Phase 2: Database integration
try:
    from ..database.model_tracker import record_new_model, get_model_tracker
    from ..database.interaction_logger import get_interaction_logger
    DB_ENABLED = True
except ImportError:
    try:
        from database.model_tracker import record_new_model, get_model_tracker
        from database.interaction_logger import get_interaction_logger
        DB_ENABLED = True
    except ImportError:
        DB_ENABLED = False

logger = logging.getLogger(__name__)

class InteractionDataset(Dataset):
    """Dataset for training on user interactions"""

    def __init__(self, interactions, tokenizer, max_length=512):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.data = []

        for interaction in interactions:
            # Format as conversation
            text = f"User: {interaction['input']}\nAssistant: {interaction['response']}\n"
            self.data.append(text)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        text = self.data[idx]
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': encoding['input_ids'].flatten()  # For causal LM
        }

class ModelTrainer:
    """Handles training of AI models"""

    def __init__(self, base_model="microsoft/DialoGPT-small", output_dir="./models"):
        self.base_model = base_model
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(base_model)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(base_model)

    def load_interactions(self, interactions_file="interactions.json", use_database=True):
        """Load interaction data for training"""
        interactions = []

        # Phase 2: Try to load from database first
        if DB_ENABLED and use_database:
            try:
                interaction_logger = get_interaction_logger()
                db_interactions = interaction_logger.get_recent_interactions(limit=1000)

                if db_interactions:
                    logger.info(f"Loaded {len(db_interactions)} interactions from database")
                    # Convert database format to expected format
                    for db_int in db_interactions:
                        interactions.append({
                            "id": db_int["id"],
                            "input": db_int["input"],
                            "response": db_int["response"],
                            "timestamp": db_int["timestamp"].isoformat() if hasattr(db_int["timestamp"], 'isoformat') else str(db_int["timestamp"])
                        })
                    return interactions
                else:
                    logger.info("No interactions found in database, trying file fallback")

            except Exception as e:
                logger.error(f"Database loading error: {e}, falling back to file")

        # Fallback to file loading
        if not os.path.exists(interactions_file):
            logger.warning(f"No interactions file found: {interactions_file}")
            return []

        with open(interactions_file, 'r') as f:
            file_interactions = json.load(f)

        logger.info(f"Loaded {len(file_interactions)} interactions from file")
        interactions.extend(file_interactions)

        return interactions

    def train(self, interactions=None, num_epochs=3, batch_size=4, learning_rate=5e-5):
        """Train the model on interaction data"""

        if interactions is None:
            interactions = self.load_interactions()

        if not interactions:
            logger.error("No interaction data available for training")
            return None

        # Create dataset
        dataset = InteractionDataset(interactions, self.tokenizer)

        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            learning_rate=learning_rate,
            save_steps=500,
            save_total_limit=2,
            logging_steps=100,
            evaluation_strategy="no",
            load_best_model_at_end=False,
        )

        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
        )

        # Train
        logger.info("Starting model training...")
        trainer.train()

        # Generate version info
        version = self._generate_version()
        model_path = os.path.join(self.output_dir, f"model_v{version}")

        # Save model
        trainer.save_model(model_path)
        self.tokenizer.save_pretrained(model_path)

        # Save metadata
        metadata = {
            "version": version,
            "base_model": self.base_model,
            "trained_on": len(interactions),
            "training_date": datetime.now().isoformat(),
            "epochs": num_epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate
        }

        with open(os.path.join(model_path, "metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2)

        # Phase 2: Record model in database
        if DB_ENABLED:
            try:
                training_data = {
                    "notes": f"Trained on {len(interactions)} interactions",
                    "training_interactions": len(interactions),
                    "base_model": self.base_model
                }

                record_success = record_new_model(version, f"model_v{version}", training_data)
                if record_success:
                    logger.info(f"Model v{version} recorded in database")

                    # Mark interactions as used for training
                    interaction_logger = get_interaction_logger()
                    interaction_ids = [int(interaction.get('id', 0)) for interaction in interactions if interaction.get('id')]
                    if interaction_ids:
                        interaction_logger.mark_as_used_for_training(interaction_ids)
                        logger.info(f"Marked {len(interaction_ids)} interactions as used for training")
                else:
                    logger.error("Failed to record model in database")

            except Exception as e:
                logger.error(f"Database recording error: {e}")

        logger.info(f"Model saved to {model_path}")
        return model_path

    def _generate_version(self):
        """Generate next version number"""
        existing_versions = []
        for item in os.listdir(self.output_dir):
            if item.startswith("model_v") and os.path.isdir(os.path.join(self.output_dir, item)):
                try:
                    version = int(item.replace("model_v", ""))
                    existing_versions.append(version)
                except ValueError:
                    continue

        return max(existing_versions) + 1 if existing_versions else 1

def train_model(interactions_file="interactions.json", **kwargs):
    """Convenience function to train a model"""
    trainer = ModelTrainer(**kwargs)
    return trainer.train()

if __name__ == "__main__":
    # Example usage
    trainer = ModelTrainer()
    model_path = trainer.train()
    print(f"Trained model saved to: {model_path}")