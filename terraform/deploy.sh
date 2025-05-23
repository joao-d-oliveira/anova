#!/bin/bash

# Script to deploy the Docker container to ECS
# This script will:
# 1. Build the Docker image
# 2. Tag the image
# 3. Push the image to Amazon ECR
# 4. Update the ECS service to use the new image

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Deploying Basketball Analysis Application to ECS${NC}"
echo "=================================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI is not installed. Please install AWS CLI first.${NC}"
    exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}Terraform is not installed. Please install Terraform first.${NC}"
    exit 1
fi

# Check if we're in the terraform directory
if [ ! -f "main.tf" ]; then
    echo -e "${RED}This script must be run from the terraform directory.${NC}"
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

# Get AWS region and ECR repository URL from Terraform output
echo -e "${GREEN}Getting AWS region and ECR repository URL...${NC}"
AWS_REGION=$(terraform output -raw aws_region 2>/dev/null || echo "us-east-1")
ECR_REPO_URL=$(terraform output -raw ecr_repository_url 2>/dev/null)
APP_NAME=$(terraform output -raw app_name 2>/dev/null || echo "basketball-analysis")
IMAGE_TAG=$(date +%Y%m%d%H%M%S)

if [ -z "$ECR_REPO_URL" ]; then
    echo -e "${RED}Failed to get ECR repository URL. Make sure Terraform has been applied.${NC}"
    echo -e "${YELLOW}Running terraform apply to create infrastructure...${NC}"
    
    # Check if terraform.tfvars exists
    if [ ! -f "terraform.tfvars" ]; then
        echo -e "${RED}terraform.tfvars file not found. Please create it based on terraform.tfvars.example.${NC}"
        exit 1
    fi
    
    terraform apply -auto-approve
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Terraform apply failed.${NC}"
        exit 1
    fi
    
    # Try to get ECR repository URL again
    ECR_REPO_URL=$(terraform output -raw ecr_repository_url)
    
    if [ -z "$ECR_REPO_URL" ]; then
        echo -e "${RED}Failed to get ECR repository URL after applying Terraform.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}AWS Region: ${AWS_REGION}${NC}"
echo -e "${GREEN}ECR Repository URL: ${ECR_REPO_URL}${NC}"
echo -e "${GREEN}Image Tag: ${IMAGE_TAG}${NC}"

# Build Docker image
echo -e "${GREEN}Building Docker image...${NC}"
cd ..
docker build --platform linux/amd64 -t ${APP_NAME}:${IMAGE_TAG} .

if [ $? -ne 0 ]; then
    echo -e "${RED}Docker build failed.${NC}"
    exit 1
fi

# Tag Docker image for ECR
echo -e "${GREEN}Tagging Docker image for ECR...${NC}"
docker tag ${APP_NAME}:${IMAGE_TAG} ${ECR_REPO_URL}:${IMAGE_TAG}
docker tag ${APP_NAME}:${IMAGE_TAG} ${ECR_REPO_URL}:latest

# Authenticate Docker to ECR
echo -e "${GREEN}Authenticating Docker to ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} --profile anova | docker login --username AWS --password-stdin ${ECR_REPO_URL}

if [ $? -ne 0 ]; then
    echo -e "${RED}Docker authentication to ECR failed.${NC}"
    exit 1
fi

# Push Docker image to ECR
echo -e "${GREEN}Pushing Docker image to ECR...${NC}"
docker push ${ECR_REPO_URL}:${IMAGE_TAG}
docker push ${ECR_REPO_URL}:latest

if [ $? -ne 0 ]; then
    echo -e "${RED}Docker push to ECR failed.${NC}"
    exit 1
fi

# Return to terraform directory
cd terraform

# Update terraform.tfvars with the new image tag
echo -e "${GREEN}Updating image_tag in terraform.tfvars...${NC}"
sed -i.bak "s/^image_tag.*=.*\".*\"/image_tag = \"${IMAGE_TAG}\"/" terraform.tfvars

# Apply Terraform to update the ECS service
echo -e "${GREEN}Applying Terraform to update the ECS service...${NC}"
terraform apply -auto-approve

if [ $? -ne 0 ]; then
    echo -e "${RED}Terraform apply failed.${NC}"
    exit 1
fi

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo "=================================================================="

# Get the application URL
echo -e "${GREEN}Getting the application URL...${NC}"
./get_app_url.sh

echo -e "${GREEN}Deployment process completed.${NC}"