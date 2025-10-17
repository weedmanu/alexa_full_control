#!/usr/bin/env python3
"""Test script for Scenario CLI integration."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from cli import create_context
from cli.commands import ScenarioCommand
import argparse

def test_create():
    """Test creating a scenario."""
    print("=" * 60)
    print("Testing Scenario CLI Integration")
    print("=" * 60)
    
    # Create context
    ctx = create_context()
    
    # Create command
    cmd = ScenarioCommand(ctx)
    
    # Test create
    print("\n1️⃣  Testing scenario creation...")
    args = argparse.Namespace(
        name='Ambiance Salon',
        actions='[{"device": "Salon Echo", "action": "volume", "params": {"level": 50}}]'
    )
    success = cmd._create_scenario(args)
    print(f"   Create result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    # Test list
    print("\n2️⃣  Testing scenario listing...")
    args = argparse.Namespace()
    cmd._list_scenarios(args)
    
    # Test show
    print("\n3️⃣  Testing scenario details...")
    args = argparse.Namespace(name='Ambiance Salon')
    cmd._show_scenario_info(args)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    
    ctx.cleanup()

if __name__ == '__main__':
    test_create()
