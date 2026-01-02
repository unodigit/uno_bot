"""Integration tests for welcome message template functionality."""
import pytest


@pytest.mark.asyncio
async def test_create_welcome_template(client):
    """Test creating a new welcome message template."""
    template_data = {
        "name": "Standard Welcome",
        "content": "Hello! Welcome to our service. How can I help you today?",
        "description": "Standard welcome message for general use",
        "is_default": True,
        "is_active": True,
    }

    response = await client.post("/api/v1/templates", json=template_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Standard Welcome"
    assert data["content"] == "Hello! Welcome to our service. How can I help you today?"
    assert data["is_default"] is True
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_list_templates(client):
    """Test listing all templates."""
    # Create multiple templates
    await client.post("/api/v1/templates", json={
        "name": "Template 1",
        "content": "Content 1",
        "is_default": False,
    })
    await client.post("/api/v1/templates", json={
        "name": "Template 2",
        "content": "Content 2",
        "is_default": False,
    })

    # List all templates
    response = await client.get("/api/v1/templates")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_get_default_template(client):
    """Test getting the default template."""
    # Create default template
    await client.post("/api/v1/templates", json={
        "name": "Default Welcome",
        "content": "Default message",
        "is_default": True,
    })

    # Get default
    response = await client.get("/api/v1/templates/default")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Default Welcome"
    assert data["is_default"] is True


@pytest.mark.asyncio
async def test_select_template_for_industry(client):
    """Test selecting template based on industry."""
    # Create templates for different industries
    await client.post("/api/v1/templates", json={
        "name": "Healthcare Welcome",
        "content": "Welcome to healthcare consulting",
        "target_industry": "healthcare",
        "is_default": False,
    })
    await client.post("/api/v1/templates", json={
        "name": "Default Welcome",
        "content": "Default welcome message",
        "is_default": True,
    })

    # Select template for healthcare
    response = await client.post("/api/v1/templates/select", json={
        "industry": "healthcare"
    })
    assert response.status_code == 200

    data = response.json()
    assert "healthcare" in data["content"].lower() or data["name"] == "Healthcare Welcome"


@pytest.mark.asyncio
async def test_update_template(client):
    """Test updating a template."""
    # Create template
    create_response = await client.post("/api/v1/templates", json={
        "name": "Original Name",
        "content": "Original content",
    })
    template_id = create_response.json()["id"]

    # Update template
    update_response = await client.patch(f"/api/v1/templates/{template_id}", json={
        "name": "Updated Name",
        "content": "Updated content",
    })
    assert update_response.status_code == 200

    data = update_response.json()
    assert data["name"] == "Updated Name"
    assert data["content"] == "Updated content"


@pytest.mark.asyncio
async def test_delete_template(client):
    """Test deleting a template."""
    # Create template
    create_response = await client.post("/api/v1/templates", json={
        "name": "To Delete",
        "content": "This will be deleted",
    })
    template_id = create_response.json()["id"]

    # Delete template
    delete_response = await client.delete(f"/api/v1/templates/{template_id}")
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/templates/{template_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_session_uses_default_template(client):
    """Test that new sessions use the default welcome template."""
    # Create default template
    await client.post("/api/v1/templates", json={
        "name": "Test Default",
        "content": "Test welcome message from template",
        "is_default": True,
    })

    # Create session
    session_response = await client.post("/api/v1/sessions", json={
        "visitor_id": "test_visitor_123",
        "source_url": "http://example.com",
        "user_agent": "TestAgent/1.0",
    })
    assert session_response.status_code == 201

    session_data = session_response.json()
    # Check that welcome message uses template content
    messages = session_data["messages"]
    assert len(messages) > 0
    welcome_message = messages[0]
    assert welcome_message["content"] == "Test welcome message from template"
    assert welcome_message["meta_data"]["type"] == "welcome"
    assert welcome_message["meta_data"]["template_id"] is not None


@pytest.mark.asyncio
async def test_only_active_templates_are_used(client):
    """Test that inactive templates are not used for new sessions."""
    # Create inactive default template
    await client.post("/api/v1/templates", json={
        "name": "Inactive Default",
        "content": "This should not be used",
        "is_default": True,
        "is_active": False,
    })

    # Create active default template
    await client.post("/api/v1/templates", json={
        "name": "Active Default",
        "content": "This should be used",
        "is_default": True,
        "is_active": True,
    })

    # Create session
    session_response = await client.post("/api/v1/sessions", json={
        "visitor_id": "test_visitor_124",
        "source_url": "http://example.com",
        "user_agent": "TestAgent/1.0",
    })

    session_data = session_response.json()
    welcome_message = session_data["messages"][0]
    assert welcome_message["content"] == "This should be used"


@pytest.mark.asyncio
async def test_use_count_increments(client):
    """Test that template use count increments when selected."""
    # Create template
    create_response = await client.post("/api/v1/templates", json={
        "name": "Count Test",
        "content": "Count test message",
        "is_default": True,
    })
    template_id = create_response.json()["id"]
    initial_use_count = create_response.json()["use_count"]

    # Create multiple sessions
    for i in range(3):
        await client.post("/api/v1/sessions", json={
            "visitor_id": f"test_visitor_{i}",
            "source_url": "http://example.com",
            "user_agent": "TestAgent/1.0",
        })

    # Check use count
    get_response = await client.get(f"/api/v1/templates/{template_id}")
    data = get_response.json()
    assert data["use_count"] == initial_use_count + 3


@pytest.mark.asyncio
async def test_get_active_templates(client):
    """Test listing only active templates."""
    # Create mixed active/inactive templates
    await client.post("/api/v1/templates", json={
        "name": "Active 1",
        "content": "Active content 1",
        "is_active": True,
    })
    await client.post("/api/v1/templates", json={
        "name": "Inactive 1",
        "content": "Inactive content 1",
        "is_active": False,
    })
    await client.post("/api/v1/templates", json={
        "name": "Active 2",
        "content": "Active content 2",
        "is_active": True,
    })

    # Get active templates
    response = await client.get("/api/v1/templates/active")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert all(t["is_active"] for t in data)


@pytest.mark.asyncio
async def test_only_one_default_template(client):
    """Test that setting a template as default unsets others."""
    # Create first default template
    await client.post("/api/v1/templates", json={
        "name": "First Default",
        "content": "First default content",
        "is_default": True,
    })

    # Create second default template (should unset the first)
    await client.post("/api/v1/templates", json={
        "name": "Second Default",
        "content": "Second default content",
        "is_default": True,
    })

    # Get all templates
    response = await client.get("/api/v1/templates")
    templates = response.json()

    # Find both templates
    first = next(t for t in templates if t["name"] == "First Default")
    second = next(t for t in templates if t["name"] == "Second Default")

    # Only second should be default
    assert first["is_default"] is False
    assert second["is_default"] is True
