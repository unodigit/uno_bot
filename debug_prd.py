import asyncio
from httpx import AsyncClient
from src.main import app
from src.core.database import get_db
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async def test():
    # Create test database
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Import models and create tables
    from src.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Override get_db
    async def get_test_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db

    async with AsyncClient(app=app, base_url='http://test') as client:
        # Create session
        response = await client.post('/api/v1/sessions', json={'visitor_id': 'test-123'})
        print('Create session:', response.status_code)
        session_id = response.json()['id']

        # Add messages
        messages = [
            'My name is John Doe',
            'john@example.com',
            'TechCorp',
            'Need help with AI strategy',
            '$75,000 budget',
            '2-3 months timeline'
        ]

        for msg in messages:
            r = await client.post(f'/api/v1/sessions/{session_id}/messages', json={'content': msg})
            print(f'Message: {msg[:20]}... -> {r.status_code}')

        # Try PRD generation
        response = await client.post('/api/v1/prd/generate', json={'session_id': session_id})
        print('PRD Generate:', response.status_code)
        if response.status_code != 201:
            print('Error:', response.json())

asyncio.run(test())
