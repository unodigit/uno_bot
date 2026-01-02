"""Test README completeness (Feature #139)

Tests that verify:
- Feature #139: README contains complete setup instructions
"""

from pathlib import Path


class TestReadmeComplete:
    """Test README completeness"""

    def test_readme_complete(self):
        """Verify README contains complete setup instructions (Feature #139)

        Steps:
        1. Read README.md
        2. Verify prerequisites listed
        3. Verify setup steps documented
        4. Verify environment variables documented
        """
        print("\n=== Feature #139: README Complete Setup Instructions ===")

        readme_path = Path("README.md")
        assert readme_path.exists(), "README.md not found"

        content = readme_path.read_text()

        # Test 1: Verify prerequisites section
        print("\n--- Test 1: Prerequisites Section ---")
        assert "## Quick Start" in content or "## Prerequisites" in content, \
            "Quick Start or Prerequisites section not found"

        required_prereqs = [
            "Python",
            "Node.js",
            "pnpm",
            "uv"
        ]

        found_prereqs = []
        for prereq in required_prereqs:
            if prereq in content:
                found_prereqs.append(prereq)
                print(f"  ✓ {prereq} mentioned")

        assert len(found_prereqs) >= 3, f"Missing prerequisites: found {found_prereqs}"

        # Test 2: Verify installation steps
        print("\n--- Test 2: Installation Steps ---")
        assert "## Installation" in content or "### Installation" in content, \
            "Installation section not found"

        # Check for common installation commands
        install_keywords = [
            "git clone",
            "init.sh",
            "pip install",
            "pnpm install",
            "npm install"
        ]

        found_install = False
        for keyword in install_keywords:
            if keyword in content:
                print(f"  ✓ Found '{keyword}' instruction")
                found_install = True

        assert found_install, "No installation instructions found"

        # Test 3: Verify environment variables documented
        print("\n--- Test 3: Environment Variables ---")
        env_section_found = False

        # Look for environment variables section
        if "Environment" in content and "variable" in content.lower():
            env_section_found = True
            print("  ✓ Environment variables section found")

        # Check for required env vars
        required_env_vars = [
            "ANTHROPIC_API_KEY",
            "DATABASE_URL",
        ]

        for var in required_env_vars:
            if var in content:
                print(f"  ✓ {var} documented")

        assert env_section_found or any(var in content for var in required_env_vars), \
            "Environment variables not documented"

        # Test 4: Verify project structure documented
        print("\n--- Test 4: Project Structure ---")
        if "## Project Structure" in content or "## Directory" in content:
            print("  ✓ Project structure section found")
            assert "src/" in content or "client/" in content, \
                "Project structure incomplete"
        else:
            print("  (Project structure optional)")

        # Test 5: Verify API documentation section
        print("\n--- Test 5: API Documentation ---")
        if "## API" in content or "API Documentation" in content:
            print("  ✓ API documentation section found")

        # Test 6: Verify development instructions
        print("\n--- Test 6: Development Instructions ---")
        if "## Development" in content or "## Running" in content:
            print("  ✓ Development section found")

            # Check for test commands
            if "pytest" in content or "test" in content.lower():
                print("  ✓ Testing instructions found")

        # Test 7: Verify key sections exist
        print("\n--- Test 7: Key Sections ---")
        required_sections = [
            ("## Features", "Features"),
            ("## Tech Stack", "Tech Stack"),
        ]

        for section, name in required_sections:
            if section in content:
                print(f"  ✓ {name} section found")
            else:
                print(f"  ⚠ {name} section not found (optional)")

        # Test 8: Check for badges or status indicators (optional)
        print("\n--- Test 8: README Quality ---")
        lines = content.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]

        print(f"  ✓ README has {len(non_empty_lines)} lines")
        print(f"  ✓ README has {len(content)} characters")

        assert len(non_empty_lines) > 50, "README seems too short"
        assert len(content) > 2000, "README seems incomplete"

        # Test 9: Verify proper Markdown formatting
        print("\n--- Test 9: Markdown Formatting ---")
        code_blocks = content.count('```')
        print(f"  ✓ Found {code_blocks // 2} code blocks")

        headers = len([l for l in lines if l.startswith('#')])
        print(f"  ✓ Found {headers} headers")

        # Test 10: Verify contact or support section
        print("\n--- Test 10: Contact/Support ---")
        if "## Support" in content or "## Contributing" in content or "## License" in content:
            print("  ✓ Support/Contributing/License section found")

        print("\n✅ Feature #139: README contains complete setup instructions")
        return True


if __name__ == "__main__":
    test = TestReadmeComplete()
    test.test_readme_complete()
