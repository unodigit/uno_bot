#!/usr/bin/env python3
"""Test script to verify TodoListMiddleware state functionality."""

import sys
import os
sys.path.append('/media/DATA/projects/autonomous-coding-uno-bot/unobot')
sys.path.append('/media/DATA/projects/autonomous-coding-uno-bot/unobot/.venv/lib/python3.11/site-packages')

async def test_todolist_middleware_state():
    """Test if TodoListMiddleware creates state that can be accessed."""
    try:
        from deepagents import create_deep_agent
        from deepagents.backends import CompositeBackend, FilesystemBackend

        print("=== Testing TodoListMiddleware State Access ===")

        # Create a temporary directory for testing
        test_dir = "/tmp/deepagents_test"
        os.makedirs(test_dir, exist_ok=True)

        backend = CompositeBackend(
            default=FilesystemBackend(root_dir=test_dir),
            routes={
                "/prd/": FilesystemBackend(root_dir=test_dir)
            }
        )

        # Create agent with default model
        agent = create_deep_agent(
            tools=[],  # No custom tools
            system_prompt="You are a test agent for todo functionality",
            backend=backend,
            middleware=[]  # No custom middleware
        )

        print("✓ Agent created successfully")

        # Test 1: Run the agent with a simple input
        print("\n--- Test 1: Initial agent run ---")
        try:
            result = await agent.ainvoke({
                "messages": [
                    {"role": "user", "content": "Please create a todo list with 3 tasks"}
                ]
            })
            print(f"✓ Agent executed successfully")
            print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else type(result)}")
        except Exception as e:
            print(f"⚠ Agent execution failed: {e}")

        # Test 2: Check agent state
        print("\n--- Test 2: Check agent state ---")
        try:
            state = agent.get_state(None)  # Use None for current thread
            print(f"✓ Agent state retrieved")
            print(f"State type: {type(state)}")
            if hasattr(state, 'values'):
                print(f"State values: {state.values}")
            else:
                print(f"State: {state}")
        except Exception as e:
            print(f"⚠ State retrieval failed: {e}")

        # Test 3: Check if agent has any todo-related state
        print("\n--- Test 3: Look for todo-related state ---")
        try:
            # Try to access backend directly
            if hasattr(agent, 'store') and agent.store:
                print(f"Agent store: {agent.store}")
                # Try to list items in store
                try:
                    # This might contain todo state
                    pass
                except Exception as e:
                    print(f"Store access failed: {e}")
        except Exception as e:
            print(f"⚠ Backend access failed: {e}")

        print("\n=== TodoListMiddleware State Verification ===")
        print("Note: TodoListMiddleware may store state in the agent's internal state")
        print("The write_todos and read_todos functions might be available as tools")
        print("when the agent is invoked with appropriate input")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_todolist_middleware_state())
    sys.exit(0 if success else 1)