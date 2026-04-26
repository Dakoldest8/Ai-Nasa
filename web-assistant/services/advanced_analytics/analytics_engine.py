"""
Phase 8: Advanced Analytics
Comprehensive analytics and insights for AI system performance
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, Counter
import statistics
import numpy as np

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """Advanced analytics engine for AI system insights"""

    def __init__(self):
        self.metrics_cache = {}
        self.insights_cache = {}
        self.cache_timeout = 300  # 5 minutes

    def analyze_system_performance(self, db_manager) -> Dict:
        """Analyze overall system performance"""
        try:
            # Get interaction data
            interactions = db_manager.get_recent_interactions(1000)

            if not interactions:
                return {"error": "No interaction data available"}

            # Calculate key metrics
            metrics = {
                "total_interactions": len(interactions),
                "avg_response_time": self._calculate_avg_response_time(interactions),
                "sentiment_distribution": self._analyze_sentiment_distribution(interactions),
                "peak_usage_hours": self._find_peak_usage_hours(interactions),
                "user_engagement": self._calculate_user_engagement(interactions),
                "model_performance": self._analyze_model_performance(interactions),
                "error_rate": self._calculate_error_rate(interactions)
            }

            return metrics

        except Exception as e:
            logger.error(f"System performance analysis failed: {e}")
            return {"error": str(e)}

    def analyze_robot_performance(self, db_manager) -> Dict:
        """Analyze robot-specific performance metrics"""
        try:
            # Get robot statistics
            robot_stats = db_manager.get_robot_statistics()

            if not robot_stats or robot_stats.get('robot_count', 0) == 0:
                return {"error": "No robot data available"}

            # Get robot interactions
            robot_interactions = []
            for robot in db_manager.get_robot_list():
                interactions = db_manager.get_robot_interactions(robot['robot_id'], limit=100)
                robot_interactions.extend(interactions)

            # Calculate robot-specific metrics
            metrics = {
                "robot_count": robot_stats['robot_count'],
                "total_robot_interactions": robot_stats['total_interactions'],
                "avg_sentiment": self._calculate_avg_sentiment(robot_interactions),
                "interaction_types": self._analyze_interaction_types(robot_interactions),
                "robot_health": self._analyze_robot_health(robot_interactions),
                "performance_trends": self._analyze_performance_trends(robot_interactions),
                "user_satisfaction": self._calculate_user_satisfaction(robot_interactions)
            }

            return metrics

        except Exception as e:
            logger.error(f"Robot performance analysis failed: {e}")
            return {"error": str(e)}

    def generate_insights(self, db_manager) -> List[Dict]:
        """Generate actionable insights from data"""
        insights = []

        try:
            # System performance insights
            system_perf = self.analyze_system_performance(db_manager)
            if "error" not in system_perf:
                insights.extend(self._generate_system_insights(system_perf))

            # Robot performance insights
            robot_perf = self.analyze_robot_performance(db_manager)
            if "error" not in robot_perf:
                insights.extend(self._generate_robot_insights(robot_perf))

            # Training insights
            training_insights = self._generate_training_insights(db_manager)
            insights.extend(training_insights)

            # Sort by priority
            insights.sort(key=lambda x: x.get('priority', 0), reverse=True)

        except Exception as e:
            logger.error(f"Insights generation failed: {e}")

        return insights

    def _calculate_avg_response_time(self, interactions: List[Dict]) -> float:
        """Calculate average response time"""
        response_times = [i.get('processing_time_ms', 0) for i in interactions if i.get('processing_time_ms')]
        return statistics.mean(response_times) if response_times else 0

    def _analyze_sentiment_distribution(self, interactions: List[Dict]) -> Dict:
        """Analyze sentiment distribution"""
        sentiments = [i.get('sentiment_score') for i in interactions if i.get('sentiment_score') is not None]

        if not sentiments:
            return {"neutral": 1.0}

        # Categorize sentiments
        positive = sum(1 for s in sentiments if s > 0.2)
        negative = sum(1 for s in sentiments if s < -0.2)
        neutral = len(sentiments) - positive - negative

        total = len(sentiments)
        return {
            "positive": positive / total,
            "negative": negative / total,
            "neutral": neutral / total
        }

    def _find_peak_usage_hours(self, interactions: List[Dict]) -> List[int]:
        """Find peak usage hours"""
        hour_counts = defaultdict(int)

        for interaction in interactions:
            if 'timestamp' in interaction:
                try:
                    dt = datetime.fromisoformat(interaction['timestamp'].replace('Z', '+00:00'))
                    hour_counts[dt.hour] += 1
                except:
                    pass

        # Return top 3 peak hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        return [hour for hour, count in sorted_hours[:3]]

    def _calculate_user_engagement(self, interactions: List[Dict]) -> Dict:
        """Calculate user engagement metrics"""
        if not interactions:
            return {"engagement_score": 0}

        # Group by user
        user_interactions = defaultdict(list)
        for i in interactions:
            user_id = i.get('user_id', 'anonymous')
            user_interactions[user_id].append(i)

        # Calculate engagement metrics
        total_users = len(user_interactions)
        active_users = sum(1 for interactions in user_interactions.values() if len(interactions) > 1)
        avg_interactions_per_user = len(interactions) / total_users if total_users > 0 else 0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "avg_interactions_per_user": avg_interactions_per_user,
            "engagement_rate": active_users / total_users if total_users > 0 else 0
        }

    def _analyze_model_performance(self, interactions: List[Dict]) -> Dict:
        """Analyze model performance over time"""
        model_versions = defaultdict(list)

        for i in interactions:
            version = i.get('model_version', 0)
            sentiment = i.get('sentiment_score')
            confidence = i.get('confidence_score')

            if sentiment is not None:
                model_versions[version].append({
                    'sentiment': sentiment,
                    'confidence': confidence
                })

        # Calculate performance by version
        performance = {}
        for version, data in model_versions.items():
            sentiments = [d['sentiment'] for d in data]
            confidences = [d['confidence'] for d in data if d['confidence'] is not None]

            performance[version] = {
                "avg_sentiment": statistics.mean(sentiments) if sentiments else 0,
                "avg_confidence": statistics.mean(confidences) if confidences else 0,
                "interaction_count": len(data)
            }

        return performance

    def _calculate_error_rate(self, interactions: List[Dict]) -> float:
        """Calculate system error rate"""
        total = len(interactions)
        if total == 0:
            return 0

        errors = sum(1 for i in interactions if not i.get('success', True))
        return errors / total

    def _calculate_avg_sentiment(self, interactions: List[Dict]) -> float:
        """Calculate average sentiment"""
        sentiments = [i.get('sentiment_score', 0) for i in interactions if i.get('sentiment_score') is not None]
        return statistics.mean(sentiments) if sentiments else 0

    def _analyze_interaction_types(self, interactions: List[Dict]) -> Dict:
        """Analyze interaction types distribution"""
        types = Counter(i.get('interaction_type', 'unknown') for i in interactions)
        total = len(interactions)

        return {interaction_type: count / total for interaction_type, count in types.items()}

    def _analyze_robot_health(self, interactions: List[Dict]) -> Dict:
        """Analyze robot health based on interactions"""
        success_rate = sum(1 for i in interactions if i.get('success', True)) / len(interactions) if interactions else 0

        # Analyze error patterns
        errors = [i for i in interactions if not i.get('success', True)]
        error_types = Counter(i.get('error_message', 'unknown') for i in errors)

        return {
            "success_rate": success_rate,
            "error_rate": 1 - success_rate,
            "common_errors": dict(error_types.most_common(3))
        }

    def _analyze_performance_trends(self, interactions: List[Dict]) -> Dict:
        """Analyze performance trends over time"""
        if len(interactions) < 10:
            return {"trend": "insufficient_data"}

        # Sort by timestamp
        sorted_interactions = sorted(interactions, key=lambda x: x.get('timestamp', ''))

        # Split into halves for trend analysis
        midpoint = len(sorted_interactions) // 2
        first_half = sorted_interactions[:midpoint]
        second_half = sorted_interactions[midpoint:]

        first_avg_sentiment = self._calculate_avg_sentiment(first_half)
        second_avg_sentiment = self._calculate_avg_sentiment(second_half)

        trend = "stable"
        if second_avg_sentiment > first_avg_sentiment + 0.1:
            trend = "improving"
        elif second_avg_sentiment < first_avg_sentiment - 0.1:
            trend = "declining"

        return {
            "trend": trend,
            "first_half_avg": first_avg_sentiment,
            "second_half_avg": second_avg_sentiment,
            "change": second_avg_sentiment - first_avg_sentiment
        }

    def _calculate_user_satisfaction(self, interactions: List[Dict]) -> float:
        """Calculate user satisfaction score"""
        # Use sentiment as proxy for satisfaction
        sentiments = [i.get('sentiment_score', 0) for i in interactions if i.get('sentiment_score') is not None]

        if not sentiments:
            return 0.5  # Neutral default

        # Convert to 0-1 scale (sentiment is -1 to 1, convert to 0-1)
        satisfaction_scores = [(s + 1) / 2 for s in sentiments]
        return statistics.mean(satisfaction_scores)

    def _generate_system_insights(self, metrics: Dict) -> List[Dict]:
        """Generate insights from system metrics"""
        insights = []

        # Response time insight
        if metrics.get('avg_response_time', 0) > 2000:  # Over 2 seconds
            insights.append({
                "type": "performance",
                "title": "Slow Response Times Detected",
                "description": f"Average response time of {metrics['avg_response_time']:.0f}ms exceeds recommended threshold",
                "priority": 8,
                "recommendation": "Consider optimizing model inference or implementing response caching"
            })

        # Sentiment insight
        sentiment_dist = metrics.get('sentiment_distribution', {})
        if sentiment_dist.get('negative', 0) > 0.3:  # Over 30% negative
            insights.append({
                "type": "sentiment",
                "title": "High Negative Sentiment",
                "description": f"{sentiment_dist['negative']:.1%} of interactions show negative sentiment",
                "priority": 9,
                "recommendation": "Review recent model training data and consider additional fine-tuning"
            })

        # Peak usage insight
        peak_hours = metrics.get('peak_usage_hours', [])
        if peak_hours:
            insights.append({
                "type": "usage",
                "title": "Peak Usage Hours Identified",
                "description": f"System is most active during hours: {', '.join(map(str, peak_hours))}",
                "priority": 5,
                "recommendation": "Consider scheduling maintenance during off-peak hours"
            })

        return insights

    def _generate_robot_insights(self, metrics: Dict) -> List[Dict]:
        """Generate insights from robot metrics"""
        insights = []

        # Robot health insight
        health = metrics.get('robot_health', {})
        if health.get('error_rate', 0) > 0.1:  # Over 10% errors
            insights.append({
                "type": "robot_health",
                "title": "High Robot Error Rate",
                "description": f"Robot error rate of {health['error_rate']:.1%} indicates potential issues",
                "priority": 9,
                "recommendation": "Check robot hardware, network connectivity, and model versions"
            })

        # Performance trend insight
        trends = metrics.get('performance_trends', {})
        if trends.get('trend') == 'declining':
            insights.append({
                "type": "performance_trend",
                "title": "Declining Robot Performance",
                "description": f"Robot performance has declined by {trends.get('change', 0):.2f} sentiment points",
                "priority": 8,
                "recommendation": "Consider updating robot models or investigating environmental factors"
            })

        return insights

    def _generate_training_insights(self, db_manager) -> List[Dict]:
        """Generate insights about training effectiveness"""
        insights = []

        try:
            # Check recent training history
            models = db_manager.get_models_list()
            if len(models) >= 2:
                latest = models[0]
                previous = models[1]

                # Compare performance
                if latest.get('notes') and 'accuracy' in latest['notes'].lower():
                    insights.append({
                        "type": "training",
                        "title": "Model Training Completed",
                        "description": f"Latest model v{latest['version']} trained with {latest.get('training_interactions', 0)} interactions",
                        "priority": 6,
                        "recommendation": "Monitor performance metrics over next few days"
                    })

        except Exception as e:
            logger.error(f"Training insights generation failed: {e}")

        return insights

# Global analytics engine
analytics_engine = AnalyticsEngine()

def get_analytics_engine() -> AnalyticsEngine:
    """Get the global analytics engine instance"""
    return analytics_engine