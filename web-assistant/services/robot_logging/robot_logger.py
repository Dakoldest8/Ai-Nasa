"""
Phase 6: Robot Logging System
Handles logging of robot interactions and feedback for continuous learning
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading
import time
from queue import Queue

logger = logging.getLogger(__name__)

@dataclass
class RobotInteraction:
    """Represents a robot interaction log entry"""
    timestamp: str
    robot_id: str
    interaction_type: str  # 'voice_command', 'sensor_input', 'system_event', etc.
    user_input: Optional[str] = None
    robot_response: Optional[str] = None
    sentiment_score: Optional[float] = None
    confidence_score: Optional[float] = None
    model_version: Optional[int] = None
    processing_time_ms: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class RobotFeedback:
    """Represents robot feedback for model improvement"""
    timestamp: str
    robot_id: str
    feedback_type: str  # 'user_correction', 'performance_rating', 'error_report'
    original_interaction_id: Optional[str] = None
    feedback_data: Optional[Dict[str, Any]] = None
    improvement_suggestion: Optional[str] = None
    user_rating: Optional[int] = None  # 1-5 scale
    metadata: Optional[Dict[str, Any]] = None

class RobotLogger:
    """Handles logging of robot interactions and feedback"""

    def __init__(self, robot_id: str, web_server_url: str = "http://localhost:8000",
                 batch_size: int = 10, flush_interval: int = 30):
        self.robot_id = robot_id
        self.web_server_url = web_server_url
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        self.interaction_queue = Queue()
        self.feedback_queue = Queue()

        self.last_flush = datetime.now()
        self.flush_thread = None
        self.running = False

    def start_logging(self):
        """Start the background logging thread"""
        self.running = True
        self.flush_thread = threading.Thread(target=self._background_flush, daemon=True)
        self.flush_thread.start()
        logger.info(f"Robot logging started for {self.robot_id}")

    def stop_logging(self):
        """Stop the background logging thread"""
        self.running = False
        if self.flush_thread:
            self.flush_thread.join(timeout=5)
        self._flush_queues()  # Final flush
        logger.info(f"Robot logging stopped for {self.robot_id}")

    def log_interaction(self, interaction: RobotInteraction):
        """Log a robot interaction"""
        if interaction.robot_id != self.robot_id:
            interaction.robot_id = self.robot_id

        self.interaction_queue.put(interaction)

        # Check if we should flush
        if self.interaction_queue.qsize() >= self.batch_size:
            self._flush_interactions()

    def log_feedback(self, feedback: RobotFeedback):
        """Log robot feedback"""
        if feedback.robot_id != self.robot_id:
            feedback.robot_id = self.robot_id

        self.feedback_queue.put(feedback)

        # Check if we should flush
        if self.feedback_queue.qsize() >= self.batch_size:
            self._flush_feedback()

    def _background_flush(self):
        """Background thread for periodic flushing"""
        while self.running:
            try:
                now = datetime.now()
                if (now - self.last_flush).total_seconds() >= self.flush_interval:
                    self._flush_queues()
                    self.last_flush = now

                time.sleep(5)  # Check every 5 seconds

            except Exception as e:
                logger.error(f"Background flush error: {e}")
                time.sleep(10)

    def _flush_queues(self):
        """Flush both interaction and feedback queues"""
        self._flush_interactions()
        self._flush_feedback()

    def _flush_interactions(self):
        """Flush interaction queue to web server"""
        interactions = []
        while not self.interaction_queue.empty() and len(interactions) < self.batch_size:
            try:
                interaction = self.interaction_queue.get_nowait()
                interactions.append(asdict(interaction))
            except:
                break

        if interactions:
            self._send_to_web_server("interactions", interactions)

    def _flush_feedback(self):
        """Flush feedback queue to web server"""
        feedbacks = []
        while not self.feedback_queue.empty() and len(feedbacks) < self.batch_size:
            try:
                feedback = self.feedback_queue.get_nowait()
                feedbacks.append(asdict(feedback))
            except:
                break

        if feedbacks:
            self._send_to_web_server("feedback", feedbacks)

    def _send_to_web_server(self, endpoint: str, data: List[Dict]):
        """Send data to web server"""
        try:
            url = f"{self.web_server_url}/robot/{endpoint}"
            response = requests.post(url, json=data, timeout=10)

            if response.status_code == 200:
                logger.debug(f"Successfully sent {len(data)} {endpoint} to web server")
            else:
                logger.warning(f"Failed to send {endpoint}: HTTP {response.status_code}")
                # Re-queue failed items
                self._requeue_failed_data(endpoint, data)

        except Exception as e:
            logger.error(f"Failed to send {endpoint} to web server: {e}")
            # Re-queue failed items
            self._requeue_failed_data(endpoint, data)

    def _requeue_failed_data(self, endpoint: str, data: List[Dict]):
        """Re-queue failed data for retry"""
        try:
            if endpoint == "interactions":
                for item in data:
                    interaction = RobotInteraction(**item)
                    self.interaction_queue.put(interaction)
            elif endpoint == "feedback":
                for item in data:
                    feedback = RobotFeedback(**item)
                    self.feedback_queue.put(feedback)
        except Exception as e:
            logger.error(f"Failed to re-queue {endpoint}: {e}")

    def get_queue_status(self) -> Dict:
        """Get current queue status"""
        return {
            "robot_id": self.robot_id,
            "interactions_queued": self.interaction_queue.qsize(),
            "feedback_queued": self.feedback_queue.qsize(),
            "last_flush": self.last_flush.isoformat() if self.last_flush else None,
            "logging_active": self.running
        }

class RobotLoggingAPI:
    """API for quick robot logging without full logger setup"""

    def __init__(self, robot_id: str, web_server_url: str = "http://localhost:8000"):
        self.robot_id = robot_id
        self.web_server_url = web_server_url

    def log_interaction(self, interaction_type: str, **kwargs) -> bool:
        """Quick log an interaction"""
        try:
            interaction = RobotInteraction(
                timestamp=datetime.now().isoformat(),
                robot_id=self.robot_id,
                interaction_type=interaction_type,
                **kwargs
            )

            data = [asdict(interaction)]
            url = f"{self.web_server_url}/robot/interactions"
            response = requests.post(url, json=data, timeout=5)

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Quick log failed: {e}")
            return False

    def log_feedback(self, feedback_type: str, **kwargs) -> bool:
        """Quick log feedback"""
        try:
            feedback = RobotFeedback(
                timestamp=datetime.now().isoformat(),
                robot_id=self.robot_id,
                feedback_type=feedback_type,
                **kwargs
            )

            data = [asdict(feedback)]
            url = f"{self.web_server_url}/robot/feedback"
            response = requests.post(url, json=data, timeout=5)

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Quick feedback log failed: {e}")
            return False

# Global instances
robot_loggers = {}

def get_robot_logger(robot_id: str, web_server_url: str = "http://localhost:8000") -> RobotLogger:
    """Get or create a robot logger instance"""
    if robot_id not in robot_loggers:
        robot_loggers[robot_id] = RobotLogger(robot_id, web_server_url)
    return robot_loggers[robot_id]

def get_robot_logging_api(robot_id: str, web_server_url: str = "http://localhost:8000") -> RobotLoggingAPI:
    """Get a robot logging API instance"""
    return RobotLoggingAPI(robot_id, web_server_url)