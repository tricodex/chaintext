#!/bin/bash
# VM Setup Script for ChainContext
# This script prepares a Google Cloud Confidential VM for running ChainContext

# Exit on error
set -e

echo "Setting up ChainContext on Google Cloud Confidential VM..."

# Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required system packages
echo "Installing required system packages..."
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    tpm2-tools \
    libtss2-dev \
    git \
    mongodb \
    redis-server

# Install Docker for containerization
echo "Installing Docker..."
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
"$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Check TPM access
echo "Checking TPM accessibility..."
if [ -c /dev/tpm0 ]; then
    echo "TPM device found at /dev/tpm0"
    sudo chmod 666 /dev/tpm0
else
    echo "Warning: TPM device not found. TEE attestation will not work."
fi

# Clone the repository (if not already cloned)
if [ ! -d "chaincontext-backend" ]; then
    echo "Cloning ChainContext repository..."
    git clone https://github.com/yourusername/chaincontext.git
    cd chaincontext/chaincontext-backend
else
    echo "Repository already exists."
    cd chaincontext-backend
fi

# Create and setup Python virtual environment
echo "Setting up Python virtual environment..."
bash ./setup_venv.sh

# Ensure .env file is configured
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file to set your GEMINI_API_KEY."
else
    echo ".env file already exists."
fi

# Start required services
echo "Starting MongoDB service..."
sudo systemctl enable mongodb
sudo systemctl start mongodb

echo "Starting Redis service..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

echo "Setup complete! To run ChainContext, execute:"
echo "source .venv/bin/activate"
echo "python dev.py"
