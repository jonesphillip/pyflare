#!/bin/bash
set -e

# Colors
DIM='\033[2m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "Flare CLI 0.1.0"
echo ""

# Check if uv is installed
echo "> Checking dependencies"
if ! command -v uv &> /dev/null; then
    echo -e "${RED}error:${NC} uv is not installed" >&2
    echo ""
    echo "Install uv with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "Or visit: https://docs.astral.sh/uv"
    exit 1
fi

UV_VERSION=$(uv --version | cut -d' ' -f2)
echo -e "  ${GREEN}✓${NC} ${DIM}uv $UV_VERSION${NC}"

# Install flare as a uv tool
echo ""
echo "> Installing globally"
uv tool install --force . >/dev/null 2>&1
echo -e "  ${GREEN}✓${NC} Installed flare"

echo ""
echo "Next, deploy your Worker:"
echo "  1. Ensure Docker is running"
echo "     (Docker Desktop recommended: https://docs.docker.com/desktop/)"
echo "  2. cd flare-worker"
echo "  3. npm install
echo "  4. npx wrangler deploy"
echo ""
echo "Then configure Flare:"
echo "  flare config init"
echo ""
