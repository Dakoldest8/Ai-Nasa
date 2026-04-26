"""
Phase 2: Interaction Logger
Logs all AI interactions to MySQL database for training data
"""

import logging
from typing import Optional
from .connection import get_db_manager

logger = logging.getLogger(__name__)

class InteractionLogger:
    """Logs AI interactions to database"""

    def __init__(self):
        self.db = get_db_manager()

    def log_web_interaction(self, user_id: int, input_text: str, response: str,
                           agent_type: str = None, sentiment_score: float = None) -> bool:
        """Log a web assistant interaction"""
        try:
            success = self.db.log_interaction(
                source="web_assistant",
                user_id=user_id,
                input_text=input_text,
                response=response,
                sentiment_score=sentiment_score,
                agent_type=agent_type
            )

            if success:
                logger.info(f"Logged web interaction for user {user_id}")
            else:
                logger.error("Failed to log web interaction")

            return success

        except Exception as e:
            logger.error(f"Error logging web interaction: {e}")
            return False

    def log_pi_interaction(self, input_text: str, response: str,
                          agent_type: str = "robot_general") -> bool:
        """Log a Pi robot interaction"""
        try:
            success = self.db.log_interaction(
                source="pi_robot",
                user_id=None,  # Pi doesn't have user auth
                input_text=input_text,
                response=response,
                agent_type=agent_type
            )

            if success:
                logger.info("Logged Pi robot interaction")
            else:
                logger.error("Failed to log Pi interaction")

            return success

        except Exception as e:
            logger.error(f"Error logging Pi interaction: {e}")
            return False

    def get_recent_interactions(self, limit: int = 100) -> list:
        """Get recent interactions for training"""
        try:
            return self.db.get_recent_interactions(limit)
        except Exception as e:
            logger.error(f"Error getting recent interactions: {e}")
            return []

    def mark_as_used_for_training(self, interaction_ids: list) -> bool:
        """Mark interactions as used for training"""
        try:
            return self.db.mark_interactions_used(interaction_ids)
        except Exception as e:
            logger.error(f"Error marking interactions as used: {e}")
            return False

    def get_stats(self) -> dict:
        """Get interaction statistics"""
        try:
            total = self.db.get_total_interactions()
            unused = self.db.get_unused_interactions_count()

            return {
                "total_interactions": total,
                "unused_for_training": unused,
                "used_for_training": total - unused
            }
        except Exception as e:
            logger.error(f"Error getting interaction stats: {e}")
            return {"error": str(e)}

    def log_reading_activity(self, user_id: int, book_title: str, duration_minutes: int,
                           start_time: str = None, end_time: str = None, progress_percent: float = None,
                           mood_tag: str = None) -> bool:
        """Log a reading activity"""
        try:
            success = self.db.log_reading_activity(
                user_id=user_id,
                book_title=book_title,
                duration_minutes=duration_minutes,
                start_time=start_time,
                end_time=end_time,
                progress_percent=progress_percent,
                mood_tag=mood_tag
            )

            if success:
                logger.info(f"Logged reading activity for user {user_id}: {book_title}")
            else:
                logger.error("Failed to log reading activity")

            return success

        except Exception as e:
            logger.error(f"Error logging reading activity: {e}")
            return False

    def get_reading_history(self, user_id: int, limit: int = 50) -> list:
        """Get reading history for a user"""
        try:
            return self.db.get_reading_history(user_id, limit)
        except Exception as e:
            logger.error(f"Error getting reading history: {e}")
            return []

    def get_reading_stats(self, user_id: int) -> dict:
        """Get reading statistics for a user"""
        try:
            return self.db.get_reading_stats(user_id)
        except Exception as e:
            logger.error(f"Error getting reading stats: {e}")
            return {}

# Global logger instance
_interaction_logger = None

def get_interaction_logger() -> InteractionLogger:
    """Get the global interaction logger instance"""
    global _interaction_logger
    if _interaction_logger is None:
        _interaction_logger = InteractionLogger()
    return _interaction_logger

def log_web_interaction(user_id: int, input_text: str, response: str,
                       agent_type: str = None, sentiment_score: float = None) -> bool:
    """Convenience function to log web interactions"""
    logger = get_interaction_logger()
    return logger.log_web_interaction(user_id, input_text, response, agent_type, sentiment_score)

def log_pi_interaction(input_text: str, response: str, agent_type: str = "robot_general") -> bool:
    """Convenience function to log Pi interactions"""
    logger = get_interaction_logger()
    return logger.log_pi_interaction(input_text, response, agent_type)

def log_reading_activity(user_id: int, book_title: str, duration_minutes: int,
                        start_time: str = None, end_time: str = None, progress_percent: float = None,
                        mood_tag: str = None) -> bool:
    """Convenience function to log reading activities"""
    logger = get_interaction_logger()
    return logger.log_reading_activity(user_id, book_title, duration_minutes, start_time, end_time, progress_percent, mood_tag)
_interaction_logger = None

def get_interaction_logger() -> InteractionLogger:
    """Get the global interaction logger instance"""
    global _interaction_logger
    if _interaction_logger is None:
        _interaction_logger = InteractionLogger()
    return _interaction_logger

def log_web_interaction(user_id: int, input_text: str, response: str,
                       agent_type: str = None, sentiment_score: float = None) -> bool:
    """Convenience function to log web interactions"""
    logger = get_interaction_logger()
    return logger.log_web_interaction(user_id, input_text, response, agent_type, sentiment_score)

def log_pi_interaction(input_text: str, response: str, agent_type: str = "robot_general") -> bool:
    """Convenience function to log Pi interactions"""
    logger = get_interaction_logger()
    return logger.log_pi_interaction(input_text, response, agent_type)