#!/bin/bash
# Setup script for Google Cloud Confidential VM with vTPM attestation
# Based on the Flare x Google Verifiable AI Hackathon workshop requirements

set -e

echo "=== Setting up Google Cloud Confidential VM with vTPM attestation ==="

# Check if running with root permissions
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Check if we're running on the required machine type
MACHINE_TYPE=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/machine-type)
if [[ "$MACHINE_TYPE" != *"n2d-standard-2"* ]]; then
  echo "WARNING: This VM is not running on the required n2d-standard-2 machine type."
  echo "The hackathon requirements specify using n2d-standard-2 machine type."
  echo "Current machine type: $MACHINE_TYPE"
fi

# Check if Confidential Computing is enabled
if [ -c "/dev/tpm0" ]; then
  echo "TPM device found at /dev/tpm0 - Confidential Computing is enabled."
else
  echo "ERROR: TPM device not found at /dev/tpm0"
  echo "This indicates that the VM is not configured as a Confidential VM."
  echo "Please create a new VM with Confidential Computing enabled."
  echo "You can continue setup, but TEE attestation will not work."
fi

echo "=== Installing system dependencies ==="
apt-get update
apt-get install -y \
  build-essential \
  curl \
  git \
  tpm2-tools \
  libtss2-dev \
  python3-pip \
  python3-venv

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
  echo "=== Installing Docker ==="
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
  usermod -aG docker $SUDO_USER
fi

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
  echo "=== Installing Docker Compose ==="
  curl -SL https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
  chmod +x /usr/local/bin/docker-compose
fi

# Install Go (for Go-TPM tools)
echo "=== Installing Go ==="
GO_VERSION="1.22.3"
wget https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz
rm -rf /usr/local/go && tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz
rm go${GO_VERSION}.linux-amd64.tar.gz

# Add Go to PATH for the current user
echo 'export PATH=$PATH:/usr/local/go/bin' >> /home/$SUDO_USER/.bashrc

# Install Go-TPM
echo "=== Installing Go-TPM tools ==="
export PATH=$PATH:/usr/local/go/bin
sudo -H -u $SUDO_USER bash -c "go install github.com/google/go-tpm-tools/cmd/...@latest"

# Check for uv and install it if needed
if ! command -v uv &> /dev/null; then
  echo "=== Installing uv package manager ==="
  curl -fsSL https://astral.sh/uv/install.sh | sh
fi

# Setup Python virtual environment for the ChainContext project
echo "=== Setting up Python virtual environment ==="
cd /home/$SUDO_USER/apps/MPC/hackathons/chaincontext/chaincontext-backend
sudo -H -u $SUDO_USER bash -c "python3 -m venv .venv"
sudo -H -u $SUDO_USER bash -c "source .venv/bin/activate && uv pip install -r requirements.txt"

# Check for TPM device
if [ -c /dev/tpm0 ]; then
  echo "=== TPM device found at /dev/tpm0 ==="
else
  echo "=== WARNING: TPM device not found at /dev/tpm0 ==="
  echo "=== This may indicate that the VM is not a Confidential VM ==="
  echo "=== vTPM attestation will not work without a TPM device ==="
fi

# Set permissions for /dev/tpm0 if it exists
if [ -c /dev/tpm0 ]; then
  echo "=== Setting permissions for /dev/tpm0 ==="
  chmod 666 /dev/tpm0
fi

# Print info about the VM
echo "=== VM Information ==="
lscpu | grep "Model name"
free -h | grep "Mem:"

echo "=== Setup complete ==="
echo "=== Please log out and back in to apply the changes to your environment ==="
