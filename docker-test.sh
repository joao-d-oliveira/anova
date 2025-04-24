#!/bin/bash

# Script to test the Docker setup locally

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing Docker setup for Basketball PDF Analysis Pipeline${NC}"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating a sample .env file...${NC}"
    echo "ANTHROPICS_API_KEY=your_api_key_here" > .env
    echo -e "${YELLOW}Please update the .env file with your actual Anthropic API key.${NC}"
fi

# Build and start the containers
echo -e "${GREEN}Building and starting Docker containers...${NC}"
docker-compose up --build -d

# Check if containers are running
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Containers started successfully!${NC}"
    
    # Wait for the application to start
    echo -e "${YELLOW}Waiting for the application to start...${NC}"
    sleep 10
    
    # Check if the application is accessible
    echo -e "${GREEN}Testing application access...${NC}"
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000)
    
    if [ "$response" == "200" ]; then
        echo -e "${GREEN}Application is accessible at http://localhost:8000${NC}"
    else
        echo -e "${RED}Application is not accessible. HTTP response code: $response${NC}"
        echo -e "${YELLOW}Check the logs for more information:${NC}"
        docker-compose logs app
    fi
    
    # Provide instructions for stopping the containers
    echo -e "${YELLOW}To stop the containers, run:${NC} docker-compose down"
else
    echo -e "${RED}Failed to start containers. Check the logs for more information.${NC}"
    docker-compose logs
fi

echo "=================================================="
echo -e "${YELLOW}Docker test completed.${NC}"
