import asyncio
from httpx import AsyncClient
from src.main import app
from src.core.database import get_db, Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async def test():
    # Create test database
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create tables
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
        print(f'1. Create session: {response.status_code}')
        session_id = response.json()['id']
        print(f'   Session ID: {session_id}')

        # Check initial state
        session_data = await client.get(f'/api/v1/sessions/{session_id}')
        print(f'   Initial client_info: {session_data.json()["client_info"]}')
        print(f'   Initial business_context: {session_data.json()["business_context"]}')

        # Add messages one by one and check state
        messages = [
            'My name is John Doe',
            'john@example.com',
            'TechCorp',
            'We need help with AI strategy and data analytics',
            '$75,000 budget',
            '2-3 months timeline'
        ]

        for i, msg in enumerate(messages, 1):
            r = await client.post(f'/api/v1/sessions/{session_id}/messages', json={'content': msg})
            print(f'{i+1}. Message "{msg[:30]}...": {r.status_code}')

            # Check session state after each message
            session_data = await client.get(f'/api/v1/sessions/{session_id}')
            data = session_data.json()
            print(f'   client_info: {data["client_info"]}')
            print(f'   business_context: {data["business_context"]}')
            print(f'   qualification: {data["qualification"]}')

        # Try PRD generation
        print('\n3. Attempting PRD generation...')
        response = await client.post('/api/v1/prd/generate', json={'session_id': session_id})
        print(f'   Status: {response.status_code}')
        if response.status_code != 201:
            print(f'   Error: {response.json()}')
        else:
            print(f'   Success! PRD created')

asyncio.run(test())
