#!/bin/bash

# UnoBot - Development Setup Script (without Docker)
# This version skips Docker/PostgreSQL/Redis and uses SQLite for development

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  UnoBot Dev Setup (SQLite Mode)${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check for required tools (excluding docker)
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} $1 found"
}

echo -e "${YELLOW}Checking required tools...${NC}"
check_command "python3"
check_command "node"
check_command "pnpm"
check_command "uv"

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}✓${NC} Python version: $PYTHON_VERSION"
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓${NC} Node version: $NODE_VERSION"

echo ""
echo -e "${YELLOW}Setting up environment...${NC}"

# Create .env file with SQLite
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file (SQLite mode)...${NC}"
    cat > .env << 'ENVEOF'
# Environment Configuration for UnoBot (Development)
NODE_ENV=development
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
BACKEND_PORT=8000
FRONTEND_PORT=5173

# Using SQLite for development (no PostgreSQL required)
DATABASE_URL=sqlite+aiosqlite:///./unobot.db
REDIS_URL=redis://localhost:6379

# Anthropic AI (Claude)
ANTHROPIC_API_KEY=

# Other configs (not needed for initial dev)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
SENDGRID_API_KEY=
SECRET_KEY=dev-secret-key-change-in-production
SESSION_EXPIRY_DAYS=7
ENVEOF
    echo -e "${GREEN}✓${NC} Created .env file"
else
    echo -e "${GREEN}✓${NC} .env file exists"
fi

# Check for API key
if [ -f /tmp/api-key ]; then
    echo -e "${YELLOW}Found API key at /tmp/api-key${NC}"
    API_KEY=$(cat /tmp/api-key)
    sed -i "s/ANTHROPIC_API_KEY=$/ANTHROPIC_API_KEY=$API_KEY/" .env
    echo -e "${GREEN}✓${NC} Added API key to .env"
fi

echo ""
echo -e "${YELLOW}Installing Python dependencies...${NC}"
uv sync

echo ""
echo -e "${YELLOW}Creating frontend project...${NC}"
if [ ! -d "client" ]; then
    pnpm create vite client --template react-ts
    echo -e "${GREEN}✓${NC} Created Vite React TypeScript project"

    cd client
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    pnpm add

    # Install required dependencies
    pnpm add @tanstack/react-query zustand socket.io-client lucide-react
    pnpm add framer-motion react-markdown
    pnpm add -D tailwindcss postcss autoprefixer @types/node

    # Initialize TailwindCSS
    pnpm exec tailwindcss init -p

    cd ..
    echo -e "${GREEN}✓${NC} Frontend created"
else
    echo -e "${GREEN}✓${NC} Client directory exists"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your ANTHROPIC_API_KEY"
echo "  2. Run: ./scripts/start-servers.sh"
echo ""
