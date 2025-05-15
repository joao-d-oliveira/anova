variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "The AWS profile to use for deployment"
  type        = string
  default     = "anova"
}

variable "app_name" {
  description = "Name of the application"
  type        = string
  default     = "basketball-analysis"
}

variable "ecr_repository_name" {
  description = "Name of the ECR repository"
  type        = string
  default     = "basketball-analysis"
}

variable "image_tag" {
  description = "Tag of the Docker image to deploy"
  type        = string
  default     = "latest"
}

variable "container_port" {
  description = "Port exposed by the container"
  type        = number
  default     = 8000
}

# VPC and subnet IDs are now retrieved automatically using data sources
# These variables are kept for backward compatibility with terraform.tfvars
variable "vpc_id" {
  description = "ID of the VPC (now retrieved automatically using data sources)"
  type        = string
  default     = null
}

variable "subnet_ids" {
  description = "List of subnet IDs (now retrieved automatically using data sources)"
  type        = list(string)
  default     = null
}

variable "db_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  default     = "anova"
}

variable "db_username" {
  description = "Username for the PostgreSQL database"
  type        = string
  default     = "anova_user"
  sensitive   = true
}

variable "db_password" {
  description = "Password for the PostgreSQL database"
  type        = string
  sensitive   = true
}

variable "anthropic_api_key" {
  description = "Anthropic API key for Claude 3.7"
  type        = string
  sensitive   = true
}

variable "app_count" {
  description = "Number of ECS tasks to run"
  type        = number
  default     = 1
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "session_secret_key" {
  description = "Secret key for session encryption"
  type        = string
  sensitive   = true
}

variable "aws_access_key_id" {
  description = "AWS Access Key ID for the application to use"
  type        = string
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS Secret Access Key for the application to use"
  type        = string
  sensitive   = true
}
