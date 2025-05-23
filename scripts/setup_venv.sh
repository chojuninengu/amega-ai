#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up virtual environment for amega-ai...${NC}"

# Check if Python 3.8 or higher is installed
python3 -c "import sys; assert sys.version_info >= (3, 8), 'Python 3.8 or higher is required'" || {
    echo "Error: Python 3.8 or higher is required"
    exit 1
}

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
else
    echo -e "${BLUE}Virtual environment already exists...${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
python -m pip install --upgrade pip

# Install requirements
echo -e "${BLUE}Installing requirements...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${BLUE}To activate the virtual environment, run:${NC}"
echo -e "    source venv/bin/activate" 