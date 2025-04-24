#!/bin/bash

# Script to deploy the application using Terraform

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Deploying Basketball PDF Analysis Pipeline to AWS ECS using Terraform${NC}"
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

# Check if terraform.tfvars exists
if [ ! -f terraform.tfvars ]; then
    echo -e "${YELLOW}Warning: terraform.tfvars file not found. Creating from example...${NC}"
    if [ -f terraform.tfvars.example ]; then
        cp terraform.tfvars.example terraform.tfvars
        echo -e "${YELLOW}Please update terraform.tfvars with your actual values before continuing.${NC}"
        echo -e "${YELLOW}Press Enter to continue after updating the file, or Ctrl+C to exit.${NC}"
        read
    else
        echo -e "${RED}terraform.tfvars.example not found. Please create terraform.tfvars manually.${NC}"
        exit 1
    fi
fi

# Initialize Terraform
echo -e "${GREEN}Initializing Terraform...${NC}"
terraform init

if [ $? -ne 0 ]; then
    echo -e "${RED}Terraform initialization failed.${NC}"
    exit 1
fi

# Plan the deployment
echo -e "${GREEN}Planning Terraform deployment...${NC}"
terraform plan -out=tfplan

if [ $? -ne 0 ]; then
    echo -e "${RED}Terraform plan failed.${NC}"
    exit 1
fi

# Ask for confirmation
echo -e "${YELLOW}Do you want to apply the Terraform plan? (y/n)${NC}"
read -r answer
if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
    echo -e "${YELLOW}Deployment cancelled.${NC}"
    exit 0
fi

# Apply the plan
echo -e "${GREEN}Applying Terraform plan...${NC}"
terraform apply tfplan

if [ $? -ne 0 ]; then
    echo -e "${RED}Terraform apply failed.${NC}"
    exit 1
fi

# Get outputs
echo -e "${GREEN}Getting deployment outputs...${NC}"
ECR_REPO_URL=$(terraform output -raw ecr_repository_url)
AWS_REGION=$(terraform output -raw aws_region 2>/dev/null || echo "us-east-1")

# Build and push Docker image
echo -e "${GREEN}Building and pushing Docker image to ECR...${NC}"
echo -e "${YELLOW}Do you want to build and push the Docker image to ECR? (y/n)${NC}"
read -r answer
if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
    # Authenticate Docker to ECR
    echo -e "${GREEN}Authenticating Docker to ECR...${NC}"
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO_URL

    if [ $? -ne 0 ]; then
        echo -e "${RED}Docker authentication to ECR failed.${NC}"
        exit 1
    fi

    # Build Docker image
    echo -e "${GREEN}Building Docker image...${NC}"
    cd ..
    docker build -t basketball-analysis .

    if [ $? -ne 0 ]; then
        echo -e "${RED}Docker build failed.${NC}"
        exit 1
    fi

    # Tag Docker image
    echo -e "${GREEN}Tagging Docker image...${NC}"
    docker tag basketball-analysis:latest $ECR_REPO_URL:latest

    if [ $? -ne 0 ]; then
        echo -e "${RED}Docker tag failed.${NC}"
        exit 1
    fi

    # Push Docker image
    echo -e "${GREEN}Pushing Docker image to ECR...${NC}"
    docker push $ECR_REPO_URL:latest

    if [ $? -ne 0 ]; then
        echo -e "${RED}Docker push failed.${NC}"
        exit 1
    fi

    echo -e "${GREEN}Docker image pushed to ECR successfully.${NC}"
    cd terraform
fi

# Print deployment information
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${YELLOW}Deployment Information:${NC}"
echo -e "ECR Repository URL: ${GREEN}$ECR_REPO_URL${NC}"
echo -e "ECS Cluster: ${GREEN}$(terraform output -raw ecs_cluster_name)${NC}"
echo -e "ECS Service: ${GREEN}$(terraform output -raw ecs_service_name)${NC}"
echo -e "RDS Endpoint: ${GREEN}$(terraform output -raw rds_endpoint)${NC}"
echo -e "CloudWatch Log Group: ${GREEN}$(terraform output -raw cloudwatch_log_group)${NC}"

echo -e "${YELLOW}Note: The application may take a few minutes to start up.${NC}"
echo -e "${YELLOW}You can check the status of the ECS service in the AWS Console.${NC}"

echo "=================================================================="
echo -e "${YELLOW}Deployment completed.${NC}"
