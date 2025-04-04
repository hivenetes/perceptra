#!/bin/bash

# Exit on any error
set -e

# Load environment variables from .env file
if [ -f "server/.env" ]; then
    export $(cat server/.env | grep -v '^#' | xargs)
else
    echo "Error: server/.env file not found"
    exit 1
fi

# SSH connection details
SSH_HOST="184.105.215.148"
SSH_USER="paperspace"
SSH_KEY="~/.ssh/ai"

# Check if SSH key exists
if [ ! -f "${SSH_KEY/#\~/$HOME}" ]; then
    echo "Error: SSH key not found at $SSH_KEY"
    exit 1
fi

# Test SSH connection
echo "Testing SSH connection..."
if ! ssh -i $SSH_KEY -o ConnectTimeout=5 $SSH_USER@$SSH_HOST "echo 'SSH connection successful'"; then
    echo "Error: Failed to establish SSH connection"
    exit 1
fi

# Create and setup NIM cache directory with proper permissions
echo "Setting up NIM cache directory..."
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "
    mkdir -p ~/nim-cache
    export NIM_CACHE_PATH=~/nim-cache
    sudo chmod -R 777 \$NIM_CACHE_PATH
"

# Create server directory on remote if it doesn't exist
echo "Creating server directory on remote..."
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "mkdir -p ~/server"

# Copy server directory to VM
echo "Copying server directory to VM..."
scp -i $SSH_KEY -r server/{*,.env} $SSH_USER@$SSH_HOST:~/server/

# Docker login to nvcr.io
#echo "Configuring Docker login..."
#ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "echo $NGC_CLI_API_KEY | docker login nvcr.io -u \$oauthtoken --password-stdin"

# Install docker-compose if not already installed
echo "Ensuring docker-compose is installed..."
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "
    if ! command -v docker-compose &> /dev/null; then
        echo 'Installing docker-compose...'
        sudo curl -L \"https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-linux-x86_64\" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        docker-compose --version
    else
        echo 'docker-compose is already installed'
        docker-compose --version
    fi
"

# Start the application using docker-compose
#echo "Starting the application..."
#ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "cd ~/server && docker-compose --env-file .env up -d"

echo "Deployment completed successfully!" 