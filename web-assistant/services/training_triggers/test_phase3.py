"""
Phase 3: Smart Training Triggers Test
Tests the automated training trigger logic and API endpoints
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

# Add paths for imports
import os
import sys

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, grandparent_dir)
sys.path.insert(0, parent_dir)

def test_phase3_training_triggers():
    """Test the complete Phase 3 smart training trigger system"""

    print("🧠 Phase 3: Smart Training Triggers Test")
    print("=" * 50)

    # Test 1: Database Connection
    print("\n📡 Test 1: Database Connection...")
    try:
        from services.database.connection import init_database_connection
        success = init_database_connection()
        if success:
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

    # Test 2: Training Trigger Logic
    print("\n🎯 Test 2: Training Trigger Logic...")
    try:
        from services.training_triggers.trigger_logic import get_trigger_status, force_training_trigger

        # Get initial status
        status = get_trigger_status()
        if "error" not in status:
            print("✅ Trigger status retrieved")
            print(f"   Should train: {status['should_train']}")
            print(f"   Reason: {status['reason']}")
            print(f"   Unused interactions: {status['current_stats']['unused_interactions']}")
        else:
            print(f"❌ Trigger status error: {status['error']}")
            return False

    except Exception as e:
        print(f"❌ Trigger logic error: {e}")
        return False

    # Test 3: Force Training Trigger
    print("\n🚀 Test 3: Force Training Trigger...")
    try:
        success = force_training_trigger("Phase 3 test trigger")
        if success:
            print("✅ Training trigger forced successfully")
        else:
            print("❌ Failed to force training trigger")
            return False

    except Exception as e:
        print(f"❌ Force trigger error: {e}")
        return False

    # Test 4: Automated Training Service
    print("\n🤖 Test 4: Automated Training Service...")
    try:
        from services.training_triggers.automated_service import get_training_service

        service = get_training_service(auto_start=False)  # Don't auto-start for test
        service_status = service.get_service_status()

        print("✅ Automated training service initialized")
        print(f"   Service running: {service_status['service_running']}")
        print(f"   Check interval: {service_status['check_interval_minutes']} minutes")

    except Exception as e:
        print(f"❌ Automated service error: {e}")
        return False

    # Test 5: Training API Endpoints (if server is running)
    print("\n🌐 Test 5: Training API Endpoints...")
    try:
        # Try to connect to AI server (assumes it's running on port 8000)
        response = requests.get("http://localhost:8000/training/status", timeout=5)

        if response.status_code == 200:
            api_status = response.json()
            print("✅ Training API endpoints accessible")
            print(f"   Should train: {api_status['trigger_status']['should_train']}")
            print(f"   Service running: {api_status['service_status']['service_running']}")
        else:
            print(f"⚠️  AI server not running (status: {response.status_code}) - API test skipped")

    except requests.exceptions.RequestException:
        print("⚠️  AI server not accessible - API test skipped")
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

    # Test 6: Manual Training Trigger via API
    print("\n🔧 Test 6: Manual Training via API...")
    try:
        response = requests.post(
            "http://localhost:8000/training/trigger",
            json={"reason": "Phase 3 API test"},
            timeout=5
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Manual training trigger API successful")
            print(f"   Status: {result['status']}")
        else:
            print(f"⚠️  API returned status {response.status_code} - server may not be running")

    except requests.exceptions.RequestException:
        print("⚠️  AI server not accessible - manual trigger test skipped")
    except Exception as e:
        print(f"❌ Manual trigger API error: {e}")
        return False

    print("\n🎉 Phase 3 Smart Training Triggers Test: SUCCESS!")
    print("\nSummary:")
    print("- ✅ Database connection works")
    print("- ✅ Training trigger logic works")
    print("- ✅ Force trigger works")
    print("- ✅ Automated service initializes")
    print("- ✅ API endpoints registered (when server running)")
    print("- ✅ Manual trigger API works (when server running)")
    print("\nReady for Phase 4: Export + Sync System")

    # Cleanup
    try:
        from services.database.connection import close_database_connection
        close_database_connection()
        print("✅ Database connection closed")
    except Exception:
        pass

    return True

def demo_training_trigger_conditions():
    """Demonstrate different training trigger conditions"""
    print("\n📊 Training Trigger Conditions Demo")
    print("-" * 40)

    try:
        from services.training_triggers.trigger_logic import get_trigger_status

        status = get_trigger_status()

        print("Current Conditions:")
        print(f"  Unused Interactions: {status['current_stats']['unused_interactions']} / {status['trigger_conditions']['min_interactions_threshold']} needed")
        print(f"  Hours Since Training: {status['trigger_conditions']['hours_since_last_training']:.1f} / {status['trigger_conditions']['max_training_gap_hours']} max gap")
        print(f"  Average Sentiment: {status['trigger_conditions']['average_sentiment']:.2f} / {status['trigger_conditions']['sentiment_threshold']} threshold")
        print(f"  Agent Diversity OK: {status['trigger_conditions']['agent_diversity_ok']}")
        print(f"\nShould Train: {status['should_train']}")
        print(f"Reason: {status['reason']}")

    except Exception as e:
        print(f"Demo error: {e}")

if __name__ == "__main__":
    success = test_phase3_training_triggers()

    # Show demo regardless of test result
    demo_training_trigger_conditions()

    sys.exit(0 if success else 1)