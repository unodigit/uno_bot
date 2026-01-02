#!/usr/bin/env python3
"""
Download and verify the PRD content.
"""

import asyncio
import httpx

async def download_and_verify_prd():
    """Download PRD and verify its content."""
    base_url = "http://localhost:8000"
    prd_id = "0080dd12-0240-490f-bdd3-73829502992f"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{base_url}/api/v1/prd/{prd_id}/download",
                headers={"Accept": "text/markdown"}
            )

            if response.status_code == 200:
                content = response.text

                print("=== PRD Content Verification ===")
                print(f"Content Length: {len(content)} characters")
                print(f"Content Type: {response.headers.get('content-type', '')}")
                print(f"Content-Disposition: {response.headers.get('content-disposition', '')}")

                print("\n=== First 500 characters ===")
                print(content[:500])

                print("\n=== Checking Markdown Structure ===")
                lines = content.split('\n')

                # Check for markdown structure
                has_title = any(line.startswith('#') for line in lines[:10])
                has_sections = sum(1 for line in lines if line.startswith('##')) >= 3
                has_lists = any(line.startswith('-') or line.startswith('*') for line in lines)
                has_code_blocks = any('```' in line for line in lines)

                print(f"✓ Has title: {has_title}")
                print(f"✓ Has sections: {has_sections}")
                print(f"✓ Has lists: {has_lists}")
                print(f"✓ Has code blocks: {has_code_blocks}")

                # Check for key sections
                content_lower = content.lower()
                has_executive_summary = 'executive summary' in content_lower
                has_context = 'context' in content_lower
                has_solution = 'solution' in content_lower
                has_parameters = 'parameters' in content_lower
                has_timeline = 'timeline' in content_lower

                print(f"✓ Has Executive Summary: {has_executive_summary}")
                print(f"✓ Has Context: {has_context}")
                print(f"✓ Has Solution: {has_solution}")
                print(f"✓ Has Parameters: {has_parameters}")
                print(f"✓ Has Timeline: {has_timeline}")

                print("\n=== Verification Complete ===")
                all_checks = all([
                    has_title, has_sections, has_executive_summary,
                    has_context, has_solution, has_parameters
                ])

                if all_checks:
                    print("✅ PRD content is valid and well-structured!")
                else:
                    print("❌ PRD content has issues")

                return content

            else:
                print(f"Failed to download PRD: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error downloading PRD: {e}")
            return None

if __name__ == "__main__":
    asyncio.run(download_and_verify_prd())