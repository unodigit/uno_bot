import asyncio
import sys
import os

# Suppress logging
os.environ['LOGLEVEL'] = 'ERROR'

async def main():
    from httpx import AsyncClient
    from src.main import app
    from src.core.database import get_db, Base
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    # Create test database
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def get_test_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db

    async with AsyncClient(app=app, base_url='http://test') as client:
        # Create session
        response = await client.post('/api/v1/sessions', json={'visitor_id': 'test-123'})
        session_id = response.json()['id']
        print(f'Session: {session_id}')

        # Add messages
        for msg in ['My name is John Doe', 'john@example.com', 'TechCorp', 'We need help with AI', '$75k', '2 months']:
            await client.post(f'/api/v1/sessions/{session_id}/messages', json={'content': msg})

        # Check session state
        session_data = await client.get(f'/api/v1/sessions/{session_id}')
        data = session_data.json()
        print(f'client_info: {data["client_info"]}')
        print(f'business_context: {data["business_context"]}')

        # Try PRD
        response = await client.post('/api/v1/prd/generate', json={'session_id': session_id})
        print(f'PRD status: {response.status_code}')
        if response.status_code != 201:
            print(f'Error: {response.json()}')

asyncio.run(main())
