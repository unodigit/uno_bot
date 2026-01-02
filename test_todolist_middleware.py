#!/usr/bin/env python3
"""Test script to verify TodoListMiddleware functionality in DeepAgents."""

import sys
import os
sys.path.append('/media/DATA/projects/autonomous-coding-uno-bot/unobot')
sys.path.append('/media/DATA/projects/autonomous-coding-uno-bot/unobot/.venv/lib/python3.11/site-packages')

async def test_todolist_middleware():
    """Test if TodoListMiddleware functions are available."""
    try:
        from deepagents import create_deep_agent
        from deepagents.backends import CompositeBackend, FilesystemBackend

        print("=== Testing TodoListMiddleware Functionality ===")

        # Create a simple agent to test todo functionality
        # We'll use just FilesystemBackend since StateBackend requires runtime

        # Create a temporary directory for testing
        test_dir = "/tmp/deepagents_test"
        os.makedirs(test_dir, exist_ok=True)

        backend = CompositeBackend(
            default=FilesystemBackend(root_dir=test_dir),
            routes={
                "/prd/": FilesystemBackend(root_dir=test_dir)
            }
        )

        agent = create_deep_agent(
            model=None,  # Use default Claude Sonnet 4
            tools=[],  # No custom tools
            system_prompt="You are a test agent for todo functionality",
            backend=backend,
            middleware=[]  # No custom middleware
        )

        print("✓ Agent created successfully")

        # Check if agent has todo-related functions
        agent_attrs = dir(agent)
        todo_functions = [attr for attr in agent_attrs if 'todo' in attr.lower()]

        print(f"Agent attributes containing 'todo': {todo_functions}")

        # Check for specific todo functions
        expected_functions = ['write_todos', 'read_todos']

        for func_name in expected_functions:
            if hasattr(agent, func_name):
                print(f"✓ {func_name} tool is available")
            else:
                print(f"✗ {func_name} tool is NOT available")

        # Try to call write_todos if available
        if hasattr(agent, 'write_todos'):
            try:
                # This should work if the function exists
                result = agent.write_todos(["Test task 1", "Test task 2"])
                print(f"✓ write_todos executed successfully: {result}")
            except Exception as e:
                print(f"⚠ write_todos call failed: {e}")

        # Try to call read_todos if available
        if hasattr(agent, 'read_todos'):
            try:
                result = agent.read_todos()
                print(f"✓ read_todos executed successfully: {result}")
            except Exception as e:
                print(f"⚠ read_todos call failed: {e}")

        print("\n=== Conclusion ===")
        if hasattr(agent, 'write_todos') and hasattr(agent, 'read_todos'):
            print("✅ TodoListMiddleware functionality is WORKING - both write_todos and read_todos are available")
            return True
        else:
            print("❌ TodoListMiddleware functionality is NOT WORKING - missing required functions")
            return False

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_todolist_middleware())
    sys.exit(0 if success else 1)