#!/bin/bash

# ==========================================
# AlienTec Live Recon Engine - Setup Script
# ==========================================
# Tested on: Kali Linux, Debian/Ubuntu
# ==========================================

# --- Configuration ---
ENV_DIR="venv"
PYTHON_BIN="$ENV_DIR/bin/python"
PIP_BIN="$ENV_DIR/bin/pip"
SECLIST_PATH="/usr/share/seclists"  # <---- Hardcoded path used in your Python config

# --- Colors ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Helper Functions ---
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_tool() {
    if command -v $1 &> /dev/null; then
        echo -e "  [${GREEN}✔${NC}] Binary found: $1"
    else
        echo -e "  [${RED}✘${NC}] Binary missing: $1 (See README to install)"
        MISSING_TOOLS=1
    fi
}

# --- 1. Pre-Flight Checks ---
echo -e "\n${YELLOW}>>> Step 1: System Checks${NC}"

# Must be root to write to /usr/share/seclists
if [ "$EUID" -ne 0 ]; then
    log_error "This script must be run as root (sudo ./install.sh) to install SecLists."
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    log_error "requirements.txt not found! Aborting."
    exit 1
fi
log_success "Root privileges and file check passed."

# --- 2. Installing Python Core ---
echo -e "\n${YELLOW}>>> Step 2: Installing Python Environment Components${NC}"
# Update only if needed, don't fail hard if network is glitchy
if ! apt-get update -qq; then
    log_warn "apt-get update failed. Trying to proceed anyway..."
fi

# Install minimal system deps for Python
if ! apt-get install -y python3 python3-pip python3-venv python3-dev build-essential git &> /dev/null; then
    log_error "Failed to install Python core packages or git."
    exit 1
fi
log_success "Python core installed."

# --- 3. SecLists Installation (Daniel Miessler) ---
echo -e "\n${YELLOW}>>> Step 3: Checking SecLists (Critical Dependency)${NC}"

if [ -d "$SECLIST_PATH" ]; then
    log_success "SecLists found at $SECLIST_PATH."
else
    log_warn "SecLists not found at $SECLIST_PATH."
    log_info "Attempting installation..."

    # Method A: Try apt (Best for Kali)
    if apt-get install -y seclists &> /dev/null; then
        log_success "Installed SecLists via apt."
    else
        # Method B: Git Clone (Best for Ubuntu/Debian)
        log_warn "apt package not found. Cloning from Daniel Miessler's GitHub..."
        log_info "Downloading... (This might take a minute)"
        
        # Using --depth 1 to save bandwidth and time
        if git clone --depth 1 https://github.com/danielmiessler/SecLists.git "$SECLIST_PATH"; then
            log_success "SecLists cloned successfully to $SECLIST_PATH."
        else
            log_error "CRITICAL: Could not install SecLists."
            log_error "Your tool requires this path. Please install manually:"
            log_error "sudo git clone https://github.com/danielmiessler/SecLists.git $SECLIST_PATH"
            exit 1
        fi
    fi
fi

# --- 4. Python Setup ---
echo -e "\n${YELLOW}>>> Step 4: Setting up Virtual Environment${NC}"
if [ ! -d "$ENV_DIR" ]; then
    python3 -m venv "$ENV_DIR"
    log_success "Venv created."
fi

$PIP_BIN install --upgrade pip -q
log_info "Installing Python dependencies..."
if ! $PIP_BIN install -r requirements.txt; then
    log_error "Failed to install Python packages via pip."
    exit 1
fi
log_success "Dependencies installed."

# --- 5. Configuration & Database ---
echo -e "\n${YELLOW}>>> Step 5: Finalizing Configuration${NC}"

# .env Copy
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    log_warn "Created .env from example. Please configure your secrets later."
fi

# DB Migration
log_info "Setting up Database..."
$PYTHON_BIN manage.py migrate
$PYTHON_BIN manage.py collectstatic --noinput &> /dev/null
log_success "Database & Static files ready."

# --- 6. Tool Verification (Status Report) ---
echo -e "\n${YELLOW}>>> Step 6: Verifying External Scanner Tools${NC}"
echo "Note: The following tools are required for scans but must be installed manually."
MISSING_TOOLS=0

check_tool "nmap"
check_tool "feroxbuster"
check_tool "nikto"
check_tool "curl"

# --- 7. Permissions Fix ---
# Give ownership back to the sudo user so they can run the tool without sudo later
if [ ! -z "$SUDO_USER" ]; then
    chown -R $SUDO_USER:$SUDO_USER "$ENV_DIR" db.sqlite3 .env &> /dev/null
    log_success "Permissions reset for user: $SUDO_USER"
fi

# --- 8. Summary ---
echo -e "\n${GREEN}=====================================================${NC}"
echo -e "${GREEN}  🚀 ALIENTEC ENGINE SETUP COMPLETE 🚀  ${NC}"
echo -e "${GREEN}=====================================================${NC}"

if [ $MISSING_TOOLS -eq 1 ]; then
    echo -e "${RED}⚠️  WARNING: Some tools (nmap/feroxbuster) are missing!${NC}"
    echo -e "${RED}   Please install them manually, otherwise scans will fail.${NC}"
else
    echo -e "${GREEN}All tools found. You are ready to go!${NC}"
fi

echo -e "\n${YELLOW}Start the Backend:${NC}"
echo -e "  source venv/bin/activate"
echo -e "  uvicorn engine_api:app --host 0.0.0.0 --port 8001"

echo -e "\n${YELLOW}Start the Frontend:${NC}"
echo -e "  source venv/bin/activate"
echo -e "  python manage.py runserver\n"