"""Integration tests for PRD generation, download, and preview APIs.

Tests for Features:
- 127: POST /api/v1/sessions/{id}/prd generates document
- 128: GET /api/v1/prd/{id}/download returns markdown file
- 129: GET /api/v1/prd/{id}/preview returns PRD preview
"""
import uuid
import pytest
from src.services.session_service import SessionService
from src.schemas.session import SessionCreate
from src.services.expert_service import ExpertService
from src.schemas.expert import ExpertCreate


@pytest.mark.asyncio
async def test_prd_generation_with_complete_session(client, sample_visitor_id: str):
    """Test POST /api/v1/prd/generate creates PRD for qualified session."""
    # Create a session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    # Simulate a complete conversation by adding messages
    # This mimics what happens during a real conversation
    messages = [
        "My name is John Doe",
        "My email is john@example.com",
        "I work at TechCorp",
        "We need help with AI strategy and data analytics",
        "Budget is around $75,000",
        "Timeline is 2-3 months",
    ]

    for msg in messages:
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": msg},
        )

    # Now generate PRD
    response = await client.post(
        "/api/v1/prd/generate",
        json={"session_id": session_id},
    )

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["session_id"] == session_id
    assert data["version"] == 1
    assert "content_markdown" in data
    assert len(data["content_markdown"]) > 0
    assert data["client_name"] == "John Doe"
    assert data["client_company"] == "Techcorp"  # title() converts TechCorp -> Techcorp
    assert data["storage_url"] == f"/api/v1/prd/{data['id']}/download"
    assert data["download_count"] == 0


@pytest.mark.asyncio
async def test_prd_generation_fails_without_name(client, sample_visitor_id: str):
    """Test PRD generation fails if client name is missing."""
    # Create a session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    # Add only some messages (missing name)
    await client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"content": "We need help with AI"},
    )

    # Try to generate PRD
    response = await client.post(
        "/api/v1/prd/generate",
        json={"session_id": session_id},
    )

    assert response.status_code == 400
    assert "name" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_prd_generation_fails_without_challenges(client, sample_visitor_id: str):
    """Test PRD generation fails if business challenges are missing."""
    # Create a session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    # Add messages with name but no challenges
    await client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"content": "My name is John Doe"},
    )

    # Try to generate PRD
    response = await client.post(
        "/api/v1/prd/generate",
        json={"session_id": session_id},
    )

    assert response.status_code == 400
    assert "challenges" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_prd_generation_fails_for_nonexistent_session(client):
    """Test PRD generation fails for non-existent session."""
    fake_id = str(uuid.uuid4())
    response = await client.post(
        "/api/v1/prd/generate",
        json={"session_id": fake_id},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_prd_download_returns_markdown_file(client, sample_visitor_id: str):
    """Test GET /api/v1/prd/{id}/download returns markdown file."""
    # Create and populate session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    # Add messages
    messages = [
        "My name is Jane Smith",
        "jane@example.com",
        "Acme Corp",
        "Need help with cloud migration",
        "$100,000 budget",
        "6 months timeline",
    ]

    for msg in messages:
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": msg},
        )

    # Generate PRD
    prd_response = await client.post(
        "/api/v1/prd/generate",
        json={"session_id": session_id},
    )
    prd_id = prd_response.json()["id"]

    # Download PRD
    response = await client.get(f"/api/v1/prd/{prd_id}/download")

    assert response.status_code == 200

    # Check headers
    headers = response.headers
    assert "text/markdown" in headers.get("content-type", "")
    assert "attachment" in headers.get("content-disposition", "")
    assert ".md" in headers.get("content-disposition", "")

    # Check content
    content = response.content.decode("utf-8")
    assert len(content) > 0
    assert "# " in content or "## " in content  # Markdown heading


@pytest.mark.asyncio
async def test_prd_download_increments_download_count(client, sample_visitor_id: str):
    """Test PRD download increments download count."""
    # Create and populate session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    for msg in ["My name is Test", "Test Corp", "Need help", "$50k", "3 months"]:
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": msg},
        )

    # Generate PRD
    prd_response = await client.post(
        "/api/v1/prd/generate",
        json={"session_id": session_id},
    )
    prd_id = prd_response.json()["id"]

    # Download once
    await client.get(f"/api/v1/prd/{prd_id}/download")

    # Check count increased
    get_response = await client.get(f"/api/v1/prd/{prd_id}")
    assert get_response.json()["download_count"] == 1

    # Download again
    await client.get(f"/api/v1/prd/{prd_id}/download")

    # Check count increased again
    get_response = await client.get(f"/api/v1/prd/{prd_id}")
    assert get_response.json()["download_count"] == 2


