#!/usr/bin/env python3
"""Test that config_flow can be imported."""

import sys
import os

# Add custom_components to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "custom_components"))

try:
    print("Testing config_flow import...")
    from netcommander.config_flow import ConfigFlow, DOMAIN
    print(f"✓ Successfully imported ConfigFlow")
    print(f"✓ Domain: {DOMAIN}")
    print(f"✓ ConfigFlow class: {ConfigFlow}")
    print(f"✓ VERSION: {ConfigFlow.VERSION}")
    print("\n✅ All imports successful!")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
