"""
Phase 2: Database Integration Test
Tests the MySQL brain integration with interaction logging and model tracking
"""

import os
import sys
import json
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_phase2_database_integration():
    """Test the complete Phase 2 database integration"""

    print("🧠 Phase 2: MySQL Brain Integration Test")
    print("=" * 50)

    # Test 1: Database Connection
    print("\n📡 Test 1: Database Connection...")
    try:
        from database.connection import init_database_connection, get_db_manager, close_database_connection

        success = init_database_connection()
        if success:
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return False

    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

    # Test 2: Log Interactions
    print("\n💬 Test 2: Interaction Logging...")
    try:
        from database.interaction_logger import log_web_interaction, log_pi_interaction, get_interaction_logger

        # Log some test interactions
        web_success = log_web_interaction(
            user_id=1,
            input_text="Hello, how are you?",
            response="I'm doing well, thank you!",
            agent_type="general",
            sentiment_score=0.2
        )

        pi_success = log_pi_interaction(
            input_text="Tell me a joke",
            response="Why did the robot go to school? To improve its learning algorithms!",
            agent_type="robot_general"
        )

        if web_success and pi_success:
            print("✅ Interaction logging successful")
        else:
            print("❌ Interaction logging failed")
            return False

    except Exception as e:
        print(f"❌ Interaction logging error: {e}")
        return False

    # Test 3: Model Tracking
    print("\n🤖 Test 3: Model Tracking...")
    try:
        from database.model_tracker import record_new_model, get_model_tracker

        # Record a test model
        model_data = {
            "notes": "Test model for Phase 2 integration",
            "training_interactions": 25,
            "base_model": "microsoft/DialoGPT-small"
        }

        model_success = record_new_model(
            version=1,
            file_name="model_v1_test",
            training_data=model_data
        )

        if model_success:
            print("✅ Model tracking successful")
        else:
            print("❌ Model tracking failed")
            return False

    except Exception as e:
        print(f"❌ Model tracking error: {e}")
        return False

    # Test 4: System State
    print("\n📊 Test 4: System State Tracking...")
    try:
        db = get_db_manager()
        state = db.get_system_state()

        if state:
            print(f"✅ System state retrieved: v{state.get('last_model_version', 0)} model, {state.get('total_interactions', 0)} interactions")
        else:
            print("❌ System state retrieval failed")
            return False

    except Exception as e:
        print(f"❌ System state error: {e}")
        return False

    # Test 5: Training Data Summary
    print("\n📈 Test 5: Training Data Summary...")
    try:
        from database.model_tracker import get_training_summary

        summary = get_training_summary()
        if "error" not in summary:
            print(f"✅ Training summary: {summary['total_interactions']} total, {summary['unused_interactions']} unused")
        else:
            print(f"❌ Training summary error: {summary['error']}")
            return False

    except Exception as e:
        print(f"❌ Training summary error: {e}")
        return False

    # Test 6: Training Trigger Check
    print("\n🚀 Test 6: Training Trigger Logic...")
    try:
        from database.model_tracker import should_trigger_training

        should_train = should_trigger_training()
        print(f"✅ Training trigger check: {'YES' if should_train else 'NO'} (needs 50+ unused interactions)")

    except Exception as e:
        print(f"❌ Training trigger error: {e}")
        return False

    # Cleanup
    print("\n🧹 Cleaning up...")
    close_database_connection()
    print("✅ Database connection closed")

    print("\n🎉 Phase 2 Database Integration Test: SUCCESS!")
    print("\nSummary:")
    print("- ✅ Database connection works")
    print("- ✅ Interaction logging works")
    print("- ✅ Model tracking works")
    print("- ✅ System state tracking works")
    print("- ✅ Training data queries work")
    print("- ✅ Training trigger logic works")
    print("\nReady for Phase 3: Smart Training Triggers")

    return True

if __name__ == "__main__":
    success = test_phase2_database_integration()
    sys.exit(0 if success else 1)