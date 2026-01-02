# UnoBot - AI Business Consultant & Appointment Booking System

An AI-powered business consultant chatbot that transforms website visitors into qualified leads by conducting intelligent business discovery conversations, automatically generating Project Requirements Documents (PRDs), and seamlessly booking appointments with UnoDigit professionals.

## Features

- **AI-Powered Chat Widget**: Floating chat button with real-time streaming responses
- **Intelligent Conversations**: DeepAgents-powered discovery and qualification
- **PRD Generation**: Automatic Project Requirements Document creation
- **Expert Matching**: Smart matching with UnoDigit professionals based on needs
- **Calendar Integration**: Google Calendar integration for appointment booking
- **Email Notifications**: Automated confirmations and reminders via SendGrid
- **Session Management**: Persistent sessions with 7-day duration
- **Admin Dashboard**: Expert management and analytics

## Tech Stack

### Frontend
- **Framework**: React 18+ with Vite and TypeScript
- **Styling**: TailwindCSS 3.x with custom design tokens
- **State Management**: Zustand for client state, TanStack Query for server state
- **Real-time**: Socket.io Client for WebSocket communication
- **UI Components**: Radix UI primitives, Lucide React icons, Framer Motion

### Backend
- **Runtime**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL 15 with SQLAlchemy ORM
- **Cache**: Redis 7 for sessions and caching
- **AI Framework**: DeepAgents (langchain-ai/deepagents)
- **LLM**: Claude Sonnet 4.5 via Anthropic API
- **Calendar**: Google Calendar API with OAuth 2.0
- **Email**: SendGrid for transactional emails

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- pnpm (package manager)
- uv (Python package manager)
- Docker & Docker Compose
- Google Cloud project with Calendar API enabled
- SendGrid account
- Anthropic API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd unobot
```

2. Run the setup script:
```bash
chmod +x init.sh
./init.sh
```

3. Configure environment variables:
```bash
# Edit .env with your API keys
nano .env
```

Required environment variables:
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret
- `SENDGRID_API_KEY`: SendGrid API key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

4. Start the development servers:

**Backend:**
```bash
uv run uvicorn src.main:app --reload --port 8000
```

**Frontend:**
```bash
cd client
pnpm dev
```

## Project Structure

```
unobot/
├── src/                       # Backend source code
│   ├── api/                  # API routes and endpoints
│   │   ├── routes/           # Route handlers
│   │   └── dependencies.py   # FastAPI dependencies
│   ├── models/               # SQLAlchemy database models
│   ├── services/             # Business logic layer
│   ├── schemas/              # Pydantic schemas
│   ├── utils/                # Utility functions
│   ├── core/                 # Core config and database
│   ├── static/               # Static assets
│   ├── templates/            # Jinja2 templates
│   └── main.py               # FastAPI application
│
├── client/                    # Frontend React application
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── stores/           # Zustand stores
│   │   ├── api/              # API client
│   │   └── types/            # TypeScript types
│   └── ...
│
├── tests/                     # Test files
│   ├── e2e/                  # End-to-end tests (Playwright)
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── fixtures/             # Test data
│
├── scripts/                   # Utility scripts
├── reports/                   # Generated reports
├── docs/                      # Documentation
├── logs/                      # Log files
│
├── feature_list.json          # Feature tracking (200+ test cases)
├── app_spec.txt               # Application specification
├── init.sh                    # Setup script
├── pyproject.toml             # Python dependencies
└── docker-compose.yml         # Docker services
```

## API Documentation

Once the backend is running, access the API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Key Endpoints

- `POST /api/v1/sessions` - Create new chat session
- `POST /api/v1/sessions/{id}/messages` - Send message
- `GET /api/v1/sessions/{id}` - Get session history
- `POST /api/v1/sessions/{id}/prd` - Generate PRD
- `GET /api/v1/experts/{id}/availability` - Get expert availability
- `POST /api/v1/sessions/{id}/bookings` - Create booking

### WebSocket

Connect to `/ws/chat` for real-time chat with streaming responses.

Events:
- `send_message`: Send a chat message
- `message_stream`: Receive streaming response
- `prd_ready`: PRD generation complete
- `booking_confirmed`: Booking confirmed

## Development

### Running Tests

```bash
# Backend tests
uv run pytest

# With coverage
uv run pytest --cov=src

# E2E tests
uv run playwright test
```

### Linting

```bash
# Python
uv run ruff check src tests
uv run mypy src

# TypeScript (in client directory)
pnpm lint
```

### Database Migrations

```bash
# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1
```

## Design System

### Colors
- **Primary**: #2563EB (UnoDigit Blue)
- **Secondary**: #10B981 (Success Green)
- **Error**: #EF4444
- **Background**: #FFFFFF
- **Surface**: #F3F4F6
- **Text**: #1F2937

### Typography
- **Font**: Inter, -apple-system, sans-serif
- **Sizes**: 14px (SM), 16px (Base), 18px (LG)

## Contributing

1. Create a feature branch
2. Make changes following the code style
3. Write tests for new functionality
4. Run all tests and linting
5. Submit a pull request

## License

Proprietary - UnoDigit

## Support

For support, contact the UnoDigit development team.
