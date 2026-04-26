"""
Phase 3: Automated Training Service
Runs in background and automatically trains models when triggers are met
"""

import time
import logging
import threading
from datetime import datetime
from typing import Optional, Dict
from .trigger_logic import get_training_trigger
from ..model_pipeline.trainer import ModelTrainer
from ..database.model_tracker import get_model_tracker

logger = logging.getLogger(__name__)

class AutomatedTrainingService:
    """Background service that automatically trains models based on triggers"""

    def __init__(self, check_interval_minutes=15, auto_start=True):
        self.check_interval_minutes = check_interval_minutes
        self.is_running = False
        self.training_thread = None
        self.last_check_time = None

        self.trigger = get_training_trigger()
        self.model_tracker = get_model_tracker()

        if auto_start:
            self.start()

    def start(self):
        """Start the automated training service"""
        if self.is_running:
            logger.warning("Automated training service is already running")
            return

        self.is_running = True
        self.training_thread = threading.Thread(target=self._training_loop, daemon=True)
        self.training_thread.start()

        logger.info(f"Automated training service started (check every {self.check_interval_minutes} minutes)")

    def stop(self):
        """Stop the automated training service"""
        self.is_running = False
        if self.training_thread:
            self.training_thread.join(timeout=30)
        logger.info("Automated training service stopped")

    def _training_loop(self):
        """Main training loop that runs in background"""
        while self.is_running:
            try:
                self._check_and_train()
                self.last_check_time = datetime.now()

                # Sleep for check interval
                time.sleep(self.check_interval_minutes * 60)

            except Exception as e:
                logger.error(f"Error in training loop: {e}")
                time.sleep(60)  # Brief pause on error

    def _check_and_train(self):
        """Check triggers and train if needed"""
        try:
            # Check if training should be triggered
            should_train, reason = self.trigger.should_trigger_training()

            if should_train:
                logger.info(f"Training trigger activated: {reason}")
                self._perform_training()
            else:
                logger.debug(f"Training not triggered: {reason}")

        except Exception as e:
            logger.error(f"Error checking training triggers: {e}")

    def _perform_training(self):
        """Perform the actual model training"""
        try:
            # Update system status
            self.model_tracker.db.update_system_state({
                'system_status': 'training',
                'pending_training': False
            })

            logger.info("Starting automated model training...")

            # Create trainer and train model
            trainer = ModelTrainer()
            model_path = trainer.train()

            if model_path:
                logger.info(f"Automated training completed successfully: {model_path}")

                # System status back to active
                self.model_tracker.db.update_system_state({
                    'system_status': 'active'
                })

                return True
            else:
                logger.error("Automated training failed - no model path returned")
                self.model_tracker.db.update_system_state({
                    'system_status': 'error'
                })
                return False

        except Exception as e:
            logger.error(f"Error during automated training: {e}")
            try:
                self.model_tracker.db.update_system_state({
                    'system_status': 'error'
                })
            except Exception:
                pass
            return False

    def manual_train_now(self) -> bool:
        """Manually trigger training immediately (for testing/admin)"""
        try:
            logger.info("Manual training requested")
            success = self._perform_training()
            return success
        except Exception as e:
            logger.error(f"Error in manual training: {e}")
            return False

    def get_service_status(self) -> Dict:
        """Get status of the automated training service"""
        return {
            "service_running": self.is_running,
            "check_interval_minutes": self.check_interval_minutes,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "trigger_status": self.trigger.get_trigger_status()
        }

# Global service instance
_training_service = None

def get_training_service(**kwargs) -> AutomatedTrainingService:
    """Get the global automated training service instance"""
    global _training_service
    if _training_service is None:
        _training_service = AutomatedTrainingService(**kwargs)
    return _training_service

def start_automated_training(**kwargs):
    """Start the automated training service"""
    service = get_training_service(**kwargs)
    service.start()
    return service

def stop_automated_training():
    """Stop the automated training service"""
    global _training_service
    if _training_service:
        _training_service.stop()
        _training_service = None

def manual_train_now(**kwargs) -> bool:
    """Manually trigger training"""
    service = get_training_service(**kwargs)
    return service.manual_train_now()

def get_training_service_status(**kwargs) -> Dict:
    """Get training service status"""
    service = get_training_service(**kwargs)
    return service.get_service_status()