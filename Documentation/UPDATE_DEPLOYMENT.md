# Updating Existing Deployment

This guide provides instructions for updating an existing ECS deployment with the changes we've made to fix the database schema and report generation issues.

## Overview of Changes

1. **Database Schema Changes**:
   - Increased column sizes in the `game_simulations` table
   - Added database initialization script

2. **Application Changes**:
   - Fixed report generation to handle non-string values
   - Added entrypoint script for database initialization

3. **Infrastructure Changes**:
   - Upgraded ECS task resources
   - Upgraded RDS instance
   - Added auto-scaling

## Update Process

### 1. Update the Database Schema

Since the database is already deployed and contains data, we need to update the schema without losing data:

```bash
# Connect to the RDS instance using the bastion host or VPN
psql -h $(terraform output -raw rds_endpoint) -U anova_user -d anova

# Run the ALTER TABLE command to modify the column sizes
ALTER TABLE game_simulations ALTER COLUMN win_probability TYPE VARCHAR(100);
ALTER TABLE game_simulations ALTER COLUMN projected_score TYPE VARCHAR(100);

# Exit PostgreSQL
\q
```

### 2. Build and Push the Updated Docker Image

```bash
# Build the updated Docker image
docker build -t basketball-analysis:latest . --platform linux/amd64

# Authenticate to ECR
aws ecr get-login-password --region $(terraform output -raw aws_region) | docker login --username AWS --password-stdin $(terraform output -raw ecr_repository_url)

# Tag and push the image
docker tag basketball-analysis:latest $(terraform output -raw ecr_repository_url):latest
docker push $(terraform output -raw ecr_repository_url):latest
```

### 3. Apply Terraform Changes

```bash
cd terraform

# Initialize Terraform (if not already done)
terraform init

# Create a plan to see what will change
terraform plan -out=tfplan

# Review the changes carefully to ensure they match expectations
# The plan should show updates to:
# - ECS task definition
# - RDS instance
# - Auto-scaling configuration
# - Other resources

# Apply the changes
terraform apply tfplan
```

### 4. Force New ECS Deployment

Even after pushing a new image and updating the task definition, you may need to force a new deployment:

```bash
# Force a new deployment
aws ecs update-service --cluster $(terraform output -raw ecs_cluster_name) --service $(terraform output -raw ecs_service_name) --force-new-deployment --region $(terraform output -raw aws_region)
```

### 5. Verify the Update

```bash
# Check the ECS service status
aws ecs describe-services --cluster $(terraform output -raw ecs_cluster_name) --services $(terraform output -raw ecs_service_name) --region $(terraform output -raw aws_region)

# Check the latest task status
TASK_ARN=$(aws ecs list-tasks --cluster $(terraform output -raw ecs_cluster_name) --service-name $(terraform output -raw ecs_service_name) --region $(terraform output -raw aws_region) --query 'taskArns[0]' --output text)
aws ecs describe-tasks --cluster $(terraform output -raw ecs_cluster_name) --tasks $TASK_ARN --region $(terraform output -raw aws_region)

# Check the logs
aws logs get-log-events --log-group-name "/ecs/basketball-analysis" --log-stream-name $(aws logs describe-log-streams --log-group-name "/ecs/basketball-analysis" --order-by LastEventTime --descending --limit 1 --query 'logStreams[0].logStreamName' --output text) --region $(terraform output -raw aws_region)
```

## Rollback Plan

If issues occur during the update, you can roll back using the following steps:

### 1. Roll Back Terraform Changes

```bash
# If you have a previous state file, you can use it to restore the previous configuration
terraform apply -var-file=previous_values.tfvars
```

### 2. Roll Back Database Schema

```bash
# Connect to the database
psql -h $(terraform output -raw rds_endpoint) -U anova_user -d anova

# Revert the column size changes
ALTER TABLE game_simulations ALTER COLUMN win_probability TYPE VARCHAR(50);
ALTER TABLE game_simulations ALTER COLUMN projected_score TYPE VARCHAR(50);

# Exit PostgreSQL
\q
```

### 3. Roll Back to Previous Docker Image

```bash
# If you tagged the previous image with a version
aws ecs update-service --cluster $(terraform output -raw ecs_cluster_name) --service $(terraform output -raw ecs_service_name) --task-definition basketball-analysis:previous --region $(terraform output -raw aws_region)
```

## Monitoring the Update

During and after the update, monitor the following:

1. **ECS Task Status**: Watch for successful task startup
2. **CloudWatch Logs**: Check for any errors in the application logs
3. **RDS Performance**: Monitor database performance during and after the update
4. **Application Functionality**: Test the application to ensure it's working correctly

## Special Considerations

### Database Downtime

The ALTER TABLE commands should be fast since we're only changing column types to a larger size, but be prepared for a brief period where the database might be less responsive.

### Zero-Downtime Deployment

The ECS service is configured to use a rolling deployment strategy, which should minimize downtime. However, during the transition, some requests might fail if they hit a task that's being replaced.

### Auto-Scaling

After the update, the service will have auto-scaling enabled. Monitor the scaling events to ensure they're working as expected and adjust the scaling thresholds if necessary.
