from flask import Flask, request, jsonify
import os
import re
import joblib

# Support both package imports and direct script execution.
try:
    from .memory import load_memory, save_memory
    from .router import route
    from .escalation import needs_escalation
    from .agent_utils import format_agent_response, safe_llm_call
    from .ollama_client import ask_llm
except ImportError:
    from memory import load_memory, save_memory
    from router import route
    from escalation import needs_escalation
    from agent_utils import format_agent_response, safe_llm_call
    from ollama_client import ask_llm

# Phase 2: Database integration
try:
    from ..database.interaction_logger import log_web_interaction
    from ..database.connection import init_database_connection
    DB_ENABLED = True
except ImportError:
    try:
        from database.interaction_logger import log_web_interaction
        from database.connection import init_database_connection
        DB_ENABLED = True
    except ImportError:
        DB_ENABLED = False
        print("Database integration not available - running without logging")

# Phase 3: Training triggers integration
try:
    from ..training_triggers.training_api import register_training_endpoints
    TRAINING_ENABLED = True
except ImportError:
    try:
        from training_triggers.training_api import register_training_endpoints
        TRAINING_ENABLED = True
    except ImportError:
        TRAINING_ENABLED = False
        print("Training triggers not available - running without automated training")

# Phase 4: Export/sync integration
try:
    from ..export_sync.sync_api import register_sync_endpoints
    SYNC_ENABLED = True
except ImportError:
    try:
        from export_sync.sync_api import register_sync_endpoints
        SYNC_ENABLED = True
    except ImportError:
        SYNC_ENABLED = False
        print("Export/sync not available - running without model synchronization")

# Phase 5: Pi updates integration
try:
    from ..pi_updates.pi_update_api import register_pi_update_endpoints
    PI_UPDATES_ENABLED = True
except ImportError:
    try:
        from pi_updates.pi_update_api import register_pi_update_endpoints
        PI_UPDATES_ENABLED = True
    except ImportError:
        PI_UPDATES_ENABLED = False
        print("Pi updates not available - running without robot updates")

# Phase 6: Robot logging integration
try:
    from ..robot_logging.robot_logging_api import register_robot_logging_endpoints
    ROBOT_LOGGING_ENABLED = True
except ImportError:
    try:
        from robot_logging.robot_logging_api import register_robot_logging_endpoints
        ROBOT_LOGGING_ENABLED = True
    except ImportError:
        ROBOT_LOGGING_ENABLED = False
        print("Robot logging not available - running without robot interaction logging")

# Phase 7: Federated learning integration
try:
    from ..federated_learning.federated_api import register_federated_endpoints
    FEDERATED_ENABLED = True
except ImportError:
    try:
        from federated_learning.federated_api import register_federated_endpoints
        FEDERATED_ENABLED = True
    except ImportError:
        FEDERATED_ENABLED = False
        print("Federated learning not available - running without collaborative training")

# Phase 8: Advanced analytics integration
try:
    from ..advanced_analytics.analytics_api import register_analytics_endpoints
    ANALYTICS_ENABLED = True
except ImportError:
    try:
        from advanced_analytics.analytics_api import register_analytics_endpoints
        ANALYTICS_ENABLED = True
    except ImportError:
        ANALYTICS_ENABLED = False
        print("Advanced analytics not available - running without analytics")

# Phase 8.5: Recommendation engine integration
try:
    from ..recommendation.recommendation_engine import RecommendationEngine
    RECOMMENDATIONS_ENABLED = True
except ImportError:
    try:
        from recommendation.recommendation_engine import RecommendationEngine
        RECOMMENDATIONS_ENABLED = True
    except ImportError:
        RECOMMENDATIONS_ENABLED = False
        print("Recommendation engine not available - running without suggestions")

# Phase 9: Production deployment integration
try:
    from ..production_deployment.deployment_api import register_deployment_endpoints
    DEPLOYMENT_ENABLED = True
except ImportError:
    try:
        from production_deployment.deployment_api import register_deployment_endpoints
        DEPLOYMENT_ENABLED = True
    except ImportError:
        DEPLOYMENT_ENABLED = False
        print("Production deployment not available - running without production monitoring")

app = Flask(__name__)

# Allow the PHP website (served from http://localhost) to call this API (port 8000)
try:
    from flask_cors import CORS
    CORS(app, resources={r"/chat": {"origins": ["http://localhost"]}})
except Exception:
    # If flask-cors isn't installed, the server will still run,
    # but browser fetch() from another origin may be blocked.
    pass

BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "models")
USER_DIR = os.path.join(BASE_DIR, "users")
os.makedirs(USER_DIR, exist_ok=True)

MENTAL_MODEL_PATH = os.path.join(MODEL_DIR, "mental_health_classifier.joblib")
VECTOR_PATH = os.path.join(MODEL_DIR, "global_vectorizer.joblib")


def normalize_user_id(raw_user_id) -> str:
    """
    Convert user_id to a safe, consistent string so memory never mixes.
    We only allow digits (numeric user ids).
    """
    if raw_user_id is None:
        return ""

    s = str(raw_user_id).strip()

    # Keep only digits (reject anything else)
    if not re.fullmatch(r"\d+", s):
        return ""

    # Normalize: remove leading zeros by converting to int and back
    return str(int(s))


def load_mental_health_model():
    try:
        if not os.path.exists(MENTAL_MODEL_PATH):
            return None
        return joblib.load(MENTAL_MODEL_PATH)
    except Exception:
        return None


