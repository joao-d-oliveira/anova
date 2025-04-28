#!/bin/bash

# Script to destroy the AWS resources created by Terraform

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Destroying Basketball PDF Analysis Pipeline AWS resources${NC}"
echo "=================================================================="

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}Terraform is not installed. Please install Terraform first.${NC}"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI is not installed. Please install AWS CLI first.${NC}"
    exit 1
fi

# Initialize Terraform if needed
if [ ! -d ".terraform" ]; then
    echo -e "${GREEN}Initializing Terraform...${NC}"
    terraform init

    if [ $? -ne 0 ]; then
        echo -e "${RED}Terraform initialization failed.${NC}"
        exit 1
    fi
fi

# Get ECR repository URL before destroying
ECR_REPO_URL=$(terraform output -raw ecr_repository_url 2>/dev/null)
AWS_REGION=$(terraform output -raw aws_region 2>/dev/null || echo "us-east-1")

# Ask for confirmation
echo -e "${RED}WARNING: This will destroy all AWS resources created by Terraform.${NC}"
echo -e "${RED}This action cannot be undone.${NC}"
echo -e "${YELLOW}Do you want to proceed with destroying all resources? (y/n)${NC}"
read -r answer
if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
    echo -e "${YELLOW}Destroy operation cancelled.${NC}"
    exit 0
fi

# Plan the destroy operation
echo -e "${GREEN}Planning Terraform destroy operation...${NC}"
terraform plan -destroy -out=tfdestroyplan

if [ $? -ne 0 ]; then
    echo -e "${RED}Terraform destroy plan failed.${NC}"
    exit 1
fi

# Ask for final confirmation
echo -e "${RED}FINAL WARNING: This will destroy all AWS resources created by Terraform.${NC}"
echo -e "${YELLOW}Do you want to apply the destroy plan? (y/n)${NC}"
read -r answer
if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
    echo -e "${YELLOW}Destroy operation cancelled.${NC}"
    exit 0
fi

# Apply the destroy plan
echo -e "${GREEN}Applying Terraform destroy plan...${NC}"
terraform apply tfdestroyplan

if [ $? -ne 0 ]; then
    echo -e "${RED}Terraform destroy failed.${NC}"
    exit 1
fi

# Clean up Docker images if ECR repository URL was obtained
if [ ! -z "$ECR_REPO_URL" ]; then
    echo -e "${YELLOW}Do you want to clean up local Docker images? (y/n)${NC}"
    read -r answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        # Authenticate Docker to ECR (needed for some cleanup operations)
        echo -e "${GREEN}Authenticating Docker to ECR...${NC}"
        aws ecr get-login-password --region $AWS_REGION --profile anova | docker login --username AWS --password-stdin $ECR_REPO_URL 2>/dev/null || true
        
        echo -e "${GREEN}Removing local Docker images...${NC}"
        docker rmi $ECR_REPO_URL:latest basketball-analysis:latest 2>/dev/null || true
        echo -e "${GREEN}Local Docker images removed.${NC}"
    fi
fi

echo -e "${GREEN}All AWS resources have been destroyed successfully.${NC}"
echo "=================================================================="
echo -e "${YELLOW}Destroy operation completed.${NC}"

# Remind users about the get_app_url.sh script
if [ -f "get_app_url.sh" ]; then
    echo -e "${YELLOW}Note: The get_app_url.sh script is still available locally.${NC}"
    echo -e "${YELLOW}It will no longer work since the resources have been destroyed.${NC}"
fi
