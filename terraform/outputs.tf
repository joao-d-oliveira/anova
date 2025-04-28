output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.app.name
}

output "task_definition_arn" {
  description = "ARN of the task definition"
  value       = aws_ecs_task_definition.app.arn
}

output "rds_endpoint" {
  description = "Endpoint of the RDS instance"
  value       = aws_db_instance.postgres.address
}

output "rds_port" {
  description = "Port of the RDS instance"
  value       = aws_db_instance.postgres.port
}

output "cloudwatch_log_group" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.app.name
}

output "aws_region" {
  description = "The AWS region where resources are deployed"
  value       = var.aws_region
}

output "app_url_info" {
  description = "Information on how to access the application"
  value       = "The application is accessible at http://<task-public-ip>:${var.container_port}"
}

output "get_app_host_command" {
  description = "Command to get the current host IP address of the application"
  value       = "aws --profile anova --region ${var.aws_region} ec2 describe-network-interfaces --filters Name=description,Values='*${aws_ecs_cluster.main.name}*' --query 'NetworkInterfaces[?Status==`in-use`].Association.PublicIp' --output text"
}

output "access_app_command" {
  description = "One-liner command to get and open the application URL"
  value       = "open http://$(aws --profile anova --region ${var.aws_region} ec2 describe-network-interfaces --filters Name=description,Values='*${aws_ecs_cluster.main.name}*' --query 'NetworkInterfaces[?Status==`in-use`].Association.PublicIp' --output text):${var.container_port}"
}