@pytest.mark.asyncio
async def test_prd_download_not_found(client):
    """Test PRD download returns 404 for non-existent PRD."""
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/prd/{fake_id}/download")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_prd_preview_returns_data(client, sample_visitor_id: str):
    """Test GET /api/v1/prd/{id}/preview returns PRD preview."""
    # Create and populate session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    messages = [
        "My name is Preview Test",
        "preview@example.com",
        "Preview Corp",
        "Need analytics solution",
        "$80,000 budget",
        "4 months timeline",
    ]

    for msg in messages:
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": msg},
        )

    # Generate PRD
    prd_response = await client.post(
        "/api/v1/prd/generate",
        json={"session_id": session_id},
    )
    prd_id = prd_response.json()["id"]

    # Get preview
    response = await client.get(f"/api/v1/prd/{prd_id}/preview")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == prd_id
    assert "filename" in data
    assert ".md" in data["filename"]
    assert "preview_text" in data
    assert len(data["preview_text"]) > 0
    assert data["version"] == 1
    assert "created_at" in data


@pytest.mark.asyncio
async def test_prd_preview_not_found(client):
    """Test PRD preview returns 404 for non-existent PRD."""
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/prd/{fake_id}/preview")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_prd_preview_truncates_long_content(client, sample_visitor_id: str):
    """Test PRD preview truncates long content to 200 chars."""
    # Create and populate session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    for msg in ["My name is Test", "Test Corp", "Need help", "$50k", "3 months"]:
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": msg},
        )

    # Generate PRD
    prd_response = await client.post(
        "/api/v1/prd/generate",
        json={"session_id": session_id},
    )
    prd_id = prd_response.json()["id"]

    # Get preview
    response = await client.get(f"/api/v1/prd/{prd_id}/preview")
    data = response.json()

    # Preview text should be max 200 chars
    assert len(data["preview_text"]) <= 200
    # If truncated, should end with "..."
    if len(data["preview_text"]) == 200:
        assert data["preview_text"].endswith("...")


@pytest.mark.asyncio
async def test_prd_get_by_id(client, sample_visitor_id: str):
    """Test GET /api/v1/prd/{id} retrieves PRD by ID."""
    # Create and populate session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    for msg in ["My name is GetTest", "Get Corp", "Need help", "$50k", "3 months"]:
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": msg},
        )

    # Generate PRD
    prd_response = await client.post(
        "/api/v1/prd/generate",
        json={"session_id": session_id},
    )
    prd_id = prd_response.json()["id"]

    # Get PRD by ID
    response = await client.get(f"/api/v1/prd/{prd_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == prd_id
    assert data["session_id"] == session_id
    assert data["client_name"] == "GetTest"
    assert data["client_company"] == "Get Corp"
    assert "content_markdown" in data
    assert "conversation_summary" in data


@pytest.mark.asyncio
async def test_prd_get_not_found(client):
    """Test GET /api/v1/prd/{id} returns 404 for non-existent PRD."""
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/prd/{fake_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_prd_version_tracking(client, sample_visitor_id: str):
    """Test that PRD version tracking works correctly."""
    # Create and populate session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    for msg in ["My name is VersionTest", "Version Corp", "Need help", "$50k", "3 months"]:
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": msg},
        )

    # Generate first PRD
    prd_response = await client.post(
        "/api/v1/prd/generate",
        json={"session_id": session_id},
    )
    assert prd_response.json()["version"] == 1

    # Regenerate with feedback
    prd_id = prd_response.json()["id"]
    regen_response = await client.post(
        f"/api/v1/prd/{prd_id}/regenerate",
        json={"feedback": "Make it more detailed"},
    )

    assert regen_response.status_code == 201
    assert regen_response.json()["version"] == 2
    assert regen_response.json()["id"] != prd_id  # New PRD with new ID


@pytest.mark.asyncio
async def test_prd_generation_with_summary(client, sample_visitor_id: str):
    """Test PRD generation with conversation summary."""
    # Create and populate session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    for msg in ["My name is SummaryTest", "Summary Corp", "Need help", "$50k", "3 months"]:
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": msg},
        )

    # Generate summary first
    summary_response = await client.post(
        "/api/v1/prd/generate-summary",
        json={"session_id": session_id},
    )
    assert summary_response.status_code == 200
    summary = summary_response.json()["summary"]
    assert len(summary) > 0

    # Approve and generate PRD
    prd_response = await client.post(
        "/api/v1/prd/approve-summary-and-generate-prd",
        json={"session_id": session_id, "approve": True, "summary": summary},
    )

    assert prd_response.status_code == 201
    data = prd_response.json()
    assert data["conversation_summary"] == summary
    assert data["version"] == 1


@pytest.mark.asyncio
async def test_prd_summary_rejection_regenerates(client, sample_visitor_id: str):
    """Test that rejecting summary regenerates a new one."""
    # Create and populate session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    for msg in ["My name is RejectTest", "Reject Corp", "Need help", "$50k", "3 months"]:
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": msg},
        )

    # Generate first summary
    summary1_response = await client.post(
        "/api/v1/prd/generate-summary",
        json={"session_id": session_id},
    )
    summary1 = summary1_response.json()["summary"]

    # Reject and request new summary
    reject_response = await client.post(
        "/api/v1/prd/approve-summary-and-generate-prd",
        json={"session_id": session_id, "approve": False},
    )

    # Should return a new summary response, not a PRD
    assert reject_response.status_code == 200
    assert "summary" in reject_response.json()
    assert "id" not in reject_response.json()  # Not a PRD response
