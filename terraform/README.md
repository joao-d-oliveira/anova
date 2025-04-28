# Terraform Deployment for Basketball PDF Analysis Pipeline

This directory contains Terraform configuration files for deploying the Basketball PDF Analysis Pipeline to AWS ECS using Python 3.12.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) installed (v1.0.0 or newer)
- AWS CLI installed and configured with appropriate credentials
- Docker installed locally
- An existing VPC and subnets in your AWS account

## Files

- `main.tf` - Main Terraform configuration file
- `variables.tf` - Variable definitions
- `outputs.tf` - Output definitions
- `terraform.tfvars.example` - Example variable values

## Setup

1. Copy the example variables file and update it with your values:

```bash
cp terraform.tfvars.example terraform.tfvars
```

2. Edit `terraform.tfvars` with your specific values:
   - `vpc_id` - Your VPC ID
   - `subnet_ids` - List of your subnet IDs
   - `db_password` - Secure password for the PostgreSQL database
   - `anthropic_api_key` - Your Anthropic API key

## Deployment Steps

1. Initialize Terraform:

```bash
terraform init
```

2. Plan the deployment:

```bash
terraform plan
```

3. Apply the configuration:

```bash
terraform apply
```

4. When prompted, type `yes` to confirm the deployment.

## Building and Pushing the Docker Image

Before the ECS service can run successfully, you need to build and push the Docker image to the ECR repository:

1. Authenticate Docker to your ECR registry:

```bash
aws ecr get-login-password --region $(terraform output -raw aws_region) | docker login --username AWS --password-stdin $(terraform output -raw ecr_repository_url)
```

2. Build the Docker image:

```bash
docker build -t basketball-analysis .
```

3. Tag the image for ECR:

```bash
docker tag basketball-analysis:latest $(terraform output -raw ecr_repository_url):latest
```

4. Push the image to ECR:

```bash
docker push $(terraform output -raw ecr_repository_url):latest
```

## Accessing the Application

After deployment, the application will be accessible via the public IP address of the ECS task. There are several ways to get this information:

### Using the Provided Script

We've included a convenient script to get the application URL:

```bash
cd terraform
./get_app_url.sh
```

This script will:
1. Get the public IP address of the running ECS task
2. Display the full application URL
3. Offer to open the URL in your default browser

### Using AWS CLI Commands

You can also get the application URL manually using AWS CLI commands:

```bash
# Get the public IP address of the running task
PUBLIC_IP=$(aws --profile anova --region $(terraform output -raw aws_region) ec2 describe-network-interfaces --filters Name=description,Values="*$(terraform output -raw ecs_cluster_name)*" --query 'NetworkInterfaces[?Status==`in-use`].Association.PublicIp' --output text)

# Construct the application URL
echo "http://${PUBLIC_IP}:$(terraform output -raw container_port 2>/dev/null || echo "8000")"
```

### Using Terraform Outputs

After running `terraform apply`, you can use the provided outputs:

```bash
# Get the command to retrieve the application host IP
terraform output -raw get_app_host_command

# Get the one-liner command to open the application in your browser
terraform output -raw access_app_command
```

### For Production Use

For a more permanent solution, consider:

1. Setting up an Application Load Balancer (ALB) to route traffic to the ECS service
2. Using AWS App Runner for a simpler deployment with built-in load balancing
3. Using AWS CloudFront with an ALB for a CDN-enabled setup

## Cleaning Up

To avoid incurring charges, remember to destroy the resources when not in use:

```bash
terraform destroy
```

When prompted, type `yes` to confirm the destruction of resources.

## Additional Configuration

### Load Balancer

To add a load balancer, you can extend the Terraform configuration with:

```hcl
resource "aws_lb" "app" {
  name               = "${var.app_name}-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb.id]
  subnets            = var.subnet_ids
}

resource "aws_lb_target_group" "app" {
  name        = "${var.app_name}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"
  
  health_check {
    path                = "/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 3
    unhealthy_threshold = 3
  }
}

resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# Update the ECS service to use the load balancer
resource "aws_ecs_service" "app" {
  # ... existing configuration ...
  
  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = var.app_name
    container_port   = var.container_port
  }
}
```

### Auto Scaling

To add auto scaling, extend the configuration with:

```hcl
resource "aws_appautoscaling_target" "app" {
  max_capacity       = 5
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "app_cpu" {
  name               = "${var.app_name}-cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.app.resource_id
  scalable_dimension = aws_appautoscaling_target.app.scalable_dimension
  service_namespace  = aws_appautoscaling_target.app.service_namespace
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}
