#!/usr/bin/env bash
#
# db-init.sh - Initialize or reset the SQLite database
#
# Usage:
#   ./scripts/db-init.sh [--reset]
#
# Examples:
#   ./scripts/db-init.sh          # Create database if it doesn't exist
#   ./scripts/db-init.sh --reset  # Backup existing DB and create fresh one

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
RESET=false

for arg in "$@"; do
    case "$arg" in
        --reset)
            RESET=true
            ;;
        --help|-h)
            echo "Usage: $0 [--reset]"
            echo ""
            echo "Options:"
            echo "  --reset    Backup existing database and create a fresh one"
            echo ""
            echo "This script initializes the library.db SQLite database."
            echo "The database schema is automatically created when the app runs."
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

DB_FILE="library.db"

echo ""
info "Database initialization script"
echo ""

# Check if database exists
if [[ -f "$DB_FILE" ]]; then
    if [[ "$RESET" == true ]]; then
        warn "Database already exists: $DB_FILE"
        
        # Create backup
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_FILE="${DB_FILE}.backup_${TIMESTAMP}"
        
        info "Creating backup: $BACKUP_FILE"
        cp "$DB_FILE" "$BACKUP_FILE"
        success "Backup created"
        
        info "Removing old database..."
        rm "$DB_FILE"
        success "Old database removed"
    else
        success "Database already exists: $DB_FILE"
        info "Use --reset flag to create a fresh database"
        echo ""
        exit 0
    fi
fi

# Initialize database by running a simple import
# The db.py module creates tables on first connection
info "Initializing database schema..."

# Create a temporary Python script to initialize the database
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

from db import connect, init_db

try:
    conn = connect()
    init_db(conn)
    conn.close()
    print("Database schema initialized successfully")
except Exception as e:
    print(f"Error initializing database: {e}", file=sys.stderr)
    sys.exit(1)
EOF

if [[ $? -eq 0 ]]; then
    success "Database initialized: $DB_FILE"
    echo ""
    info "The database is ready to use!"
    echo ""
    info "Next steps:"
    echo "  • Add media: python main.py add <username> books \"your message\""
    echo "  • View library: python main.py show <username>"
    echo ""
else
    error "Failed to initialize database"
    exit 1
fi
