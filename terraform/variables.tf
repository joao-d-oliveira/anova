variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
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

variable "vpc_id" {
  description = "ID of the VPC where resources will be deployed"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs where resources will be deployed"
  type        = list(string)
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
