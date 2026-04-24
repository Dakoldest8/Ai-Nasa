#!/usr/bin/env python3
"""
Phase 9: Complete System Integration Test
Tests all 9 phases of the Astronaut AI Ecosystem
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Any

# Add the web-assistant directory to the path
sys.path.insert(0, str(Path(__file__).parent / "web-assistant"))

class SystemIntegrationTest:
    """Comprehensive system integration testing"""

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.web_url = "http://localhost:5000"
        self.test_results = []
        self.phase_status = {}

    def log_test(self, phase: str, test_name: str, success: bool, message: str = ""):
        """Log a test result"""
        result = {
            "phase": phase,
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        status = "PASS" if success else "FAIL"
        print(f"[{phase}] {test_name}: {status} - {message}")

    def test_phase_1_core_ai(self) -> bool:
        """Test Phase 1: Core AI Pipeline"""
        print("\n=== Testing Phase 1: Core AI Pipeline ===")

        try:
            # Test basic chat endpoint
            response = requests.post(f"{self.base_url}/chat", json={
                "user_id": "12345",
                "message": "Hello, how are you?"
            }, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    self.log_test("Phase 1", "Basic Chat", True, "Chat endpoint working")
                    return True
                else:
                    self.log_test("Phase 1", "Basic Chat", False, "Missing response in chat data")
                    return False
            else:
                self.log_test("Phase 1", "Basic Chat", False, f"HTTP {response.status_code}")
                return False

        except Exception as e:
            self.log_test("Phase 1", "Basic Chat", False, str(e))
            return False

    def test_phase_2_database(self) -> bool:
        """Test Phase 2: Database Brain"""
        print("\n=== Testing Phase 2: Database Brain ===")

        success = True

        # Test database health (if available)
        try:
            response = requests.get(f"{self.base_url}/db/health", timeout=10)
            if response.status_code == 200:
                self.log_test("Phase 2", "Database Health", True, "Database connection healthy")
            else:
                self.log_test("Phase 2", "Database Health", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 2", "Database Health", False, "Database not available")
            success = False

        # Test interaction logging
        try:
            response = requests.post(f"{self.base_url}/db/log_interaction", json={
                "user_id": 12345,
                "input_text": "Test message",
                "response": "Test response",
                "agent_type": "test"
            }, timeout=10)

            if response.status_code == 200:
                self.log_test("Phase 2", "Interaction Logging", True, "Interaction logged successfully")
            else:
                self.log_test("Phase 2", "Interaction Logging", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 2", "Interaction Logging", False, "Interaction logging not available")
            success = False

        return success

    def test_phase_3_training(self) -> bool:
        """Test Phase 3: Training Triggers"""
        print("\n=== Testing Phase 3: Training Triggers ===")

        success = True

        # Test training status
        try:
            response = requests.get(f"{self.base_url}/training/status", timeout=10)
            if response.status_code == 200:
                self.log_test("Phase 3", "Training Status", True, "Training status retrieved")
            else:
                self.log_test("Phase 3", "Training Status", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 3", "Training Status", False, "Training API not available")
            success = False

        # Test trigger training
        try:
            response = requests.post(f"{self.base_url}/training/trigger", json={
                "trigger_type": "manual",
                "reason": "integration_test"
            }, timeout=10)

            if response.status_code in [200, 202]:
                self.log_test("Phase 3", "Training Trigger", True, "Training triggered successfully")
            else:
                self.log_test("Phase 3", "Training Trigger", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 3", "Training Trigger", False, "Training trigger not available")
            success = False

        return success

    def test_phase_4_sync(self) -> bool:
        """Test Phase 4: Export/Sync"""
        print("\n=== Testing Phase 4: Export/Sync ===")

        success = True

        # Test model export
        try:
            response = requests.post(f"{self.base_url}/sync/export", json={
                "model_name": "test_model",
                "version": "1.0.0"
            }, timeout=10)

            if response.status_code in [200, 201]:
                self.log_test("Phase 4", "Model Export", True, "Model export successful")
            else:
                self.log_test("Phase 4", "Model Export", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 4", "Model Export", False, "Export API not available")
            success = False

        # Test sync status
        try:
            response = requests.get(f"{self.base_url}/sync/status", timeout=10)
            if response.status_code == 200:
                self.log_test("Phase 4", "Sync Status", True, "Sync status retrieved")
            else:
                self.log_test("Phase 4", "Sync Status", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 4", "Sync Status", False, "Sync status not available")
            success = False

        return success

    def test_phase_5_pi_updates(self) -> bool:
        """Test Phase 5: Pi Updates"""
        print("\n=== Testing Phase 5: Pi Updates ===")

        success = True

        # Test update check
        try:
            response = requests.get(f"{self.base_url}/pi/check_updates", timeout=10)
            if response.status_code == 200:
                self.log_test("Phase 5", "Update Check", True, "Update check successful")
            else:
                self.log_test("Phase 5", "Update Check", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 5", "Update Check", False, "Pi updates API not available")
            success = False

        # Test update status
        try:
            response = requests.get(f"{self.base_url}/pi/update_status", timeout=10)
            if response.status_code == 200:
                self.log_test("Phase 5", "Update Status", True, "Update status retrieved")
            else:
                self.log_test("Phase 5", "Update Status", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 5", "Update Status", False, "Update status not available")
            success = False

        return success

    def test_phase_6_robot_logging(self) -> bool:
        """Test Phase 6: Robot Logging"""
        print("\n=== Testing Phase 6: Robot Logging ===")

        success = True

        # Test robot interaction logging
        try:
            response = requests.post(f"{self.base_url}/robot/log", json={
                "robot_id": "test_robot",
                "interaction_type": "test",
                "data": {"test": "data"}
            }, timeout=10)

            if response.status_code in [200, 201]:
                self.log_test("Phase 6", "Robot Logging", True, "Robot interaction logged")
            else:
                self.log_test("Phase 6", "Robot Logging", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 6", "Robot Logging", False, "Robot logging API not available")
            success = False

        # Test robot analytics
        try:
            response = requests.get(f"{self.base_url}/robot/analytics", timeout=10)
            if response.status_code == 200:
                self.log_test("Phase 6", "Robot Analytics", True, "Robot analytics retrieved")
            else:
                self.log_test("Phase 6", "Robot Analytics", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 6", "Robot Analytics", False, "Robot analytics not available")
            success = False

        return success

    def test_phase_7_federated(self) -> bool:
        """Test Phase 7: Federated Learning"""
        print("\n=== Testing Phase 7: Federated Learning ===")

        success = True

        # Test federated status
        try:
            response = requests.get(f"{self.base_url}/federated/status", timeout=10)
            if response.status_code == 200:
                self.log_test("Phase 7", "Federated Status", True, "Federated learning status retrieved")
            else:
                self.log_test("Phase 7", "Federated Status", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 7", "Federated Status", False, "Federated learning API not available")
            success = False

        # Test participant registration
        try:
            response = requests.post(f"{self.base_url}/federated/participant", json={
                "participant_id": "test_participant",
                "device_type": "test"
            }, timeout=10)

            if response.status_code in [200, 201]:
                self.log_test("Phase 7", "Participant Registration", True, "Participant registered")
            else:
                self.log_test("Phase 7", "Participant Registration", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 7", "Participant Registration", False, "Participant registration not available")
            success = False

        return success

    def test_phase_8_analytics(self) -> bool:
        """Test Phase 8: Advanced Analytics"""
        print("\n=== Testing Phase 8: Advanced Analytics ===")

        success = True

        # Test system analytics
        try:
            response = requests.get(f"{self.base_url}/analytics/system", timeout=10)
            if response.status_code == 200:
                self.log_test("Phase 8", "System Analytics", True, "System analytics retrieved")
            else:
                self.log_test("Phase 8", "System Analytics", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 8", "System Analytics", False, "System analytics not available")
            success = False

        # Test performance metrics
        try:
            response = requests.get(f"{self.base_url}/analytics/performance", timeout=10)
            if response.status_code == 200:
                self.log_test("Phase 8", "Performance Metrics", True, "Performance metrics retrieved")
            else:
                self.log_test("Phase 8", "Performance Metrics", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 8", "Performance Metrics", False, "Performance metrics not available")
            success = False

        return success

    def test_phase_9_deployment(self) -> bool:
        """Test Phase 9: Production Deployment"""
        print("\n=== Testing Phase 9: Production Deployment ===")

        success = True

        # Test system health monitoring
        try:
            response = requests.get(f"{self.base_url}/deploy/health", timeout=10)
            if response.status_code == 200:
                self.log_test("Phase 9", "System Health", True, "System health monitoring working")
            else:
                self.log_test("Phase 9", "System Health", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 9", "System Health", False, "System health monitoring not available")
            success = False

        # Test scaling status
        try:
            response = requests.get(f"{self.base_url}/deploy/scaling/status", timeout=10)
            if response.status_code == 200:
                self.log_test("Phase 9", "Scaling Status", True, "Auto-scaling status retrieved")
            else:
                self.log_test("Phase 9", "Scaling Status", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 9", "Scaling Status", False, "Auto-scaling not available")
            success = False

        # Test backup creation
        try:
            response = requests.post(f"{self.base_url}/deploy/backup/create", json={
                "components": ["config"]
            }, timeout=10)

            if response.status_code in [200, 201]:
                self.log_test("Phase 9", "Backup Creation", True, "Backup created successfully")
            else:
                self.log_test("Phase 9", "Backup Creation", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 9", "Backup Creation", False, "Backup creation not available")
            success = False

        # Test services status
        try:
            response = requests.get(f"{self.base_url}/deploy/services/status", timeout=10)
            if response.status_code == 200:
                self.log_test("Phase 9", "Services Status", True, "Services status retrieved")
            else:
                self.log_test("Phase 9", "Services Status", False, f"HTTP {response.status_code}")
                success = False
        except:
            self.log_test("Phase 9", "Services Status", False, "Services status not available")
            success = False

        return success

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all phase tests"""
        print("🚀 Starting Astronaut AI Ecosystem Integration Tests")
        print("=" * 60)

        # Test all phases
        phases = [
            ("Phase 1: Core AI Pipeline", self.test_phase_1_core_ai),
            ("Phase 2: Database Brain", self.test_phase_2_database),
            ("Phase 3: Training Triggers", self.test_phase_3_training),
            ("Phase 4: Export/Sync", self.test_phase_4_sync),
            ("Phase 5: Pi Updates", self.test_phase_5_pi_updates),
            ("Phase 6: Robot Logging", self.test_phase_6_robot_logging),
            ("Phase 7: Federated Learning", self.test_phase_7_federated),
            ("Phase 8: Advanced Analytics", self.test_phase_8_analytics),
            ("Phase 9: Production Deployment", self.test_phase_9_deployment)
        ]

        overall_success = True
        phase_results = {}

        for phase_name, test_func in phases:
            try:
                success = test_func()
                phase_results[phase_name] = success
                if not success:
                    overall_success = False
            except Exception as e:
                print(f"ERROR in {phase_name}: {e}")
                phase_results[phase_name] = False
                overall_success = False

        # Generate summary
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST SUMMARY")
        print("=" * 60)

        passed_phases = sum(1 for success in phase_results.values() if success)
        total_phases = len(phase_results)

        for phase, success in phase_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{phase}: {status}")

        print(f"\nOverall Result: {'✅ ALL PHASES PASSED' if overall_success else '❌ SOME PHASES FAILED'}")
        print(f"Passed: {passed_phases}/{total_phases} phases")

        # Save detailed results
        results_summary = {
            "overall_success": overall_success,
            "passed_phases": passed_phases,
            "total_phases": total_phases,
            "phase_results": phase_results,
            "detailed_results": self.test_results,
            "timestamp": time.time()
        }

        results_file = Path("integration_test_results.json")
        with open(results_file, "w") as f:
            json.dump(results_summary, f, indent=2, default=str)

        print(f"\nDetailed results saved to: {results_file}")

        return results_summary

def main():
    """Main test execution"""
    tester = SystemIntegrationTest()
    results = tester.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if results["overall_success"] else 1)

if __name__ == "__main__":
    main()