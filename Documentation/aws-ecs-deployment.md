# AWS ECS Deployment Guide

This guide provides instructions for deploying the Basketball PDF Analysis Pipeline to AWS Elastic Container Service (ECS) using Python 3.12.

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Docker installed locally
- ECR repository created for the application image

## Step 1: Build and Push Docker Image to ECR

1. Authenticate Docker to your ECR registry:

```bash
aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.<your-region>.amazonaws.com
```

2. Build the Docker image:

```bash
docker build -t basketball-analysis .
```

3. Tag the image for ECR:

```bash
docker tag basketball-analysis:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/basketball-analysis:latest
```

4. Push the image to ECR:

```bash
docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/basketball-analysis:latest
```

## Step 2: Set Up RDS PostgreSQL Database

1. Create a PostgreSQL RDS instance:
   - Go to AWS RDS console
   - Click "Create database"
   - Select PostgreSQL
   - Configure settings (DB instance identifier, credentials, etc.)
   - Make sure to note the endpoint, username, password, and database name

2. Configure security group to allow access from your ECS tasks

## Step 3: Create ECS Cluster

1. Go to the ECS console
2. Click "Create Cluster"
3. Select the appropriate cluster template (e.g., Networking only for Fargate)
4. Configure the cluster settings and create it

## Step 4: Create Task Definition

1. Go to "Task Definitions" in the ECS console
2. Click "Create new Task Definition"
3. Select launch type compatibility (Fargate or EC2)
4. Configure task definition:
   - Name: basketball-analysis
   - Task role: Select appropriate IAM role
   - Network mode: awsvpc (for Fargate)
   - Task execution role: ecsTaskExecutionRole
   - Task memory and CPU: Select appropriate values

5. Add container definition:
   - Container name: basketball-analysis
   - Image: <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/basketball-analysis:latest
   - Port mappings: 8000:8000
   - Environment variables:
     - DB_HOST: Your RDS endpoint
     - DB_NAME: anova
     - DB_USER: anova_user
     - DB_PASSWORD: Your secure password
     - ANTHROPICS_API_KEY: Your Anthropic API key

6. Click "Create"

## Step 5: Create ECS Service

1. Go to your ECS cluster
2. Click "Create Service"
3. Configure service:
   - Launch type: Fargate or EC2
   - Task definition: basketball-analysis (select the version)
   - Service name: basketball-analysis-service
   - Number of tasks: 1 (or more for high availability)
   - Deployment type: Rolling update

4. Configure networking:
   - VPC: Select your VPC
   - Subnets: Select appropriate subnets
   - Security groups: Create or select security group with port 8000 open
   - Auto-assign public IP: ENABLED (if you want public access)

5. Configure load balancing (optional):
   - Add a load balancer if you need high availability
   - Configure health check path: /

6. Click "Next step" and complete service creation

## Step 6: Access the Application

1. Get the public IP or DNS of your ECS task or load balancer
2. Access the application at: http://<your-public-ip>:8000

## Additional Configuration

### Setting Up CloudWatch Logs

1. In your task definition, add log configuration:
   - Log driver: awslogs
   - Log options:
     - awslogs-group: /ecs/basketball-analysis
     - awslogs-region: <your-region>
     - awslogs-stream-prefix: ecs

### Setting Up Auto Scaling (Optional)

1. In your ECS service, go to "Update Service"
2. Configure Auto Scaling:
   - Minimum number of tasks
   - Maximum number of tasks
   - Scaling policies based on CPU/memory utilization

### Setting Up a Custom Domain with HTTPS (Optional)

1. Register a domain in Route 53 or use an existing domain
2. Create an SSL certificate in ACM
3. Configure your load balancer with HTTPS listener
4. Create Route 53 record pointing to your load balancer

## Troubleshooting

- Check CloudWatch Logs for application errors
- Verify security group settings allow traffic to and from the necessary services
- Ensure the RDS database is accessible from the ECS tasks
- Verify environment variables are correctly set in the task definition

## Cleanup

To avoid incurring charges, remember to delete resources when not in use:

1. Delete the ECS service
2. Delete the ECS cluster
3. Delete the RDS instance
4. Delete the ECR repository
5. Delete any associated load balancers, target groups, and security groups
