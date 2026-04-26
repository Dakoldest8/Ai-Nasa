"""
Phase 2: Database Connection Manager
Handles MySQL connections for the AI system brain
"""

import mysql.connector
from mysql.connector import Error
import os
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages MySQL connections and operations for the AI system"""

    def __init__(self, host="localhost", user="root", password="Password", database="nasa_ai_system", port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )

            if self.connection.is_connected():
                logger.info("Successfully connected to MySQL database")
                return True

        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False

        return False

    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed")

    def execute_query(self, query: str, params: tuple = None, fetch: bool = False) -> Optional[List[Dict]]:
        """Execute a SQL query"""
        if not self.connection or not self.connection.is_connected():
            logger.error("No active database connection")
            return None

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())

            if fetch:
                result = cursor.fetchall()
            else:
                self.connection.commit()
                result = None

            cursor.close()
            return result

        except Error as e:
            logger.error(f"Error executing query: {e}")
            return None

    def get_system_state(self) -> Optional[Dict]:
        """Get current system state"""
        query = "SELECT * FROM system_state WHERE id = 1"
        result = self.execute_query(query, fetch=True)
        return result[0] if result else None

    def update_system_state(self, updates: Dict[str, Any]) -> bool:
        """Update system state"""
        if not updates:
            return False

        set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
        values = tuple(updates.values())

        query = f"UPDATE system_state SET {set_clause}, last_update = CURRENT_TIMESTAMP WHERE id = 1"
        result = self.execute_query(query, values)
        return result is not None

    def log_interaction(self, source: str, user_id: int = None, input_text: str = "",
                       response: str = "", sentiment_score: float = None,
                       agent_type: str = None) -> bool:
        """Log an AI interaction"""
        query = """
        INSERT INTO interactions (source, user_id, input, response, sentiment_score, agent_type)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (source, user_id, input_text, response, sentiment_score, agent_type)
        result = self.execute_query(query, params)
        return result is not None

    def get_recent_interactions(self, limit: int = 100) -> List[Dict]:
        """Get recent interactions for training"""
        query = """
        SELECT * FROM interactions
        WHERE used_for_training = FALSE
        ORDER BY timestamp DESC
        LIMIT %s
        """
        result = self.execute_query(query, (limit,), fetch=True)
        return result or []

    def mark_interactions_used(self, interaction_ids: List[int]) -> bool:
        """Mark interactions as used for training"""
        if not interaction_ids:
            return False

        placeholders = ", ".join(["%s"] * len(interaction_ids))
        query = f"UPDATE interactions SET used_for_training = TRUE WHERE id IN ({placeholders})"
        result = self.execute_query(query, tuple(interaction_ids))
        return result is not None

    def save_model_record(self, version: int, file_name: str, notes: str = "",
                         training_interactions: int = 0, base_model: str = "") -> bool:
        """Save a new model record"""
        query = """
        INSERT INTO models (version, file_name, notes, training_interactions, base_model, status)
        VALUES (%s, %s, %s, %s, %s, 'completed')
        """
        params = (version, file_name, notes, training_interactions, base_model)
        result = self.execute_query(query, params)

        if result is not None:
            # Update system state
            self.update_system_state({
                'last_model_version': version,
                'total_interactions': self.get_total_interactions()
            })
            return True

        return False

    def get_latest_model(self) -> Optional[Dict]:
        """Get the latest trained model"""
        query = "SELECT * FROM models ORDER BY version DESC LIMIT 1"
        result = self.execute_query(query, fetch=True)
        return result[0] if result else None

    def get_total_interactions(self) -> int:
        """Get total number of interactions"""
        query = "SELECT COUNT(*) as total FROM interactions"
        result = self.execute_query(query, fetch=True)
        return result[0]['total'] if result else 0

    def get_unused_interactions_count(self) -> int:
        """Get count of interactions not yet used for training"""
        query = "SELECT COUNT(*) as count FROM interactions WHERE used_for_training = FALSE"
        result = self.execute_query(query, fetch=True)
        return result[0]['count'] if result else 0

    def get_models_list(self) -> List[Dict]:
        """Get all models ordered by version"""
        query = "SELECT * FROM models ORDER BY version DESC"
        result = self.execute_query(query, fetch=True)
        return result or []

    # Robot logging methods (Phase 6)
    def log_robot_interaction(self, robot_id: str, interaction_type: str,
                            user_input: str = None, robot_response: str = None,
                            sentiment_score: float = None, confidence_score: float = None,
                            model_version: int = None, processing_time_ms: int = None,
                            success: bool = True, error_message: str = None,
                            metadata: str = None) -> bool:
        """Log a robot interaction"""
        query = """
        INSERT INTO robot_interactions
        (robot_id, interaction_type, user_input, robot_response, sentiment_score,
         confidence_score, model_version, processing_time_ms, success, error_message, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (robot_id, interaction_type, user_input, robot_response, sentiment_score,
                 confidence_score, model_version, processing_time_ms, success, error_message, metadata)
        result = self.execute_query(query, params)
        return result is not None

    def log_robot_feedback(self, robot_id: str, feedback_type: str,
                          original_interaction_id: str = None, feedback_data: str = None,
                          improvement_suggestion: str = None, user_rating: int = None,
                          metadata: str = None) -> bool:
        """Log robot feedback"""
        query = """
        INSERT INTO robot_feedback
        (robot_id, feedback_type, original_interaction_id, feedback_data,
         improvement_suggestion, user_rating, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (robot_id, feedback_type, original_interaction_id, feedback_data,
                 improvement_suggestion, user_rating, metadata)
        result = self.execute_query(query, params)
        return result is not None

    def get_robot_statistics(self) -> Dict:
        """Get robot statistics"""
        stats = {}

        # Count robots
        query = "SELECT COUNT(DISTINCT robot_id) as robot_count FROM robot_interactions"
        result = self.execute_query(query, fetch=True)
        stats['robot_count'] = result[0]['robot_count'] if result else 0

        # Total interactions
        query = "SELECT COUNT(*) as total FROM robot_interactions"
        result = self.execute_query(query, fetch=True)
        stats['total_interactions'] = result[0]['total'] if result else 0

        # Total feedback
        query = "SELECT COUNT(*) as total FROM robot_feedback"
        result = self.execute_query(query, fetch=True)
        stats['total_feedback'] = result[0]['total'] if result else 0

        return stats

    def get_robot_list(self) -> List[Dict]:
        """Get list of all robots with activity summary"""
        query = """
        SELECT
            ri.robot_id,
            COUNT(ri.id) as interaction_count,
            COUNT(rf.id) as feedback_count,
            MAX(ri.timestamp) as last_interaction,
            AVG(ri.sentiment_score) as avg_sentiment,
            AVG(ri.confidence_score) as avg_confidence
        FROM robot_interactions ri
        LEFT JOIN robot_feedback rf ON ri.robot_id = rf.robot_id
        GROUP BY ri.robot_id
        ORDER BY last_interaction DESC
        """
        result = self.execute_query(query, fetch=True)
        return result or []

    def get_robot_interactions(self, robot_id: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get interactions for a specific robot"""
        query = """
        SELECT * FROM robot_interactions
        WHERE robot_id = %s
        ORDER BY timestamp DESC
        LIMIT %s OFFSET %s
        """
        result = self.execute_query(query, (robot_id, limit, offset), fetch=True)
        return result or []

    def get_robot_analytics(self) -> Dict:
        """Get comprehensive robot analytics"""
        analytics = {
            'interaction_types': {},
            'feedback_types': {},
            'performance_metrics': {},
            'temporal_stats': {}
        }

        # Interaction types breakdown
        query = """
        SELECT interaction_type, COUNT(*) as count
        FROM robot_interactions
        GROUP BY interaction_type
        """
        result = self.execute_query(query, fetch=True)
        analytics['interaction_types'] = {row['interaction_type']: row['count'] for row in (result or [])}

        # Feedback types breakdown
        query = """
        SELECT feedback_type, COUNT(*) as count
        FROM robot_feedback
        GROUP BY feedback_type
        """
        result = self.execute_query(query, fetch=True)
        analytics['feedback_types'] = {row['feedback_type']: row['count'] for row in (result or [])}

        # Performance metrics
        query = """
        SELECT
            AVG(sentiment_score) as avg_sentiment,
            AVG(confidence_score) as avg_confidence,
            AVG(processing_time_ms) as avg_processing_time,
            SUM(CASE WHEN success = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100 as success_rate
        FROM robot_interactions
        """
        result = self.execute_query(query, fetch=True)
        if result:
            analytics['performance_metrics'] = result[0]

        # Temporal stats (last 24 hours)
        query = """
        SELECT COUNT(*) as recent_interactions
        FROM robot_interactions
        WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        """
        result = self.execute_query(query, fetch=True)
        analytics['temporal_stats']['last_24h_interactions'] = result[0]['recent_interactions'] if result else 0

        return analytics

    # Reading activity logging methods
    def log_reading_activity(self, user_id: int, book_title: str, duration_minutes: int,
                           start_time: str = None, end_time: str = None, progress_percent: float = None,
                           mood_tag: str = None) -> bool:
        """Log a reading activity"""
        query = """
        INSERT INTO reading_activities
        (user_id, book_title, duration_minutes, start_time, end_time, progress_percent, mood_tag)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (user_id, book_title, duration_minutes, start_time, end_time, progress_percent, mood_tag)
        result = self.execute_query(query, params)
        return result is not None

    def get_reading_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get reading history for a user"""
        query = """
        SELECT * FROM reading_activities
        WHERE user_id = %s
        ORDER BY start_time DESC
        LIMIT %s
        """
        result = self.execute_query(query, (user_id, limit), fetch=True)
        return result or []

    def get_reading_stats(self, user_id: int) -> Dict:
        """Get reading statistics for a user"""
        stats = {}

        # Total reading time
        query = "SELECT SUM(duration_minutes) as total_minutes FROM reading_activities WHERE user_id = %s"
        result = self.execute_query(query, (user_id,), fetch=True)
        stats['total_reading_minutes'] = result[0]['total_minutes'] if result and result[0]['total_minutes'] else 0

        # Favorite books (by time spent)
        query = """
        SELECT book_title, SUM(duration_minutes) as total_time
        FROM reading_activities
        WHERE user_id = %s
        GROUP BY book_title
        ORDER BY total_time DESC
        LIMIT 5
        """
        result = self.execute_query(query, (user_id,), fetch=True)
        stats['favorite_books'] = result or []

        # Reading patterns by time of day
        query = """
        SELECT HOUR(start_time) as hour, SUM(duration_minutes) as total_time
        FROM reading_activities
        WHERE user_id = %s AND start_time IS NOT NULL
        GROUP BY HOUR(start_time)
        ORDER BY total_time DESC
        """
        result = self.execute_query(query, (user_id,), fetch=True)
        stats['reading_by_hour'] = result or []

        return stats

# Global database manager instance
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    global _db_manager
    if _db_manager is None:
        # Try to get from environment variables
        host = os.getenv('DB_HOST', 'localhost')
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        database = os.getenv('DB_NAME', 'nasa_ai_system')
        port = int(os.getenv('DB_PORT', '3306'))

        _db_manager = DatabaseManager(host, user, password, database, port)

    return _db_manager

def init_database_connection() -> bool:
    """Initialize database connection"""
    manager = get_db_manager()
    return manager.connect()

def close_database_connection():
    """Close database connection"""
    manager = get_db_manager()
    manager.disconnect()