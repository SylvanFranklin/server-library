#!/usr/bin/env bash
#
# build.sh - Build frontend, backend, or both
#
# Usage:
#   ./scripts/build.sh [frontend|backend|all] [--prod|--dev]
#
# Examples:
#   ./scripts/build.sh                    # Build both in production mode
#   ./scripts/build.sh all --prod         # Build both in production mode
#   ./scripts/build.sh frontend --dev     # Build frontend in dev mode
#   ./scripts/build.sh backend            # Build backend (runs linting)

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

# Parse arguments
TARGET="all"
MODE="prod"

for arg in "$@"; do
    case "$arg" in
        frontend|backend|all)
            TARGET="$arg"
            ;;
        --prod|--production)
            MODE="prod"
            ;;
        --dev|--development)
            MODE="dev"
            ;;
        --help|-h)
            echo "Usage: $0 [frontend|backend|all] [--prod|--dev]"
            echo ""
            echo "Targets:"
            echo "  frontend   Build only the Astro static site"
            echo "  backend    Build/check only the Python backend"
            echo "  all        Build both (default)"
            echo ""
            echo "Modes:"
            echo "  --prod     Production build (default)"
            echo "  --dev      Development build"
            exit 0
            ;;
        *)
            error "Unknown argument: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo ""
info "Building server-library [$TARGET] in $MODE mode..."
echo ""

# Check for dependencies
check_dependencies() {
    local missing=0
    
    if [[ "$TARGET" == "backend" ]] || [[ "$TARGET" == "all" ]]; then
        if ! command -v uv &> /dev/null; then
            error "uv is not installed"
            missing=1
        fi
        if [[ ! -d ".venv" ]]; then
            warn "Python virtual environment not found"
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

# Build backend
build_backend() {
    info "Building backend..."
    
    # Check if ruff is available
    if command -v ruff &> /dev/null; then
        info "Running linter (ruff check)..."
        if ruff check .; then
            success "Linting passed"
        else
            error "Linting failed"
            exit 1
        fi
        
        info "Checking formatting (ruff format --check)..."
        if ruff format --check .; then
            success "Formatting check passed"
        else
            warn "Code needs formatting. Run 'ruff format .' to fix."
            if [[ "$MODE" == "prod" ]]; then
                exit 1
            fi
        fi
    else
        warn "ruff not found, skipping linting"
    fi
    
    # Run tests
    info "Running tests..."
    uv run python test_openlibrary.py
    uv run python test_book_extractor.py
    uv run python test_music_extractor.py
    
    success "Backend build complete"
}

# Build frontend
build_frontend() {
    info "Building frontend..."
    
    # Export site data from database
    info "Exporting site data from database..."
    uv run python export_site_data.py
    success "Site data exported"
    
    # Build Astro site
    if [[ "$MODE" == "dev" ]]; then
        info "Building Astro site (development mode)..."
        npm run build
    else
        info "Building Astro site (production mode)..."
        npm run build
    fi
    
    success "Frontend build complete"
    
    # Show output location
    if [[ -d "dist" ]]; then
        info "Built files are in: dist/"
    fi
}

# Check dependencies first
check_dependencies

# Execute based on target
case "$TARGET" in
    backend)
        build_backend
        ;;
    frontend)
        build_frontend
        ;;
    all)
        build_backend
        echo ""
        build_frontend
        ;;
esac

echo ""
success "Build complete!"
echo ""

if [[ "$TARGET" == "frontend" ]] || [[ "$TARGET" == "all" ]]; then
    info "To preview the site: npm run preview"
fi

echo ""
