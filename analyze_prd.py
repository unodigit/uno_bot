#!/usr/bin/env python3
"""
Analyze the actual PRD structure.
"""

import asyncio
import httpx

async def analyze_prd_structure():
    """Analyze the actual PRD structure."""
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
                lines = content.split('\n')

                print("=== PRD Structure Analysis ===")
                print(f"Total lines: {len(lines)}")

                # Find all headers
                headers = []
                for i, line in enumerate(lines):
                    if line.startswith('#'):
                        headers.append((i, line.strip()))

                print(f"\nFound {len(headers)} headers:")
                for line_num, header in headers:
                    print(f"  Line {line_num:3d}: {header}")

                print("\n=== Content Analysis ===")
                content_lower = content.lower()

                # Look for specific sections
                sections = {
                    'Executive Summary': 'executive summary' in content_lower,
                    'Context': 'context' in content_lower,
                    'Solution': 'solution' in content_lower or 'recommended solution' in content_lower,
                    'Parameters': 'parameters' in content_lower or 'requirements' in content_lower,
                    'Next Steps': 'next steps' in content_lower,
                    'Timeline': 'timeline' in content_lower or 'project timeline' in content_lower,
                    'Budget': 'budget' in content_lower,
                    'Implementation': 'implementation' in content_lower,
                    'Technical Requirements': 'technical requirements' in content_lower,
                    'Success Criteria': 'success criteria' in content_lower
                }

                for section, found in sections.items():
                    status = "✓" if found else "✗"
                    print(f"  {status} {section}")

                print(f"\n=== Full Content ===")
                print(content)

            else:
                print(f"Failed to download PRD: {response.status_code}")

        except Exception as e:
            print(f"Error analyzing PRD: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_prd_structure())