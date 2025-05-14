# Database Connection Guide

This guide explains how to connect to the AWS RDS PostgreSQL database from both local development and cloud environments.

## Overview

The application uses an AWS RDS PostgreSQL database with the following configuration:
- Instance: db.t3.small
- Engine: PostgreSQL 14
- Storage: 20GB gp2
- Multi-AZ: Disabled
- Publicly accessible: Yes (but still requires VPC access)

## Connection Methods

### Method 1: SSH Tunnel (Recommended for Local Development)

Since the RDS database is in a private subnet within the AWS VPC, you need to create an SSH tunnel through an EC2 instance in the same VPC to connect to it from your local machine.

1. **Prerequisites**:
   - An EC2 instance in the same VPC as the RDS database
   - SSH key pair for the EC2 instance
   - AWS CLI configured with appropriate credentials

2. **Using the SSH Tunnel Script**:
   ```bash
   # Make the script executable
   chmod +x db_tunnel.sh
   
   # Run the script
   ./db_tunnel.sh
   ```

3. **Script Workflow**:
   - The script will ask for your AWS profile name
   - It will list available EC2 instances
   - You'll select an instance to use for the tunnel
   - You'll provide the path to your SSH key
   - The script will create a tunnel from localhost:5433 to the RDS database

4. **Connection Details When Using Tunnel**:
   - Host: localhost
   - Port: 5433
   - Database: anova
   - Username: anova_user
   - Password: (from your .env file)

### Method 2: Direct Connection (For AWS Services)

Services running within the AWS VPC (like your ECS containers) can connect directly to the RDS database:

- Host: basketball-analysis-db.cgdoswe6ytxj.us-east-1.rds.amazonaws.com
- Port: 5432
- Database: anova
- Username: anova_user
- Password: (from your terraform.tfvars file)

## Environment Configuration

### Local Development (.env file)

For local development with SSH tunnel:

```
DB_HOST=localhost
DB_PORT=5433
DB_NAME=anova
DB_USER=anova_user
DB_PASSWORD=9lvbbiYkspuG8EKW5gHnU73KZyaCNu3IrSUM6jaB874=
```

### Docker Compose

The docker-compose.yml file is configured to use host.docker.internal:5433 to connect to the database through the SSH tunnel:

```yaml
environment:
  - DB_HOST=host.docker.internal
  - DB_PORT=5433
  - DB_NAME=${DB_NAME}
  - DB_USER=${DB_USER}
  - DB_PASSWORD=${DB_PASSWORD}
```

### AWS Deployment (Terraform)

The ECS task definition in Terraform is configured to connect directly to the RDS database:

```hcl
environment = [
  {
    name  = "DB_HOST"
    value = aws_db_instance.postgres.address
  },
  {
    name  = "DB_PORT"
    value = "5432"
  },
  {
    name  = "DB_NAME"
    value = var.db_name
  },
  {
    name  = "DB_USER"
    value = var.db_username
  },
  {
    name  = "DB_PASSWORD"
    value = var.db_password
  }
]
```

## Testing the Connection

You can test the database connection using the provided script:

```bash
# Make sure the SSH tunnel is running
./db_tunnel.sh

# In another terminal, run the test script
/opt/homebrew/Caskroom/miniforge/base/envs/anova/bin/python test_db_connection.py
```

## Troubleshooting

1. **Connection Timeout**:
   - Ensure the SSH tunnel is running
   - Verify the EC2 instance is in the same VPC as the RDS database
   - Check security groups to ensure they allow traffic on port 5432

2. **Authentication Failed**:
   - Verify the database credentials in your .env file
   - Check if the database user exists and has the correct permissions

3. **Database Not Found**:
   - Verify the database name is correct
   - Check if the database has been created