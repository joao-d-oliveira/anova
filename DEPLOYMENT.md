# Deployment Guide for Basketball Analysis Application

This guide provides instructions for deploying the Basketball PDF Analysis Pipeline to AWS Elastic Container Service (ECS) using Terraform.

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Terraform installed
- Docker installed locally

## Configuration

1. Update the `terraform/terraform.tfvars` file with your specific values:

```hcl
aws_region          = "us-east-1"
vpc_id              = "vpc-xxxxxxxxxxxxxxxxx"
subnet_ids          = ["subnet-xxxxxxxxxxxxxxxxx", "subnet-yyyyyyyyyyyyyyyyy"]
db_password         = "your-secure-password"
anthropic_api_key   = "your-anthropic-api-key"
```

## Deployment Steps

### 1. Build and Push Docker Image

1. Build the Docker image:

```bash
docker build -t basketball-analysis .
```

2. Authenticate Docker to your ECR registry:

```bash
aws ecr get-login-password --region $(terraform output -raw aws_region) | docker login --username AWS --password-stdin $(terraform output -raw ecr_repository_url)
```

3. Tag and push the image:

```bash
docker tag basketball-analysis:latest $(terraform output -raw ecr_repository_url):latest
docker push $(terraform output -raw ecr_repository_url):latest
```

### 2. Deploy Infrastructure with Terraform

1. Initialize Terraform:

```bash
cd terraform
terraform init
```

2. Plan the deployment:

```bash
terraform plan -out=tfplan
```

3. Apply the deployment:

```bash
terraform apply tfplan
```

### 3. Verify Deployment

1. Check the ECS service status:

```bash
aws ecs describe-services --cluster $(terraform output -raw ecs_cluster_name) --services $(terraform output -raw ecs_service_name) --region $(terraform output -raw aws_region)
```

2. Get the public IP of the ECS task:

```bash
aws ecs list-tasks --cluster $(terraform output -raw ecs_cluster_name) --service-name $(terraform output -raw ecs_service_name) --region $(terraform output -raw aws_region) --query 'taskArns[0]' --output text | xargs aws ecs describe-tasks --cluster $(terraform output -raw ecs_cluster_name) --region $(terraform output -raw aws_region) --tasks --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text | xargs aws ec2 describe-network-interfaces --region $(terraform output -raw aws_region) --network-interface-ids --query 'NetworkInterfaces[0].Association.PublicIp' --output text
```

3. Access the application at `http://<public-ip>:8000`

## Application Features

The deployed application includes:

- Automatic database initialization with the correct schema
- Auto-scaling based on CPU and memory utilization
- Health checks to ensure application availability
- CloudWatch logging for monitoring and troubleshooting

## Infrastructure Components

The deployment includes:

1. **ECS Cluster**: Fargate-based cluster for running containerized applications
2. **RDS PostgreSQL**: Database for storing analysis results and game simulations
3. **ECR Repository**: For storing Docker images
4. **CloudWatch Logs**: For application logging
5. **Auto Scaling**: To handle varying loads

## Database Schema

The application automatically initializes the database with the correct schema, including:

- Teams table
- Players table
- Games table
- Game simulations table with appropriate column sizes for storing analysis results

## Monitoring and Maintenance

### Logs

View application logs in CloudWatch:

```bash
aws logs get-log-events --log-group-name "/ecs/basketball-analysis" --log-stream-name $(aws logs describe-log-streams --log-group-name "/ecs/basketball-analysis" --order-by LastEventTime --descending --limit 1 --query 'logStreams[0].logStreamName' --output text) --region $(terraform output -raw aws_region)
```

### Scaling

The application automatically scales based on:
- CPU utilization (target: 70%)
- Memory utilization (target: 70%)

Maximum capacity: 5 instances
Minimum capacity: 1 instance (configurable)

### Database Backups

RDS automatically creates backups with a 7-day retention period.

## Cleanup

To destroy all resources when no longer needed:

```bash
cd terraform
terraform destroy
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**:
   - Check security group rules
   - Verify database credentials in ECS task definition

2. **Application Startup Failures**:
   - Check CloudWatch logs for error messages
   - Verify that the entrypoint script has execute permissions

3. **Auto-scaling Issues**:
   - Check CloudWatch metrics for CPU and memory utilization
   - Verify auto-scaling policies and targets
