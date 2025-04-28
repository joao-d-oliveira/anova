#!/bin/bash

# Script to get the application URL and optionally open it in a browser

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Getting Basketball Analysis Application URL${NC}"
echo "=================================================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI is not installed. Please install AWS CLI first.${NC}"
    exit 1
fi

# Get AWS region from Terraform output
AWS_REGION=$(terraform output -raw aws_region 2>/dev/null || echo "us-east-1")
CLUSTER_NAME=$(terraform output -raw ecs_cluster_name 2>/dev/null || echo "basketball-analysis-cluster")
CONTAINER_PORT=$(terraform output -raw container_port 2>/dev/null || echo "8000")

# Get the public IP address of the running task
echo -e "${GREEN}Getting the public IP address of the running task...${NC}"

# First try to get the task ARNs
echo -e "${YELLOW}Listing running tasks...${NC}"
TASK_ARNS=$(aws --profile anova --region $AWS_REGION ecs list-tasks --cluster $CLUSTER_NAME --desired-status RUNNING --query 'taskArns' --output text)

if [ -z "$TASK_ARNS" ]; then
    echo -e "${RED}No running tasks found in the cluster. Make sure the ECS service is running.${NC}"
    exit 1
fi

echo -e "${YELLOW}Found running tasks: ${TASK_ARNS}${NC}"

# Get the first task ARN
TASK_ARN=$(echo $TASK_ARNS | cut -d' ' -f1)
echo -e "${YELLOW}Using task: ${TASK_ARN}${NC}"

# Get the network interface ID for this task
echo -e "${YELLOW}Getting network interface ID...${NC}"
NETWORK_INTERFACE_ID=$(aws --profile anova --region $AWS_REGION ecs describe-tasks --cluster $CLUSTER_NAME --tasks $TASK_ARN --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text)

if [ -z "$NETWORK_INTERFACE_ID" ]; then
    echo -e "${RED}Failed to get the network interface ID. Trying alternative method...${NC}"
    # Try the alternative method using filters
    PUBLIC_IP=$(aws --profile anova --region $AWS_REGION ec2 describe-network-interfaces --filters Name=description,Values="*${CLUSTER_NAME}*" --query 'NetworkInterfaces[?Status==`in-use`].Association.PublicIp' --output text)
else
    echo -e "${YELLOW}Found network interface ID: ${NETWORK_INTERFACE_ID}${NC}"
    # Get the public IP address for this network interface
    PUBLIC_IP=$(aws --profile anova --region $AWS_REGION ec2 describe-network-interfaces --network-interface-ids $NETWORK_INTERFACE_ID --query 'NetworkInterfaces[0].Association.PublicIp' --output text)
fi

if [ -z "$PUBLIC_IP" ]; then
    echo -e "${RED}Failed to get the public IP address. Make sure the ECS task is running and has a public IP assigned.${NC}"
    exit 1
fi

echo -e "${YELLOW}Found public IP: ${PUBLIC_IP}${NC}"

# Construct the application URL
APP_URL="http://${PUBLIC_IP}:${CONTAINER_PORT}"
echo -e "${GREEN}Application URL: ${YELLOW}${APP_URL}${NC}"

# Ask if the user wants to open the URL in a browser
echo -e "${YELLOW}Do you want to open the URL in your browser? (y/n)${NC}"
read -r answer
if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
    echo -e "${GREEN}Opening the application in your browser...${NC}"
    open "$APP_URL" 2>/dev/null || xdg-open "$APP_URL" 2>/dev/null || echo -e "${RED}Failed to open the URL. Please open it manually.${NC}"
fi

echo "=================================================================="
