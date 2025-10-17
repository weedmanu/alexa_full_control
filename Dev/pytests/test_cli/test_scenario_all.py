#!/usr/bin/env python3
"""Test script for Scenario CLI - all actions."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

import argparse

from cli import create_context
from cli.commands import ScenarioCommand


def test_all_actions():
    """Test all scenario actions."""
    print("=" * 70)
    print("🎬 TESTING ALL SCENARIO CLI ACTIONS")
    print("=" * 70)

    # Create context
    ctx = create_context()

    # Create command
    cmd = ScenarioCommand(ctx)

    # Test 1: Create multiple scenarios
    print("\n1️⃣  Creating scenarios...")

    args = argparse.Namespace(
        name="Ambiance Salon", actions='[{"device": "Salon Echo", "action": "volume", "params": {"level": 50}}]'
    )
    cmd._create_scenario(args)

    args = argparse.Namespace(
        name="Morning Routine",
        actions='[{"device": "Cuisine", "action": "play", "params": {"song": "Despacito"}, "delay": 1}, {"device": "Salon Echo", "action": "volume", "params": {"level": 30}, "delay": 2}]',
    )
    cmd._create_scenario(args)

    # Test 2: List scenarios
    print("\n2️⃣  Listing all scenarios...")
    args = argparse.Namespace()
    cmd._list_scenarios(args)

    # Test 3: Show scenario details
    print("\n3️⃣  Showing scenario details...")
    args = argparse.Namespace(name="Morning Routine")
    cmd._show_scenario_info(args)

    # Test 4: Delete scenario
    print("\n4️⃣  Deleting scenario 'Ambiance Salon'...")
    args = argparse.Namespace(name="Ambiance Salon", force=True)
    cmd._delete_scenario(args)

    # Test 5: List after deletion
    print("\n5️⃣  Listing scenarios after deletion...")
    args = argparse.Namespace()
    cmd._list_scenarios(args)

    # Test 6: Edit scenario
    print("\n6️⃣  Editing 'Morning Routine'...")
    args = argparse.Namespace(
        name="Morning Routine",
        actions='[{"device": "Cuisine", "action": "volume", "params": {"level": 60}}, {"device": "Salon Echo", "action": "play", "params": {"song": "Bohemian Rhapsody"}}]',
    )
    cmd._edit_scenario(args)

    # Test 7: Show updated scenario
    print("\n7️⃣  Showing updated scenario...")
    args = argparse.Namespace(name="Morning Routine")
    cmd._show_scenario_info(args)

    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

    ctx.cleanup()


if __name__ == "__main__":
    test_all_actions()
