provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
  allowed_account_ids = ["597312200011"]
}

#################################################
# NETWORKING
#################################################

# Get default VPC
data "aws_vpc" "default" {
  default = true
}

# Get default subnets
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

#################################################
# AUTHENTICATION - COGNITO
#################################################

# AWS Cognito User Pool
resource "aws_cognito_user_pool" "anova_pool" {
  name = "anova-user-pool"
  
  # Allow users to sign up with email
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]
  
  # Password policy
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }
  
  # Schema attributes
  schema {
    attribute_data_type = "String"
    name                = "name"
    required            = true
    mutable             = true
  }
  
  schema {
    attribute_data_type = "String"
    name                = "phone_number"
    required            = true
    mutable             = true
  }
  
  schema {
    attribute_data_type = "String"
    name                = "custom:school"
    required            = false
    mutable             = true
    
    string_attribute_constraints {
      min_length = 1
      max_length = 100
    }
  }
  
  schema {
    attribute_data_type = "String"
    name                = "custom:role"
    required            = false
    mutable             = true
    
    string_attribute_constraints {
      min_length = 1
      max_length = 50
    }
  }
  
  # Email configuration
  email_configuration {
    email_sending_account = "DEVELOPER"
    from_email_address    = "no-reply@anovasports.com"
    source_arn            = aws_ses_email_identity.no_reply.arn
  }
  
  # Account recovery settings
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }
  
  # Device configuration
  device_configuration {
    challenge_required_on_new_device      = false
    device_only_remembered_on_user_prompt = true
  }
  
  # MFA configuration
  mfa_configuration = "OFF"
  
  # Admin create user config
  admin_create_user_config {
    allow_admin_create_user_only = false
    
    invite_message_template {
      email_message = "Your username is {username} and temporary password is {####}. Please login to Anova and change your password."
      email_subject = "Your temporary Anova password"
      sms_message   = "Your username is {username} and temporary password is {####}."
    }
  }
  
  # Verification message
  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_message        = "Your verification code is {####}."
    email_subject        = "Your Anova verification code"
    sms_message          = "Your verification code is {####}."
  }
  
  # Lambda triggers
  # Uncomment and configure if needed
  # lambda_config {
  #   pre_sign_up = aws_lambda_function.pre_sign_up.arn
  # }
  
  tags = {
    Name        = "Anova User Pool"
    Environment = var.environment
  }
}

# AWS Cognito User Pool Client
resource "aws_cognito_user_pool_client" "anova_client" {
  name = "anova-app-client"
  
  user_pool_id = aws_cognito_user_pool.anova_pool.id
  
  # Generate client secret
  generate_secret = true
  
  # Authentication flows
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]
  
  # Token validity
  refresh_token_validity = 30 # days
  access_token_validity  = 1  # hours
  id_token_validity      = 1  # hours
  
  # Token revocation
  enable_token_revocation = true
  
  # Prevent user existence errors
  prevent_user_existence_errors = "ENABLED"
  
  # Callback and logout URLs
  callback_urls = ["https://${aws_lb.app.dns_name}/auth/callback"]
  logout_urls   = ["https://${aws_lb.app.dns_name}/"]
  
  # OAuth settings
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = ["email", "openid", "profile"]
  supported_identity_providers         = ["COGNITO"]
  
  # Read and write attributes
  read_attributes = [
    "email",
    "name",
    "phone_number"
  ]
  
  write_attributes = [
    "email",
    "name",
    "phone_number"
  ]
}

# AWS SES Email Identity for no-reply@anovasports.com
resource "aws_ses_email_identity" "no_reply" {
  email = "no-reply@anovasports.com"
}

# Add Cognito environment variables to the ECS task definition
locals {
  cognito_environment_variables = [
    {
      name  = "COGNITO_USER_POOL_ID"
      value = aws_cognito_user_pool.anova_pool.id
    },
    {
      name  = "COGNITO_CLIENT_ID"
      value = aws_cognito_user_pool_client.anova_client.id
    },
    {
      name  = "COGNITO_CLIENT_SECRET"
      value = aws_cognito_user_pool_client.anova_client.client_secret
    },
    {
      name  = "SESSION_SECRET_KEY"
      value = var.session_secret_key
    }
  ]
}

#################################################
# CONTAINER REGISTRY
#################################################

# ECR Repository
resource "aws_ecr_repository" "app" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

#################################################
# ECS CLUSTER
#################################################

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.app_name}"
  retention_in_days = 30
}

# Task Execution Role
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.app_name}-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Task Role
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.app_name}-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

#################################################
# SECURITY GROUPS
#################################################

