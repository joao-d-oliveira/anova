# Deployment Guide for Basketball PDF Analysis Pipeline

This guide provides instructions for deploying the Basketball PDF Analysis Pipeline using Docker and AWS Elastic Container Service (ECS).

## Local Deployment with Docker

### Prerequisites

- Docker installed
- Docker Compose installed
- Anthropic API key

### Quick Start

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a `.env` file with your Anthropic API key:
   ```
   echo "ANTHROPICS_API_KEY=your_api_key_here" > .env
   ```

3. Build and start the containers:
   ```
   docker-compose up --build
   ```

4. Access the application at http://localhost:8000

### Testing the Docker Setup

We've included a script to test the Docker setup:

```bash
./docker-test.sh
```

This script will:
- Check if Docker and Docker Compose are installed
- Create a sample .env file if one doesn't exist
- Build and start the containers
- Test if the application is accessible
- Provide instructions for stopping the containers

### Docker Compose Configuration

The `docker-compose.yml` file includes:

- **app**: The main application container
  - Built from the Dockerfile
  - Exposes port 8000
  - Connects to the PostgreSQL database
  - Uses environment variables for configuration

- **db**: PostgreSQL database container
  - Uses the official PostgreSQL 14 image
  - Exposes port 5432
  - Stores data in a named volume

### Environment Variables

The application uses the following environment variables:

- `DB_HOST`: Database hostname (default: "localhost")
- `DB_NAME`: Database name (default: "anova")
- `DB_USER`: Database username (default: "anova_user")
- `DB_PASSWORD`: Database password (default: "anova@bask3t")
- `ANTHROPICS_API_KEY`: Your Anthropic API key (required)

### Technical Details

- Python 3.12 is used as the base image for the Docker container
- PostgreSQL 14 is used for the database
- The application runs on port 8000

## AWS ECS Deployment

We provide two options for deploying to AWS ECS:

### Option 1: Manual Deployment

For detailed instructions on manually deploying to AWS ECS, see [aws-ecs-deployment.md](aws-ecs-deployment.md).

### Option 2: Terraform Deployment (Recommended)

For automated infrastructure deployment using Terraform, see [terraform/README.md](terraform/README.md).

The Terraform configuration:
- Creates an ECR repository for the Docker image
- Sets up an ECS cluster
- Creates a PostgreSQL RDS instance
- Configures security groups and IAM roles
- Deploys the application as an ECS service
- Sets up CloudWatch logging

#### Key Steps for Terraform Deployment

1. Configure your AWS credentials
2. Update the Terraform variables
3. Run `terraform apply` to create the infrastructure
4. Build and push the Docker image to ECR
5. Access the application

For detailed instructions, see the [Terraform README](terraform/README.md).

## Troubleshooting

### Common Docker Issues

- **Database connection errors**: Ensure the database container is running and the environment variables are correctly set.
- **Port conflicts**: If port 8000 or 5432 is already in use, modify the port mappings in `docker-compose.yml`.
- **Permission issues**: Ensure the temp directories have appropriate permissions.

### Common AWS ECS Issues

- **Task failures**: Check CloudWatch Logs for application errors.
- **Database connectivity**: Verify security group settings allow traffic between ECS tasks and RDS.
- **Environment variables**: Ensure all required environment variables are set in the task definition.

## Security Considerations

- Store sensitive information like database credentials and API keys as environment variables.
- For production deployments, use AWS Secrets Manager or Parameter Store for sensitive values.
- Configure security groups to restrict access to only necessary ports and services.
- Use HTTPS for production deployments.
