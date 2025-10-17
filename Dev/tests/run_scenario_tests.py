#!/usr/bin/env python3
"""Run all Scenario tests directly."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[1]))

from Dev.pytests.core.scenario.test_scenario_manager import (
    TestScenarioCreation,
    TestScenarioDeletion,
    TestScenarioEditing,
    TestScenarioExecution,
    TestScenarioExportImport,
    TestScenarioManagerInit,
    TestScenarioPersistence,
    TestScenarioRenaming,
    TestScenarioRetrieval,
    TestScenarioSearch,
    TestScenarioValidation,
)


def run_all_tests():
    """Run all test classes."""
    test_classes = [
        ("Initialization", TestScenarioManagerInit),
        ("Creation", TestScenarioCreation),
        ("Retrieval", TestScenarioRetrieval),
        ("Deletion", TestScenarioDeletion),
        ("Execution", TestScenarioExecution),
        ("Persistence", TestScenarioPersistence),
        ("Renaming", TestScenarioRenaming),
        ("Editing", TestScenarioEditing),
        ("Validation", TestScenarioValidation),
        ("Search", TestScenarioSearch),
        ("Export/Import", TestScenarioExportImport),
    ]

    total_tests = 0
    total_passed = 0
    total_failed = 0

    print("=" * 70)
    print("🎬 SCENARIO MANAGER - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    for name, test_class in test_classes:
        print(f"\n▶️  {name} Tests:")
        print("-" * 70)

        try:
            instance = test_class()

            # Get all test methods
            test_methods = [m for m in dir(instance) if m.startswith('test_')]

            class_passed = 0
            class_failed = 0

            for method_name in test_methods:
                total_tests += 1
                try:
                    method = getattr(instance, method_name)
                    method()
                    print(f"  ✅ {method_name}")
                    class_passed += 1
                    total_passed += 1
                except Exception as e:
                    print(f"  ❌ {method_name}: {e}")
                    class_failed += 1
                    total_failed += 1

            print(f"  Result: {class_passed}/{class_passed + class_failed} passed")
        except Exception as e:
            print(f"  ❌ Setup error: {e}")
            total_failed += len([m for m in dir(test_class) if m.startswith('test_')])

    print("\n" + "=" * 70)
    print(f"📊 FINAL RESULTS: {total_passed}/{total_tests} tests passed")
    if total_failed == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {total_failed} tests failed")
    print("=" * 70)

    return total_failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
