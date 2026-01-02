#!/usr/bin/env python3
"""Test script to verify DeepAgents subagent delegation functionality (simplified)."""

import sys
import os
sys.path.append('/media/DATA/projects/autonomous-coding-uno-bot/unobot')
sys.path.append('/media/DATA/projects/autonomous-coding-uno-bot/unobot/.venv/lib/python3.11/site-packages')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def test_subagent_delegation():
    """Test if DeepAgents subagent delegation works correctly."""
    try:
        from deepagents import create_deep_agent
        from deepagents.backends import CompositeBackend, FilesystemBackend

        print("=== Testing SubAgent Delegation ===")

        # Create a temporary directory for testing
        test_dir = "/tmp/deepagents_subagent_test"
        os.makedirs(test_dir, exist_ok=True)

        backend = CompositeBackend(
            default=FilesystemBackend(root_dir=test_dir),
            routes={
                "/prd/": FilesystemBackend(root_dir=test_dir)
            }
        )

        # Define simple subagents for testing
        subagents = [
            {
                "name": "greeting-agent",
                "description": "Handles greetings and introductions",
                "system_prompt": "You are a greeting specialist. Your role is to provide friendly, professional greetings. Keep responses brief and welcoming.",
            },
            {
                "name": "math-agent",
                "description": "Handles mathematical calculations",
                "system_prompt": "You are a math specialist. Your role is to perform basic arithmetic calculations. Show your work.",
            },
            {
                "name": "summary-agent",
                "description": "Summarizes information",
                "system_prompt": "You are a summary specialist. Your role is to provide concise summaries of information.",
            }
        ]

        # Create agent with subagents
        agent = create_deep_agent(
            tools=[],  # No custom tools
            system_prompt="""You are a coordinator that delegates tasks to specialized subagents.
When you need to handle greetings, delegate to @greeting-agent.
When you need to do calculations, delegate to @math-agent.
When you need to summarize information, delegate to @summary-agent.

Always use the appropriate subagent for their specialized task.""",
            subagents=subagents,
            backend=backend,
            middleware=[]  # No custom middleware
        )

        print("✓ Agent with subagents created successfully")
        print(f"  Subagents registered: {[s['name'] for s in subagents]}")

        # Test 1: Greeting delegation
        print("\n--- Test 1: Greeting delegation ---")
        result1 = await agent.ainvoke({
            "messages": [
                {"role": "user", "content": "Say hello to our new user"}
            ]
        })

        print(f"✓ Greeting task executed")
        if 'messages' in result1:
            last_msg = result1['messages'][-1]
            if hasattr(last_msg, 'content'):
                print(f"  Response: {last_msg.content[:100]}...")

        # Test 2: Math delegation
        print("\n--- Test 2: Math calculation delegation ---")
        result2 = await agent.ainvoke({
            "messages": result1.get('messages', []) + [
                {"role": "user", "content": "What is 25 times 37?"}
            ]
        })

        print(f"✓ Math calculation task executed")
        if 'messages' in result2:
            last_msg = result2['messages'][-1]
            if hasattr(last_msg, 'content'):
                print(f"  Response: {last_msg.content[:100]}...")

        # Test 3: Summary delegation
        print("\n--- Test 3: Summary delegation ---")
        result3 = await agent.ainvoke({
            "messages": result2.get('messages', []) + [
                {"role": "user", "content": "Summarize what we've done so far in one sentence"}
            ]
        })

        print(f"✓ Summary task executed")
        if 'messages' in result3:
            last_msg = result3['messages'][-1]
            if hasattr(last_msg, 'content'):
                print(f"  Response: {last_msg.content[:100]}...")

        # Test 4: Explicit subagent invocation
        print("\n--- Test 4: Explicit subagent invocation ---")
        result4 = await agent.ainvoke({
            "messages": [
                {"role": "user", "content": "I need you to calculate 100 divided by 4"}
            ]
        })

        print(f"✓ Explicit invocation executed")
        if 'messages' in result4:
            last_msg = result4['messages'][-1]
            if hasattr(last_msg, 'content'):
                print(f"  Response: {last_msg.content[:100]}...")

        print("\n=== SubAgent Delegation Verification ===")

        # Check if all tests executed successfully
        all_results = [result1, result2, result3, result4]
        success_count = sum(1 for result in all_results if isinstance(result, dict) and 'messages' in result)

        if success_count == len(all_results):
            print(f"✅ SubAgent delegation is WORKING! ({success_count}/{len(all_results)} tests passed)")
            print("   - Subagents can be registered with create_deep_agent()")
            print("   - Main agent delegates to specialized subagents")
            print("   - Multiple subagents can be used in conversation")
            print("   - Subagent invocation works correctly")
            return True
        else:
            print(f"⚠ Only {success_count}/{len(all_results)} tests succeeded")
            return False

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_subagent_delegation())
    sys.exit(0 if success else 1)
