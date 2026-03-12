#!/usr/bin/env bash
#
# dev.sh - Start development environment for frontend, backend, or both
#
# Usage:
#   ./scripts/dev.sh [frontend|backend|all]
#
# Examples:
#   ./scripts/dev.sh              # Start both frontend and backend dev environments
#   ./scripts/dev.sh frontend     # Start only frontend dev server
#   ./scripts/dev.sh backend      # Show backend development instructions

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

cmd() {
    echo -e "${CYAN}  \$$NC $1"
}

# Determine what to run
TARGET="${1:-all}"

if [[ ! "$TARGET" =~ ^(frontend|backend|all)$ ]]; then
    error "Invalid target: $TARGET"
    echo "Usage: $0 [frontend|backend|all]"
    exit 1
fi

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Check for dependencies
check_dependencies() {
    local missing=0
    
    if [[ "$TARGET" == "backend" ]] || [[ "$TARGET" == "all" ]]; then
        if ! command -v uv &> /dev/null; then
            error "uv is not installed"
            missing=1
        fi
    fi
    
    if [[ "$TARGET" == "frontend" ]] || [[ "$TARGET" == "all" ]]; then
        if ! command -v npm &> /dev/null; then
            error "npm is not installed"
            missing=1
        fi
        if [[ ! -d "node_modules" ]]; then
            warn "node_modules not found"
            missing=1
        fi
    fi
    
    if [[ $missing -eq 1 ]]; then
        echo ""
        warn "Missing dependencies detected"
        info "Run './scripts/setup.sh $TARGET' to install dependencies"
        exit 2
    fi
}

# Initialize database if needed
init_db_if_needed() {
    if [[ ! -f "library.db" ]]; then
        info "Database not found, initializing..."
        ./scripts/db-init.sh
    fi
}

# Dev mode for backend
dev_backend() {
    echo ""
    info "Backend Development Mode"
    echo ""
    
    # Initialize DB if needed
    init_db_if_needed
    
    success "Backend is ready for development"
    echo ""
    info "The backend is a CLI tool. Here are some commands to try:"
    echo ""
    cmd "python main.py add <username> books \"I love reading 1984 and Brave New World\""
    cmd "python main.py add <username> music \"Listening to Radiohead and Pink Floyd\""
    cmd "python main.py add <username> movies \"Just watched Inception and Interstellar\""
    cmd "python main.py show <username>"
    echo ""
    info "Run tests:"
    echo ""
    cmd "python test_openlibrary.py"
    cmd "python test_book_extractor.py"
    cmd "python test_music_extractor.py"
    echo ""
    info "Interactive CLI:"
    echo ""
    cmd "python jimmy.py"
    cmd "python jimmy.py -m \"your message\""
    echo ""
}

# Dev mode for frontend
dev_frontend() {
    echo ""
    info "Starting frontend development server..."
    echo ""
    
    # Export site data first
    info "Exporting site data from database..."
    uv run python export_site_data.py
    success "Site data exported"
    
    # Start Astro dev server
    echo ""
    info "Starting Astro dev server..."
    info "Press Ctrl+C to stop"
    echo ""
    npm run dev
}

# Check dependencies first
check_dependencies

# Execute based on target
case "$TARGET" in
    backend)
        dev_backend
        ;;
    frontend)
        dev_frontend
        ;;
    all)
        dev_backend
        echo ""
        info "To start the frontend dev server, run:"
        cmd "./scripts/dev.sh frontend"
        echo ""
        ;;
esac
