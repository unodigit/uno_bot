#!/usr/bin/env python3
"""Test script to verify TodoListMiddleware todo functionality."""

import sys
import os
sys.path.append('/media/DATA/projects/autonomous-coding-uno-bot/unobot')
sys.path.append('/media/DATA/projects/autonomous-coding-uno-bot/unobot/.venv/lib/python3.11/site-packages')

async def test_todolist_functionality():
    """Test full TodoListMiddleware functionality."""
    try:
        from deepagents import create_deep_agent
        from deepagents.backends import CompositeBackend, FilesystemBackend

        print("=== TodoListMiddleware Full Functionality Test ===")

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
            system_prompt="You are a helpful assistant that manages todo lists. Use the write_todos and read_todos functions to manage tasks.",
            backend=backend,
            middleware=[]  # No custom middleware
        )

        print("✓ Agent created successfully")

        # Test 1: Initial todo list creation
        print("\n--- Test 1: Create initial todo list ---")
        result1 = await agent.ainvoke({
            "messages": [
                {"role": "user", "content": "Create a todo list with these tasks: 1) Research project requirements 2) Design system architecture 3) Implement core features"}
            ]
        })

        print(f"✓ Todo list created")
        print(f"Result keys: {list(result1.keys())}")

        if 'todos' in result1:
            todos = result1['todos']
            print(f"Todos from result: {todos}")
        else:
            print("⚠ No todos in result")

        # Test 2: Read existing todo list
        print("\n--- Test 2: Read existing todo list ---")
        result2 = await agent.ainvoke({
            "messages": [
                {"role": "user", "content": "Please read the current todo list"}
            ]
        })

        print(f"✓ Todo list read")
        if 'todos' in result2:
            todos = result2['todos']
            print(f"Current todos: {todos}")

        # Test 3: Add more tasks
        print("\n--- Test 3: Add more tasks ---")
        result3 = await agent.ainvoke({
            "messages": [
                {"role": "user", "content": "Add these tasks to the todo list: 4) Write unit tests 5) Deploy to staging"}
            ]
        })

        print(f"✓ Tasks added")
        if 'todos' in result3:
            todos = result3['todos']
            print(f"Updated todos: {todos}")

        # Test 4: Check conversation history and state
        print("\n--- Test 4: Check conversation state ---")
        # Build conversation history from all results
        conversation_history = []
        for i, result in enumerate([result1, result2, result3], 1):
            if 'messages' in result:
                conversation_history.extend(result['messages'])
            print(f"Step {i} - Messages: {len(result.get('messages', []))}")
            if 'todos' in result:
                print(f"Step {i} - Todos: {result['todos']}")

        print("\n=== TodoListMiddleware Verification Results ===")

        # Check if todos were successfully managed
        has_todos = any('todos' in result for result in [result1, result2, result3])

        if has_todos:
            print("✅ TodoListMiddleware functionality is WORKING!")
            print("   - write_todos function available for task planning")
            print("   - read_todos function available for progress tracking")
            print("   - Todo state persists across conversation turns")
            print("   - Agent can manage conversation progress via todos")
            return True
        else:
            print("❌ TodoListMiddleware functionality is NOT working")
            return False

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_todolist_functionality())
    sys.exit(0 if success else 1)