"""
Phase 8: Advanced Analytics API
REST endpoints for comprehensive AI system analytics and insights
"""

from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Import analytics components
try:
    from services.advanced_analytics.analytics_engine import get_analytics_engine
    from services.database.connection import get_db_manager
except ImportError:
    logger.warning("Analytics modules not available")
    get_analytics_engine = None
    get_db_manager = None

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/system/performance', methods=['GET'])
def get_system_performance():
    """Get comprehensive system performance analytics"""
    if not get_analytics_engine or not get_db_manager:
        return jsonify({"error": "Analytics not available"}), 503

    try:
        engine = get_analytics_engine()
        db = get_db_manager()

        if not db.connect():
            return jsonify({"error": "Database connection failed"}), 503

        metrics = engine.analyze_system_performance(db)
        db.disconnect()

        if "error" in metrics:
            return jsonify({"error": metrics["error"]}), 500

        return jsonify({
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"System performance analytics failed: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/robot/performance', methods=['GET'])
def get_robot_performance():
    """Get robot-specific performance analytics"""
    if not get_analytics_engine or not get_db_manager:
        return jsonify({"error": "Analytics not available"}), 503

    try:
        engine = get_analytics_engine()
        db = get_db_manager()

        if not db.connect():
            return jsonify({"error": "Database connection failed"}), 503

        metrics = engine.analyze_robot_performance(db)
        db.disconnect()

        if "error" in metrics:
            return jsonify({"error": metrics["error"]}), 500

        return jsonify({
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Robot performance analytics failed: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/insights', methods=['GET'])
def get_insights():
    """Get actionable insights from system data"""
    if not get_analytics_engine or not get_db_manager:
        return jsonify({"error": "Analytics not available"}), 503

    try:
        engine = get_analytics_engine()
        db = get_db_manager()

        if not db.connect():
            return jsonify({"error": "Database connection failed"}), 503

        insights = engine.generate_insights(db)
        db.disconnect()

        return jsonify({
            "status": "success",
            "insights": insights,
            "total_insights": len(insights),
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Insights generation failed: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get comprehensive dashboard data"""
    if not get_analytics_engine or not get_db_manager:
        return jsonify({"error": "Analytics not available"}), 503

    try:
        engine = get_analytics_engine()
        db = get_db_manager()

        if not db.connect():
            return jsonify({"error": "Database connection failed"}), 503

        # Get all analytics data
        system_perf = engine.analyze_system_performance(db)
        robot_perf = engine.analyze_robot_performance(db)
        insights = engine.generate_insights(db)

        db.disconnect()

        dashboard = {
            "system_performance": system_perf if "error" not in system_perf else None,
            "robot_performance": robot_perf if "error" not in robot_perf else None,
            "insights": insights,
            "summary": {
                "total_insights": len(insights),
                "system_health": "good" if "error" not in system_perf else "error",
                "robot_health": "good" if "error" not in robot_perf else "error"
            }
        }

        return jsonify({
            "status": "success",
            "dashboard": dashboard,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Dashboard data generation failed: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/metrics/<metric_type>', methods=['GET'])
def get_specific_metrics(metric_type: str):
    """Get specific type of metrics"""
    if not get_analytics_engine or not get_db_manager:
        return jsonify({"error": "Analytics not available"}), 503

    try:
        engine = get_analytics_engine()
        db = get_db_manager()

        if not db.connect():
            return jsonify({"error": "Database connection failed"}), 503

        metrics = None

        if metric_type == "system":
            metrics = engine.analyze_system_performance(db)
        elif metric_type == "robot":
            metrics = engine.analyze_robot_performance(db)
        else:
            return jsonify({"error": f"Unknown metric type: {metric_type}"}), 400

        db.disconnect()

        if "error" in metrics:
            return jsonify({"error": metrics["error"]}), 500

        return jsonify({
            "status": "success",
            "metric_type": metric_type,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Specific metrics retrieval failed: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/trends/<timeframe>', methods=['GET'])
def get_trends(timeframe: str):
    """Get performance trends over specified timeframe"""
    if not get_analytics_engine or not get_db_manager:
        return jsonify({"error": "Analytics not available"}), 503

    valid_timeframes = ['hour', 'day', 'week', 'month']
    if timeframe not in valid_timeframes:
        return jsonify({"error": f"Invalid timeframe. Must be one of: {valid_timeframes}"}), 400

    try:
        # For now, return basic trend analysis
        # In a full implementation, this would analyze data over the specified timeframe
        engine = get_analytics_engine()
        db = get_db_manager()

        if not db.connect():
            return jsonify({"error": "Database connection failed"}), 503

        # Get recent data based on timeframe
        limit = 100  # Default
        if timeframe == 'hour':
            limit = 10
        elif timeframe == 'day':
            limit = 50
        elif timeframe == 'week':
            limit = 200
        elif timeframe == 'month':
            limit = 1000

        interactions = db.get_recent_interactions(limit)
        db.disconnect()

        # Analyze trends
        trends = {
            "timeframe": timeframe,
            "data_points": len(interactions),
            "avg_sentiment_trend": engine._analyze_performance_trends(interactions),
            "interaction_volume": len(interactions),
            "timeframe_analysis": f"Analysis based on last {limit} interactions"
        }

        return jsonify({
            "status": "success",
            "trends": trends,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Trends analysis failed: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/reports/generate', methods=['POST'])
def generate_report():
    """Generate a comprehensive analytics report"""
    if not get_analytics_engine or not get_db_manager:
        return jsonify({"error": "Analytics not available"}), 503

    try:
        data = request.get_json() or {}
        report_type = data.get('type', 'full')  # 'full', 'system', 'robot', 'insights'

        engine = get_analytics_engine()
        db = get_db_manager()

        if not db.connect():
            return jsonify({"error": "Database connection failed"}), 503

        report = {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "sections": {}
        }

        # Generate requested sections
        if report_type in ['full', 'system']:
            system_perf = engine.analyze_system_performance(db)
            report["sections"]["system_performance"] = system_perf if "error" not in system_perf else {"error": system_perf.get("error")}

        if report_type in ['full', 'robot']:
            robot_perf = engine.analyze_robot_performance(db)
            report["sections"]["robot_performance"] = robot_perf if "error" not in robot_perf else {"error": robot_perf.get("error")}

        if report_type in ['full', 'insights']:
            insights = engine.generate_insights(db)
            report["sections"]["insights"] = insights

        db.disconnect()

        return jsonify({
            "status": "success",
            "report": report
        })

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/health', methods=['GET'])
def analytics_health():
    """Check analytics system health"""
    try:
        health = {
            "analytics_engine": get_analytics_engine is not None,
            "database_connection": False,
            "overall_status": "healthy"
        }

        if get_db_manager:
            db = get_db_manager()
            health["database_connection"] = db.connect()
            if health["database_connection"]:
                db.disconnect()

        # Determine overall status
        if not health["analytics_engine"] or not health["database_connection"]:
            health["overall_status"] = "degraded"

        return jsonify({
            "status": "success",
            "health": health,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

def register_analytics_endpoints(app):
    """Register analytics endpoints with Flask app"""
    try:
        app.register_blueprint(analytics_bp)
        logger.info("Analytics endpoints registered")
    except Exception as e:
        logger.error(f"Failed to register analytics endpoints: {e}")

# Export for external use
__all__ = ['register_analytics_endpoints']