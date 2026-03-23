#!/bin/bash

# Real Estate AI Platform – Start All Services
# Usage: ./start-all.sh
# Stop:  Ctrl+C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping all servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}All stopped. Bye!${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM

# ── 1. Ollama check ───────────────────────────────────────────────────────────
echo -e "${BLUE}Checking Ollama...${NC}"
if ! ollama list &>/dev/null; then
    echo -e "${RED}Ollama not running. Starting...${NC}"
    ollama serve &>/dev/null &
    sleep 3
fi
echo -e "${GREEN}✓ Ollama ready${NC}"

# ── 2. Backend ────────────────────────────────────────────────────────────────
echo -e "${BLUE}Starting Backend...${NC}"
cd "$SCRIPT_DIR/react-version/backend"
source venv/bin/activate
python3 server.py > /tmp/re-backend.log 2>&1 &
BACKEND_PID=$!
sleep 2
curl -sf http://localhost:8000/ > /dev/null && echo -e "${GREEN}✓ Backend ready  → http://localhost:8000${NC}" \
    || echo -e "${RED}✗ Backend failed (check /tmp/re-backend.log)${NC}"

# ── 3. Frontend ───────────────────────────────────────────────────────────────
echo -e "${BLUE}Starting Frontend...${NC}"
cd "$SCRIPT_DIR/react-version/frontend"
source ~/.nvm/nvm.sh 2>/dev/null && nvm use node &>/dev/null
npm run dev > /tmp/re-frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 5
curl -sf http://localhost:5173/ > /dev/null && echo -e "${GREEN}✓ Frontend ready → http://localhost:5173${NC}" \
    || echo -e "${RED}✗ Frontend failed (check /tmp/re-frontend.log)${NC}"

# ── 4. Summary ────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  All services running!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  App      → http://localhost:5173"
echo -e "  API      → http://localhost:8000"
echo -e "  API Docs → http://localhost:8000/docs"
echo -e "  MCP      → run separately for Claude Desktop"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}  Press Ctrl+C to stop${NC}"
echo ""

wait $BACKEND_PID $FRONTEND_PID
