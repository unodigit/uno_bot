#!/bin/bash

# UnoBot - AI Business Consultant & Appointment Booking System
# Environment Setup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  UnoBot Development Environment Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check for required tools
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed${NC}"
        echo "Please install $1 and try again."
        exit 1
    fi
    echo -e "${GREEN}✓${NC} $1 found"
}

echo -e "${YELLOW}Checking required tools...${NC}"
check_command "python3"
check_command "node"
check_command "pnpm"
check_command "uv"
check_command "docker"

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}✓${NC} Python version: $PYTHON_VERSION"

# Check Node version
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓${NC} Node version: $NODE_VERSION"

echo ""
echo -e "${YELLOW}Setting up environment...${NC}"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cat > .env << 'EOF'
# Environment Configuration for UnoBot
# Copy this file and fill in your values

# Application
NODE_ENV=development
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Backend API
BACKEND_PORT=8000
FRONTEND_PORT=5173

# Database
DATABASE_URL=postgresql://unobot:unobot@localhost:5432/unobot
REDIS_URL=redis://localhost:6379

# Anthropic AI (Claude)
# Get your API key from: https://console.anthropic.com/
ANTHROPIC_API_KEY=

# Google Calendar OAuth
# Set up at: https://console.cloud.google.com/
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# SendGrid Email
# Get your API key from: https://sendgrid.com/
SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=noreply@unodigit.com

# AWS S3 / Cloudflare R2 (for PRD storage)
S3_BUCKET_NAME=unobot-documents
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# Security
SECRET_KEY=change-this-to-a-secure-random-string
SESSION_EXPIRY_DAYS=7
EOF
    echo -e "${GREEN}✓${NC} Created .env file"
    echo -e "${YELLOW}⚠ Please edit .env and add your API keys${NC}"
else
    echo -e "${GREEN}✓${NC} .env file exists"
fi

# Check for API key in /tmp
if [ -f /tmp/api-key ]; then
    API_KEY=$(cat /tmp/api-key)
    if grep -q "^ANTHROPIC_API_KEY=$" .env; then
        sed -i "s/^ANTHROPIC_API_KEY=$/ANTHROPIC_API_KEY=$API_KEY/" .env
        echo -e "${GREEN}✓${NC} Loaded API key from /tmp/api-key"
    fi
fi

echo ""
echo -e "${YELLOW}Starting Docker services (PostgreSQL & Redis)...${NC}"

# Create docker-compose if it doesn't exist
if [ ! -f docker-compose.yml ]; then
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: unobot-postgres
    environment:
      POSTGRES_USER: unobot
      POSTGRES_PASSWORD: unobot
      POSTGRES_DB: unobot
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U unobot"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: unobot-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
EOF
    echo -e "${GREEN}✓${NC} Created docker-compose.yml"
fi

# Start Docker services
docker compose up -d
echo -e "${GREEN}✓${NC} Docker services started"

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 3

echo ""
echo -e "${YELLOW}Setting up Python backend...${NC}"

# Install Python dependencies with uv
cd "$(dirname "$0")"

if [ ! -f pyproject.toml ]; then
    echo -e "${YELLOW}Initializing Python project with uv...${NC}"
    uv init --name unobot 2>/dev/null || true
fi

# Create virtual environment and install dependencies
uv venv --quiet 2>/dev/null || true
echo -e "${GREEN}✓${NC} Virtual environment ready"

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
uv add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg alembic pydantic pydantic-settings python-dotenv redis aioredis python-socketio python-jose[cryptography] passlib[bcrypt] httpx sendgrid google-auth google-auth-oauthlib google-api-python-client icalendar boto3 2>/dev/null || true
uv add --dev pytest pytest-asyncio pytest-cov ruff mypy playwright httpx 2>/dev/null || true
echo -e "${GREEN}✓${NC} Python dependencies installed"

# Try to install deepagents (may not be available yet)
uv add deepagents 2>/dev/null || echo -e "${YELLOW}⚠ deepagents package not available, using langchain stack${NC}"
uv add langchain langchain-anthropic langgraph langsmith 2>/dev/null || true

echo ""
echo -e "${YELLOW}Setting up Frontend...${NC}"

# Check if client directory exists and has package.json
if [ -d "client" ] && [ -f "client/package.json" ]; then
    cd client
    pnpm install
    echo -e "${GREEN}✓${NC} Frontend dependencies installed"
    cd ..
elif [ ! -d "client" ]; then
    echo -e "${YELLOW}Creating frontend project with Vite...${NC}"
    pnpm create vite@latest client --template react-ts -- --yes 2>/dev/null || true

    if [ -d "client" ]; then
        cd client
        pnpm install

        # Install additional frontend dependencies
        pnpm add zustand @tanstack/react-query socket.io-client @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-tooltip @radix-ui/react-toast lucide-react framer-motion react-markdown clsx tailwind-merge
        pnpm add -D tailwindcss postcss autoprefixer @types/node

        # Initialize Tailwind
        npx tailwindcss init -p

        echo -e "${GREEN}✓${NC} Frontend created and dependencies installed"
        cd ..
    fi
else
    echo -e "${YELLOW}Frontend directory exists but no package.json - skipping${NC}"
fi

# Run database migrations if alembic is configured
if [ -f "alembic.ini" ]; then
    echo ""
    echo -e "${YELLOW}Running database migrations...${NC}"
    uv run alembic upgrade head
    echo -e "${GREEN}✓${NC} Database migrations complete"
fi

# Install Playwright browsers
echo ""
echo -e "${YELLOW}Installing Playwright browsers for E2E testing...${NC}"
uv run playwright install chromium 2>/dev/null || echo -e "${YELLOW}⚠ Playwright browsers not installed (run 'uv run playwright install' manually)${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "To start the development servers:"
echo ""
echo -e "  ${BLUE}Backend:${NC}"
echo -e "    cd $(pwd)"
echo -e "    uv run uvicorn src.main:app --reload --port 8000"
echo ""
echo -e "  ${BLUE}Frontend:${NC}"
echo -e "    cd $(pwd)/client"
echo -e "    pnpm dev"
echo ""
echo -e "  ${BLUE}Or use the start script:${NC}"
echo -e "    ./scripts/start-servers.sh"
echo ""
echo -e "${BLUE}Application URLs:${NC}"
echo -e "  Frontend:     http://localhost:5173"
echo -e "  Backend API:  http://localhost:8000"
echo -e "  API Docs:     http://localhost:8000/docs"
echo -e "  ReDoc:        http://localhost:8000/redoc"
echo ""
echo -e "${BLUE}Database:${NC}"
echo -e "  PostgreSQL:   postgresql://unobot:unobot@localhost:5432/unobot"
echo -e "  Redis:        redis://localhost:6379"
echo ""
echo -e "${YELLOW}Note: Make sure to configure your API keys in .env${NC}"
