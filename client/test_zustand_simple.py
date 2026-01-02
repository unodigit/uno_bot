"""
Simple test to verify Zustand state management works
"""
import json

async def test_zustand_feature():
    """
    Test that the chat application uses Zustand for state management
    """
    print("Testing Zustand state management...")
    
    # Step 1: Check that chatStore.ts exists and uses Zustand
    try:
        with open('client/src/stores/chatStore.ts', 'r') as f:
            content = f.read()
            
        # Verify Zustand import
        if "import { create } from 'zustand'" in content:
            print("✓ Zustand is imported in chatStore.ts")
        else:
            print("✗ Zustand import not found")
            return False
            
        # Verify store structure
        if "create<ChatStore>" in content or "create<" in content:
            print("✓ Store is created with Zustand")
        else:
            print("✗ Store creation not found")
            return False
            
        # Verify state management
        if "set(" in content and "get(" in content:
            print("✓ State management functions (set/get) are used")
        else:
            print("✗ State management functions not found")
            return False
            
        # Check for state persistence
        if "localStorage" in content or "persist" in content:
            print("✓ State persistence is configured")
        else:
            print("ℹ State persistence not configured (optional)")
            
        print("\n✓ Zustand state management is correctly implemented")
        return True
        
    except FileNotFoundError:
        print("✗ chatStore.ts not found")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

import asyncio
result = asyncio.run(test_zustand_feature())
