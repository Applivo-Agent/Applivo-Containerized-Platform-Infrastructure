#!/bin/bash
# ── Applivo Local Development Setup ─────────────────────────
# Usage: ./scripts/dev-setup.sh [up|down|logs|shell|test]
# ─────────────────────────────────────────────────────────────

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

COMPOSE_FILE="docker-compose.dev.yml"
ENV_DEV=".env.development"
ENV_PROD=".env"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Applivo Local Development Environment${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
}

check_env() {
    if [ ! -f "$ENV_DEV" ]; then
        echo -e "${RED}ERROR: $ENV_DEV not found!${NC}"
        echo "Run this script from the project root."
        exit 1
    fi
}

cmd_up() {
    print_header
    check_env
    
    echo -e "${GREEN}▶ Starting Applivo in DEVELOPMENT mode...${NC}"
    echo ""
    echo -e "${YELLOW}Services that will start:${NC}"
    echo "  • PostgreSQL  → localhost:5433"
    echo "  • Redis       → localhost:6380"
    echo "  • Backend API → localhost:8000 (with hot reload)"
    echo "  • Celery Std  → background worker (analysis, notifications)"
    echo "  • Celery Browser → background worker (scraping, applying) + VNC 5900"
    echo "  • Scheduler   → Celery Beat (periodic tasks)"
    echo "  • Flower      → localhost:5555 (task monitoring)"
    echo ""
    echo -e "${YELLOW}Quick Links:${NC}"
    echo "  API Docs:    http://localhost:8000/api/docs"
    echo "  Health:      http://localhost:8000/health"
    echo "  Flower UI:   http://localhost:5555"
    echo "  VNC Viewer:  localhost:5900 (for watching browser automation)"
    echo ""
    
    # Ensure storage dirs exist
    mkdir -p storage/resumes storage/invoices storage/screenshots storage/logs
    
    # Build and start
    docker compose -f "$COMPOSE_FILE" up --build -d
    
    echo ""
    echo -e "${GREEN}✅ All services started!${NC}"
    echo ""
    echo -e "${YELLOW}Useful commands:${NC}"
    echo "  ./scripts/dev-setup.sh logs     → View all logs"
    echo "  ./scripts/dev-setup.sh logs api → View backend logs only"
    echo "  ./scripts/dev-setup.sh shell    → Open backend container shell"
    echo "  ./scripts/dev-setup.sh test     → Run a quick health check"
    echo "  ./scripts/dev-setup.sh down     → Stop all services"
    echo ""
}

cmd_down() {
    echo -e "${YELLOW}▶ Stopping all development services...${NC}"
    docker compose -f "$COMPOSE_FILE" down
    echo -e "${GREEN}✅ Services stopped.${NC}"
}

cmd_logs() {
    local service="$1"
    if [ -n "$service" ]; then
        docker compose -f "$COMPOSE_FILE" logs -f "$service"
    else
        docker compose -f "$COMPOSE_FILE" logs -f
    fi
}

cmd_shell() {
    echo -e "${YELLOW}▶ Opening shell in backend container...${NC}"
    docker compose -f "$COMPOSE_FILE" exec backend bash
}

cmd_test() {
    echo -e "${YELLOW}▶ Running health checks...${NC}"
    
    # Wait a moment for services to be ready
    sleep 2
    
    # Test backend
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}  ✓ Backend API responding${NC}"
    else
        echo -e "${RED}  ✗ Backend API not responding (wait a few seconds and retry)${NC}"
    fi
    
    # Test Flower
    if curl -s http://localhost:5555 > /dev/null; then
        echo -e "${GREEN}  ✓ Flower UI responding${NC}"
    else
        echo -e "${RED}  ✗ Flower UI not responding${NC}"
    fi
    
    # Check if containers are running
    echo ""
    echo -e "${YELLOW}Running containers:${NC}"
    docker compose -f "$COMPOSE_FILE" ps
}

cmd_vnc() {
    echo -e "${YELLOW}▶ VNC connection info:${NC}"
    echo "  Host: localhost"
    echo "  Port: 5900"
    echo "  No password required"
    echo ""
    echo "  Open VNC Viewer → localhost:5900"
    echo "  Or use SSH tunnel: ssh -L 5900:localhost:5900 <user>@<host>"
}

cmd_help() {
    print_header
    echo ""
    echo "Usage: ./scripts/dev-setup.sh <command>"
    echo ""
    echo "Commands:"
    echo "  up       Start all development services"
    echo "  down     Stop all development services"
    echo "  logs     View logs (optionally: logs <service>)"
    echo "  shell    Open a shell in the backend container"
    echo "  test     Run health checks"
    echo "  vnc      Show VNC connection instructions"
    echo "  help     Show this help message"
    echo ""
    echo "Services for logs: backend, worker-standard, worker-browsing, scheduler, flower, database, redis"
}

# Main
COMMAND="${1:-help}"
shift || true

case "$COMMAND" in
    up)
        cmd_up
        ;;
    down)
        cmd_down
        ;;
    logs)
        cmd_logs "$1"
        ;;
    shell)
        cmd_shell
        ;;
    test)
        cmd_test
        ;;
    vnc)
        cmd_vnc
        ;;
    help|*)
        cmd_help
        ;;
esac
