"""Context-aware recommendation engine for the Astronaut AI Ecosystem."""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from ..database.interaction_logger import get_interaction_logger
    DB_ENABLED = True
except ImportError:
    get_interaction_logger = None
    DB_ENABLED = False

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """Generates lightweight, privacy-safe recommendations for the web assistant."""

    def __init__(self):
        self.interaction_logger = get_interaction_logger() if get_interaction_logger else None

    def analyze(self, message: str, user_id: str, memory: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze the current query and return recommended actions."""
        suggestions: List[str] = []
        analysis_reason = "Based on the current request and recent session context."
        lower_message = (message or "").lower()
        memory = memory or {}

        keywords = [
            (['schedule', 'meeting', 'agenda', 'timeline'],
             'Review your mission timeline and confirm the next scheduled task.'),
            (['battery', 'power', 'charge', 'energy'],
             'Check your current power reserves and battery status.'),
            (['drill', 'procedure', 'step', 'next step', 'task'],
             'Confirm the next mission step before proceeding.'),
            (['help', 'support', 'assist', 'how do i'],
             'Ask for a quick system summary or mission help guide.'),
            (['stressed', 'anxious', 'worried', 'tired', 'sleepy'],
             'Take a short break and review safety protocols.'),
            (['status', 'update', 'health', 'condition'],
             'Request a status check for the current mission systems.'),
        ]

        for triggers, action in keywords:
            if any(trigger in lower_message for trigger in triggers):
                suggestions.append(action)

        recent_messages = memory.get('recent_messages', [])
        if len(recent_messages) >= 3:
            joined_recent = ' '.join(recent_messages).lower()
            if 'power' in joined_recent and 'battery' not in lower_message:
                suggestions.append('You have asked about power recently. Consider verifying your power budget again.')
            if 'status' in joined_recent and 'summary' not in lower_message:
                suggestions.append('Summarize the last few updates to keep the mission plan concise.')

        if DB_ENABLED and self.interaction_logger:
            try:
                recent_interactions = self.interaction_logger.get_recent_interactions(limit=20)
                combined = ' '.join(
                    f"{item.get('input', '')} {item.get('response', '')}" for item in recent_interactions
                ).lower()
                if 'battery' in combined and 'battery' not in lower_message:
                    suggestions.append('A recent trend shows battery questions. Run a fast power check.')
                if 'communication' in combined and 'communication' not in lower_message:
                    suggestions.append('Communication checks are trending. Confirm your comms link quality.')

                # Reading-based suggestions
                reading_stats = self.interaction_logger.get_reading_stats(int(user_id))
                if reading_stats.get('total_reading_minutes', 0) > 0:
                    favorite_books = reading_stats.get('favorite_books', [])
                    if favorite_books:
                        top_book = favorite_books[0]['book_title']
                        suggestions.append(f"You often read '{top_book}' for relaxation. Would you like to continue?")

                    reading_by_hour = reading_stats.get('reading_by_hour', [])
                    if reading_by_hour:
                        best_hour = reading_by_hour[0]['hour']
                        current_hour = datetime.now().hour
                        if abs(current_hour - best_hour) <= 2:
                            suggestions.append("This is a time you usually enjoy reading. Consider opening a book.")

            except Exception as e:
                logger.debug(f"Recommendation DB analysis skipped: {e}")

        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in unique_suggestions:
                unique_suggestions.append(suggestion)

        result: Dict[str, Any] = {
            'enabled': True,
            'recommended_actions': unique_suggestions,
            'analysis_reason': analysis_reason
        }

        return result