def mental_health_score(text):
    model = load_mental_health_model()
    if model is None:
        return None

    try:
        if not os.path.exists(VECTOR_PATH):
            return None

        vectorizer = joblib.load(VECTOR_PATH)
        X = vectorizer.transform([text])

        coef = model["coef"]
        intercept = model["intercept"]

        score = X @ coef.T + intercept
        return float(score[0][0])
    except Exception:
        return None


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}

    user_id_raw = data.get("user_id")
    message = (data.get("message") or "").strip()
    recommendations_enabled = bool(data.get("recommendations_enabled", True))

    user_id = normalize_user_id(user_id_raw)

    if not user_id or not message:
        return jsonify({"error": "user_id (numeric) and message required"}), 400

    # ✅ memory is ALWAYS per normalized numeric user_id
    memory = load_memory(USER_DIR, user_id)

    # router.route() takes only the message
    topic = route(message)

    if topic == "mental_health":
        risk = mental_health_score(message)
        escalation = needs_escalation(message, risk)
        if escalation:
            return jsonify(escalation)

        memory["mental_health"] = {
            "last_text": message,
            "risk_detected": bool(risk is not None and risk > 0.5)
        }

    # ✅ Smaller prompt = faster response
    recent = memory.get("recent_messages", [])[-5:]
    last_topic = memory.get("last_topic")

    prompt = f"""
Recent messages: {recent}
Last topic: {last_topic}

User message:
{message}

Respond as a helpful {topic} assistant.
"""

    response = safe_llm_call(ask_llm, prompt)

    # Phase 2: Log interaction to database
    if DB_ENABLED:
        try:
            sentiment = mental_health_score(message)
            log_web_interaction(
                user_id=int(user_id),
                input_text=message,
                response=response,
                agent_type=topic,
                sentiment_score=sentiment
            )
        except Exception as e:
            print(f"Database logging error: {e}")

    ml_analysis = None
    if recommendations_enabled and RECOMMENDATIONS_ENABLED:
        try:
            engine = RecommendationEngine()
            ml_analysis = engine.analyze(message=message, user_id=user_id, memory=memory)
        except Exception as e:
            print(f"Recommendation engine error: {e}")
    elif not recommendations_enabled:
        ml_analysis = {
            "enabled": False,
            "reason": "The user has opted out of recommendation suggestions."
        }

    # Save memory
    memory.setdefault("recent_messages", []).append(message)
    memory["recent_messages"] = memory["recent_messages"][-30:]
    memory["last_topic"] = topic
    save_memory(USER_DIR, user_id, memory)

    response_payload = format_agent_response(response)
    if ml_analysis is not None:
        response_payload["ml_analysis"] = ml_analysis

    return jsonify(response_payload)


@app.route("/health")
def health():
    return jsonify({"status": "AI server running"})


# Phase 8.5: Reading activity logging endpoint
@app.route("/log_reading", methods=["POST"])
def log_reading():
    data = request.json or {}

    user_id_raw = data.get("user_id")
    book_title = data.get("book_title", "").strip()
    duration_minutes = data.get("duration_minutes", 0)
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    progress_percent = data.get("progress_percent")
    mood_tag = data.get("mood_tag")

    user_id = normalize_user_id(user_id_raw)

    if not user_id or not book_title:
        return jsonify({"error": "user_id and book_title required"}), 400

    # Log the reading activity
    if DB_ENABLED:
        try:
            success = log_reading_activity(
                user_id=int(user_id),
                book_title=book_title,
                duration_minutes=duration_minutes,
                start_time=start_time,
                end_time=end_time,
                progress_percent=progress_percent,
                mood_tag=mood_tag
            )
            if success:
                return jsonify({"status": "logged"}), 200
            else:
                return jsonify({"error": "logging failed"}), 500
        except Exception as e:
            print(f"Reading logging error: {e}")
            return jsonify({"error": "internal error"}), 500
    else:
        return jsonify({"error": "database not available"}), 503


# Phase 3: Register training endpoints
if TRAINING_ENABLED:
    try:
        register_training_endpoints(app)
        print("Training API endpoints registered with AI server")
    except Exception as e:
        print(f"Failed to register training endpoints: {e}")

# Phase 4: Register export/sync endpoints
if SYNC_ENABLED:
    try:
        register_sync_endpoints(app)
        print("Export/sync API endpoints registered with AI server")
    except Exception as e:
        print(f"Failed to register sync endpoints: {e}")

# Phase 5: Register Pi update endpoints
if PI_UPDATES_ENABLED:
    try:
        register_pi_update_endpoints(app)
        print("Pi update API endpoints registered with AI server")
    except Exception as e:
        print(f"Failed to register Pi update endpoints: {e}")

# Phase 6: Register robot logging endpoints
if ROBOT_LOGGING_ENABLED:
    try:
        register_robot_logging_endpoints(app)
        print("Robot logging API endpoints registered with AI server")
    except Exception as e:
        print(f"Failed to register robot logging endpoints: {e}")

# Phase 7: Register federated learning endpoints
if FEDERATED_ENABLED:
    try:
        register_federated_endpoints(app)
        print("Federated learning API endpoints registered with AI server")
    except Exception as e:
        print(f"Failed to register federated learning endpoints: {e}")

# Phase 8: Register analytics endpoints
if ANALYTICS_ENABLED:
    try:
        register_analytics_endpoints(app)
        print("Advanced analytics API endpoints registered with AI server")
    except Exception as e:
        print(f"Failed to register analytics endpoints: {e}")

# Phase 9: Register production deployment endpoints
if DEPLOYMENT_ENABLED:
    try:
        register_deployment_endpoints(app)
        print("Production deployment API endpoints registered with AI server")
    except Exception as e:
        print(f"Failed to register deployment endpoints: {e}")


if __name__ == "__main__":
    app.run(port=8000, debug=True)
