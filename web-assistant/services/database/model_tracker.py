"""
Phase 2: Model Tracker
Tracks model versions and training history in MySQL database
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, List
from .connection import get_db_manager

logger = logging.getLogger(__name__)

class ModelTracker:
    """Tracks AI model versions and training history"""

    def __init__(self):
        self.db = get_db_manager()

    def record_model_training(self, version: int, file_name: str, training_data: dict) -> bool:
        """Record a newly trained model"""
        try:
            notes = training_data.get('notes', '')
            training_interactions = training_data.get('training_interactions', 0)
            base_model = training_data.get('base_model', '')

            success = self.db.save_model_record(
                version=version,
                file_name=file_name,
                notes=notes,
                training_interactions=training_interactions,
                base_model=base_model
            )

            if success:
                logger.info(f"Recorded model v{version} in database")
                # Update system state
                self.db.update_system_state({
                    'last_model_version': version,
                    'last_update': datetime.now()
                })
            else:
                logger.error(f"Failed to record model v{version}")

            return success

        except Exception as e:
            logger.error(f"Error recording model training: {e}")
            return False

    def get_latest_model_info(self) -> Optional[Dict]:
        """Get information about the latest trained model"""
        try:
            return self.db.get_latest_model()
        except Exception as e:
            logger.error(f"Error getting latest model info: {e}")
            return None

    def get_all_models(self) -> List[Dict]:
        """Get all models ordered by version"""
        try:
            return self.db.get_models_list()
        except Exception as e:
            logger.error(f"Error getting models list: {e}")
            return []

    def get_model_by_version(self, version: int) -> Optional[Dict]:
        """Get model information by version number"""
        try:
            models = self.db.get_models_list()
            for model in models:
                if model['version'] == version:
                    return model
            return None
        except Exception as e:
            logger.error(f"Error getting model v{version}: {e}")
            return None

    def update_model_status(self, version: int, status: str) -> bool:
        """Update model status (training, completed, exported, failed)"""
        try:
            query = "UPDATE models SET status = %s WHERE version = %s"
            result = self.db.execute_query(query, (status, version))
            return result is not None
        except Exception as e:
            logger.error(f"Error updating model v{version} status: {e}")
            return False

    def get_system_state(self) -> Optional[Dict]:
        """Get current system state"""
        try:
            return self.db.get_system_state()
        except Exception as e:
            logger.error(f"Error getting system state: {e}")
            return None

    def trigger_training_check(self) -> bool:
        """Check if training should be triggered and update state"""
        try:
            state = self.db.get_system_state()
            if not state:
                return False

            # Get unused interactions count
            unused_count = self.db.get_unused_interactions_count()

            # Simple trigger: if we have 50+ unused interactions, trigger training
            should_train = unused_count >= 50

            self.db.update_system_state({
                'pending_training': should_train,
                'last_training_trigger': datetime.now() if should_train else state.get('last_training_trigger')
            })

            if should_train:
                logger.info(f"Training triggered: {unused_count} unused interactions available")

            return should_train

        except Exception as e:
            logger.error(f"Error checking training trigger: {e}")
            return False

    def get_training_data_summary(self) -> Dict:
        """Get summary of available training data"""
        try:
            total = self.db.get_total_interactions()
            unused = self.db.get_unused_interactions_count()
            latest_model = self.get_latest_model_info()

            return {
                "total_interactions": total,
                "unused_interactions": unused,
                "used_interactions": total - unused,
                "latest_model_version": latest_model['version'] if latest_model else 0,
                "training_ready": unused >= 50
            }
        except Exception as e:
            logger.error(f"Error getting training data summary: {e}")
            return {"error": str(e)}

# Global tracker instance
_model_tracker = None

def get_model_tracker() -> ModelTracker:
    """Get the global model tracker instance"""
    global _model_tracker
    if _model_tracker is None:
        _model_tracker = ModelTracker()
    return _model_tracker

def record_new_model(version: int, file_name: str, training_data: dict) -> bool:
    """Convenience function to record a new model"""
    tracker = get_model_tracker()
    return tracker.record_model_training(version, file_name, training_data)

def should_trigger_training() -> bool:
    """Convenience function to check if training should be triggered"""
    tracker = get_model_tracker()
    return tracker.trigger_training_check()

def get_training_summary() -> Dict:
    """Convenience function to get training data summary"""
    tracker = get_model_tracker()
    return tracker.get_training_data_summary()