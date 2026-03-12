#!/usr/bin/env bash
#
# setup.sh - Install dependencies for frontend, backend, or both
#
# Usage:
#   ./scripts/setup.sh [frontend|backend|all]
#
# Examples:
#   ./scripts/setup.sh              # Install both frontend and backend dependencies
#   ./scripts/setup.sh frontend     # Install only frontend dependencies
#   ./scripts/setup.sh backend      # Install only backend dependencies

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
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

# Determine what to install
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

echo ""
info "Setting up server-library dependencies..."
echo ""

# Setup backend
setup_backend() {
    info "Setting up backend (Python dependencies)..."
    
    # Check if uv is installed
    if ! command -v uv &> /dev/null; then
        warn "uv is not installed"
        info "Installing uv via pip..."
        
        if command -v pip3 &> /dev/null; then
            pip3 install uv
        elif command -v pip &> /dev/null; then
            pip install uv
        else
            error "Neither pip nor pip3 found. Please install Python and pip first."
            exit 2
        fi
    fi
    
    # Run uv sync
    info "Running 'uv sync' to install Python dependencies..."
    uv sync
    
    success "Backend dependencies installed"
}

# Setup frontend
setup_frontend() {
    info "Setting up frontend (npm dependencies)..."
    
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        error "npm is not installed. Please install Node.js and npm first."
        error "Visit: https://nodejs.org/"
        exit 2
    fi
    
    # Check if package.json exists
    if [[ ! -f "package.json" ]]; then
        error "package.json not found in $PROJECT_ROOT"
        exit 1
    fi
    
    # Run npm install
    info "Running 'npm install'..."
    npm install
    
    success "Frontend dependencies installed"
}

# Execute based on target
case "$TARGET" in
    backend)
        setup_backend
        ;;
    frontend)
        setup_frontend
        ;;
    all)
        setup_backend
        echo ""
        setup_frontend
        ;;
esac

echo ""
success "Setup complete!"
echo ""
info "Next steps:"
if [[ "$TARGET" == "backend" ]] || [[ "$TARGET" == "all" ]]; then
    echo "  • Run backend tests: python test_openlibrary.py"
    echo "  • Use the CLI: python main.py add <username> books \"your message\""
fi
if [[ "$TARGET" == "frontend" ]] || [[ "$TARGET" == "all" ]]; then
    echo "  • Build the site: ./scripts/build.sh frontend"
    echo "  • Start dev server: ./scripts/dev.sh frontend"
fi
echo ""
