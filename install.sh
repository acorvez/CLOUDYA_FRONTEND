#!/bin/bash

echo "Installation of Cloudya CLI..."

# Check if Python 3 is installed
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    # Check Python version
    PYTHON_VERSION=$(python --version 2>&1 | cut -d " " -f 2 | cut -d "." -f 1)
    if [ "$PYTHON_VERSION" -ge 3 ]; then
        PYTHON=python
    else
        echo "Error: Python 3 is required but not found."
        exit 1
    fi
else
    echo "Error: Python 3 is required but not found."
    exit 1
fi

echo "Using Python: $($PYTHON --version)"

# Check if pip is installed
if command -v pip3 &>/dev/null; then
    PIP=pip3
elif command -v pip &>/dev/null; then
    PIP=pip
else
    echo "Error: pip is required but not found."
    exit 1
fi

echo "Using pip: $($PIP --version)"

# Install or upgrade Cloudya
echo "Installing Cloudya CLI..."
$PIP install --upgrade cloudya

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "Cloudya CLI has been installed successfully!"
    echo ""
    echo "You can now use Cloudya by running the 'cloudya' command."
    echo ""
    echo "Get started with:"
    echo "  cloudya --help"
    echo ""
    echo "For documentation, visit: https://github.com/votre-repo/cloudya"
else
    echo "Error: Failed to install Cloudya CLI."
    exit 1
fi

# Create configuration directory
CONFIG_DIR="$HOME/.cloudya"
if [ ! -d "$CONFIG_DIR" ]; then
    echo "Creating configuration directory: $CONFIG_DIR"
    mkdir -p "$CONFIG_DIR"
fi

# Create templates directory structure
TEMPLATES_DIR="$CONFIG_DIR/templates"
if [ ! -d "$TEMPLATES_DIR" ]; then
    echo "Creating templates directory structure..."
    mkdir -p "$TEMPLATES_DIR/terraform/aws"
    mkdir -p "$TEMPLATES_DIR/terraform/gcp"
    mkdir -p "$TEMPLATES_DIR/terraform/azure"
    mkdir -p "$TEMPLATES_DIR/terraform/openstack"
    mkdir -p "$TEMPLATES_DIR/terraform/vmware"
    mkdir -p "$TEMPLATES_DIR/terraform/proxmox"
    mkdir -p "$TEMPLATES_DIR/terraform/nutanix"
    mkdir -p "$TEMPLATES_DIR/ansible"
    mkdir -p "$TEMPLATES_DIR/apps"
fi

echo ""
echo "Installation complete! You can now use Cloudya CLI."
