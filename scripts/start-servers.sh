#!/bin/bash

# Start both frontend and backend servers for development

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting UnoBot Development Servers${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${BLUE}Shutting down servers...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Start backend
echo -e "${GREEN}Starting Backend (FastAPI) on port 8000...${NC}"
uv run uvicorn src.main:app --reload --port 8000 &
BACKEND_PID=$!

# Give backend time to start
sleep 2

# Start frontend if client directory exists
if [ -d "client" ] && [ -f "client/package.json" ]; then
    echo -e "${GREEN}Starting Frontend (Vite) on port 5173...${NC}"
    cd client
    pnpm dev &
    FRONTEND_PID=$!
    cd ..
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Development servers started!${NC}"
echo ""
echo -e "Backend API:  http://localhost:8000"
echo -e "API Docs:     http://localhost:8000/docs"
if [ -n "$FRONTEND_PID" ]; then
    echo -e "Frontend:     http://localhost:5173"
fi
echo ""
echo -e "Press Ctrl+C to stop all servers"
echo -e "${BLUE}========================================${NC}"

# Wait for all background jobs
wait
