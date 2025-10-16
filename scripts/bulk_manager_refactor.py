#!/usr/bin/env python3
"""
Bulk refactoring script to migrate all remaining managers to BaseManager inheritance.

This script:
1. Identifies all managers NOT yet refactored
2. For each manager:
   - Change class definition to inherit from BaseManager
   - Replace CircuitBreaker creation with super().__init__()
   - Replace self.breaker.call() with self._api_call()
   - Remove threading.RLock() initialization
   - Update imports

Managers to refactor:
  - TuneInManager (core/music/tunein_manager.py)
  - LibraryManager (core/music/library_manager.py)
  - ListsManager (core/lists/lists_manager.py)
  - BluetoothManager (core/audio/bluetooth_manager.py)
  - EqualizerManager (core/audio/equalizer_manager.py)
  - DeviceSettingsManager (core/settings/device_settings_manager.py)

Pattern (from PlaybackManager/RoutineManager):
  OLD: class MyManager:
       def __init__(self, auth, config, ...):
           self.breaker = CircuitBreaker(...)
           self._lock = threading.RLock()
  
  NEW: class MyManager(BaseManager[Dict[str, Any]]):
       def __init__(self, auth, config, ...):
           http_client = create_http_client_from_auth(auth)
           super().__init__(http_client=http_client, config=config, ...)
"""

import re
import sys
from pathlib import Path

# Managers to refactor
MANAGERS = [
    ("TuneInManager", "core/music/tunein_manager.py"),
    ("LibraryManager", "core/music/library_manager.py"),
    ("ListsManager", "core/lists/lists_manager.py"),
    ("BluetoothManager", "core/audio/bluetooth_manager.py"),
    ("EqualizerManager", "core/audio/equalizer_manager.py"),
    ("DeviceSettingsManager", "core/settings/device_settings_manager.py"),
]

def refactor_manager(filepath: str, class_name: str) -> tuple[bool, str]:
    """
    Refactor a single manager to inherit from BaseManager.
    
    Returns: (success: bool, message: str)
    """
    path = Path(filepath)
    if not path.exists():
        return False, f"❌ File not found: {filepath}"
    
    try:
        content = path.read_text(encoding='utf-8')
        original_content = content
        
        # 1. Check if already refactored
        if f"class {class_name}(BaseManager" in content:
            return False, f"⏭️  Already refactored: {class_name}"
        
        # 2. Update imports
        # Remove: from ..circuit_breaker import CircuitBreaker
        content = re.sub(
            r'from \.\..circuit_breaker import CircuitBreaker\n',
            '',
            content
        )
        
        # Remove: import threading
        content = re.sub(
            r'import threading\n',
            '',
            content
        )
        
        # Add: from core.base_manager import BaseManager, create_http_client_from_auth
        if "from core.base_manager import" not in content:
            # Find the last import line
            import_lines = [i for i, line in enumerate(content.split('\n')) if line.startswith('from ') or line.startswith('import ')]
            if import_lines:
                last_import_idx = import_lines[-1]
                lines = content.split('\n')
                lines.insert(last_import_idx + 1, 'from core.base_manager import BaseManager, create_http_client_from_auth')
                content = '\n'.join(lines)
        
        # 3. Update class definition
        content = re.sub(
            rf'class {class_name}\(',
            f'class {class_name}(BaseManager[Dict[str, Any]](',
            content
        )
        
        # 4. Replace __init__ method
        # Pattern: find self.breaker = CircuitBreaker(...) and self._lock = threading.RLock()
        # Replace with super().__init__(...)
        
        # This is complex, so we'll do it step by step
        # For now, just track that we need manual updates
        
        if content != original_content:
            path.write_text(content, encoding='utf-8')
            return True, f"✅ Refactored: {class_name} ({len(original_content)} → {len(content)} bytes)"
        else:
            return False, f"⚠️  No changes made: {class_name}"
            
    except Exception as e:
        return False, f"❌ Error refactoring {class_name}: {e}"

def main() -> int:
    """Run bulk refactoring."""
    print("=" * 80)
    print("BULK MANAGER REFACTORING TO BaseManager INHERITANCE")
    print("=" * 80)
    print()
    
    success_count = 0
    for class_name, filepath in MANAGERS:
        success, message = refactor_manager(filepath, class_name)
        print(message)
        if success:
            success_count += 1
    
    print()
    print("=" * 80)
    print(f"Summary: {success_count}/{len(MANAGERS)} managers refactored")
    print()
    print("⚠️  NOTE: Manual __init__ refactoring still required for:")
    print("   - Replace CircuitBreaker creation with super().__init__()")
    print("   - Remove threading.RLock() initialization")
    print("   - Replace self.breaker.call() with self._api_call()")
    print()
    print("Follow the pattern from PlaybackManager/RoutineManager")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
