"""
Phase 3: Smart Training Triggers
Automatically decides when to train new models based on database state
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from ..database.model_tracker import get_model_tracker
from ..database.interaction_logger import get_interaction_logger

logger = logging.getLogger(__name__)

class TrainingTrigger:
    """Smart training trigger that decides when to train based on multiple criteria"""

    def __init__(self, min_interactions=50, max_training_gap_hours=24, sentiment_threshold=0.3):
        self.min_interactions = min_interactions  # Minimum unused interactions to trigger
        self.max_training_gap_hours = max_training_gap_hours  # Max hours between training
        self.sentiment_threshold = sentiment_threshold  # Sentiment score threshold for priority training

        self.model_tracker = get_model_tracker()
        self.interaction_logger = get_interaction_logger()

    def should_trigger_training(self) -> Tuple[bool, str]:
        """
        Check if training should be triggered
        Returns: (should_train, reason)
        """
        try:
            # Get current system state
            summary = self.model_tracker.get_training_data_summary()

            if "error" in summary:
                return False, f"Database error: {summary['error']}"

            unused_interactions = summary.get('unused_interactions', 0)
            total_interactions = summary.get('total_interactions', 0)

            # Check 1: Minimum interaction threshold
            if unused_interactions < self.min_interactions:
                return False, f"Only {unused_interactions} unused interactions (need {self.min_interactions})"

            # Check 2: Time-based trigger (don't train too frequently)
            last_training_time = self._get_last_training_time()
            if last_training_time:
                hours_since_training = (datetime.now() - last_training_time).total_seconds() / 3600
                if hours_since_training < self.max_training_gap_hours:
                    return False, f"Last training was {hours_since_training:.1f} hours ago (min gap: {self.max_training_gap_hours}h)"

            # Check 3: Sentiment-based priority (high sentiment scores = urgent training)
            sentiment_score = self._calculate_average_sentiment()
            if sentiment_score > self.sentiment_threshold:
                logger.info(f"Priority training triggered: high sentiment score {sentiment_score:.2f}")
                return True, f"High sentiment score {sentiment_score:.2f} triggers priority training"

            # Check 4: Interaction quality (ensure we have diverse agent types)
            agent_diversity = self._check_agent_diversity()
            if not agent_diversity:
                return False, "Insufficient agent type diversity in training data"

            # All checks passed
            return True, f"Ready to train: {unused_interactions} unused interactions, diverse data, timing OK"

        except Exception as e:
            logger.error(f"Error checking training trigger: {e}")
            return False, f"Error: {str(e)}"

    def _get_last_training_time(self) -> Optional[datetime]:
        """Get the timestamp of the last training"""
        try:
            state = self.model_tracker.get_system_state()
            if state and state.get('last_training_trigger'):
                return state['last_training_trigger']
            return None
        except Exception:
            return None

    def _calculate_average_sentiment(self) -> float:
        """Calculate average sentiment score from recent unused interactions"""
        try:
            recent_interactions = self.interaction_logger.get_recent_interactions(limit=100)
            sentiment_scores = []

            for interaction in recent_interactions:
                if not interaction.get('used_for_training', True):  # Only unused
                    score = interaction.get('sentiment_score')
                    if score is not None:
                        sentiment_scores.append(abs(score))  # Use absolute value for magnitude

            if sentiment_scores:
                return sum(sentiment_scores) / len(sentiment_scores)
            return 0.0

        except Exception:
            return 0.0

    def _check_agent_diversity(self) -> bool:
        """Check if we have diverse agent types in training data"""
        try:
            recent_interactions = self.interaction_logger.get_recent_interactions(limit=200)
            agent_types = set()

            for interaction in recent_interactions:
                if not interaction.get('used_for_training', True):  # Only unused
                    agent_type = interaction.get('agent_type')
                    if agent_type:
                        agent_types.add(agent_type)

            # Need at least 2 different agent types for diversity
            return len(agent_types) >= 2

        except Exception:
            return False

    def get_trigger_status(self) -> Dict:
        """Get detailed status of all trigger conditions"""
        try:
            summary = self.model_tracker.get_training_data_summary()
            should_train, reason = self.should_trigger_training()

            last_training = self._get_last_training_time()
            hours_since_training = None
            if last_training:
                hours_since_training = (datetime.now() - last_training).total_seconds() / 3600

            return {
                "should_train": should_train,
                "reason": reason,
                "current_stats": {
                    "unused_interactions": summary.get('unused_interactions', 0),
                    "total_interactions": summary.get('total_interactions', 0),
                    "latest_model_version": summary.get('latest_model_version', 0),
                    "training_ready": summary.get('training_ready', False)
                },
                "trigger_conditions": {
                    "min_interactions_threshold": self.min_interactions,
                    "max_training_gap_hours": self.max_training_gap_hours,
                    "sentiment_threshold": self.sentiment_threshold,
                    "hours_since_last_training": hours_since_training,
                    "average_sentiment": self._calculate_average_sentiment(),
                    "agent_diversity_ok": self._check_agent_diversity()
                }
            }

        except Exception as e:
            return {"error": str(e)}

    def force_training_trigger(self, reason: str = "Manual trigger") -> bool:
        """Manually force a training trigger (for testing/admin)"""
        try:
            # Update system state to indicate pending training
            success = self.model_tracker.trigger_training_check()
            if success:
                logger.info(f"Manual training trigger activated: {reason}")
            return success
        except Exception as e:
            logger.error(f"Error forcing training trigger: {e}")
            return False

# Global trigger instance
_training_trigger = None

def get_training_trigger(**kwargs) -> TrainingTrigger:
    """Get the global training trigger instance"""
    global _training_trigger
    if _training_trigger is None:
        _training_trigger = TrainingTrigger(**kwargs)
    return _training_trigger

def should_trigger_training(**kwargs) -> Tuple[bool, str]:
    """Convenience function to check if training should be triggered"""
    trigger = get_training_trigger(**kwargs)
    return trigger.should_trigger_training()

def get_trigger_status(**kwargs) -> Dict:
    """Convenience function to get trigger status"""
    trigger = get_training_trigger(**kwargs)
    return trigger.get_trigger_status()

def force_training_trigger(reason: str = "Manual trigger", **kwargs) -> bool:
    """Convenience function to force training trigger"""
    trigger = get_training_trigger(**kwargs)
    return trigger.force_training_trigger(reason)