# Security Group for ECS Tasks
resource "aws_security_group" "ecs_tasks" {
  name        = "${var.app_name}-ecs-tasks-sg"
  description = "Allow inbound traffic to ECS tasks"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    protocol    = "tcp"
    from_port   = var.container_port
    to_port     = var.container_port
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  name        = "${var.app_name}-rds-sg"
  description = "Allow inbound traffic to RDS from ECS tasks"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    protocol        = "tcp"
    from_port       = 5432
    to_port         = 5432
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Add a new ingress rule to allow external connections to RDS
resource "aws_security_group_rule" "allow_external_postgres" {
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.rds.id
  description       = "Allow external connections from anywhere"
}

#################################################
# DATABASE
#################################################

# RDS Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.app_name}-db-subnet-group"
  subnet_ids = data.aws_subnets.default.ids

  tags = {
    Name = "${var.app_name} DB Subnet Group"
  }
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "postgres" {
  identifier             = "${var.app_name}-db"
  engine                 = "postgres"
  engine_version         = "14"
  instance_class         = "db.t3.small"  # Upgraded from micro to small for better performance
  allocated_storage      = 20
  storage_type           = "gp2"
  db_name                = var.db_name
  username               = var.db_username
  password               = var.db_password
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  multi_az               = false
  publicly_accessible    = true  # Changed to true to allow external connections
  skip_final_snapshot    = true
  backup_retention_period = 7
  deletion_protection    = false
  parameter_group_name   = aws_db_parameter_group.postgres.name
}

# RDS Parameter Group
resource "aws_db_parameter_group" "postgres" {
  name   = "${var.app_name}-pg-params"
  family = "postgres14"

  parameter {
    name         = "max_connections"
    value        = "100"
    apply_method = "pending-reboot"
  }

  # Removed shared_buffers parameter to use RDS default value
  # RDS will automatically set shared_buffers based on instance memory
}

#################################################
# ECS TASK DEFINITION
#################################################

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = var.app_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"  # Increased from 512 to 1024 (1 vCPU)
  memory                   = "2048"  # Increased from 1024 to 2048 (2 GB)
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = var.app_name
      image     = "${aws_ecr_repository.app.repository_url}:${var.image_tag}"
      essential = true
      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]
      environment = concat([
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
        },
        {
          name  = "ANTHROPICS_API_KEY"
          value = var.anthropic_api_key
        },
        {
          name  = "AWS_REGION"
          value = var.aws_region
        },
        {
          name  = "SESSION_SECRET_KEY"
          value = var.session_secret_key
        },
        {
          name  = "AWS_ACCESS_KEY_ID"
          value = var.aws_access_key_id
        },
        {
          name  = "AWS_SECRET_ACCESS_KEY"
          value = var.aws_secret_access_key
        }
      ], local.cognito_environment_variables)
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.app.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/ || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60  # Give the application time to initialize the database
      }
    }
  ])
}

#################################################
# LOAD BALANCER
#################################################

# Elastic IP for the application
resource "aws_eip" "app" {
  domain = "vpc"
  tags = {
    Name = "${var.app_name}-eip"
  }
}

# Network Load Balancer with fixed IP
resource "aws_lb" "app" {
  name               = "${var.app_name}-nlb"
  internal           = false
  load_balancer_type = "network"

  subnet_mapping {
    subnet_id     = tolist(data.aws_subnets.default.ids)[0]
    allocation_id = aws_eip.app.id
  }

  tags = {
    Name = "${var.app_name}-nlb"
  }
}

# Target group for the NLB
resource "aws_lb_target_group" "app" {
  name        = "${var.app_name}-tg"
  port        = var.container_port
  protocol    = "TCP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"

  health_check {
    enabled             = true
    interval            = 30
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTP"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 6
  }
}

# Listener for the NLB
resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.app.arn
  port              = var.container_port
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

#################################################
# ECS SERVICE
#################################################

# ECS Service
resource "aws_ecs_service" "app" {
  name            = "${var.app_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.app_count
  launch_type     = "FARGATE"
  
  # Enable deployment circuit breaker
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets          = [tolist(data.aws_subnets.default.ids)[0]]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = var.app_name
    container_port   = var.container_port
  }

  depends_on = [aws_db_instance.postgres, aws_lb_listener.app]
}

#################################################
# AUTO SCALING
#################################################

# Auto Scaling Target
resource "aws_appautoscaling_target" "app" {
  max_capacity       = 5
  min_capacity       = var.app_count
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Auto Scaling Policy - CPU
resource "aws_appautoscaling_policy" "cpu" {
  name               = "${var.app_name}-cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.app.resource_id
  scalable_dimension = aws_appautoscaling_target.app.scalable_dimension
  service_namespace  = aws_appautoscaling_target.app.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Auto Scaling Policy - Memory
resource "aws_appautoscaling_policy" "memory" {
  name               = "${var.app_name}-memory-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.app.resource_id
  scalable_dimension = aws_appautoscaling_target.app.scalable_dimension
  service_namespace  = aws_appautoscaling_target.app.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value       = 70
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
