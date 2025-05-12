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

output "elastic_ip" {
  description = "Elastic IP address assigned to the application"
  value       = aws_eip.app.public_ip
}

output "nlb_dns_name" {
  description = "DNS name of the Network Load Balancer"
  value       = aws_lb.app.dns_name
}

output "app_url_info" {
  description = "Information on how to access the application"
  value       = "The application is accessible at http://${aws_eip.app.public_ip}:${var.container_port} or via the NLB at http://${aws_lb.app.dns_name}:${var.container_port}"
}

output "get_app_host_command" {
  description = "Command to get the current host IP address of the application"
  value       = "echo ${aws_eip.app.public_ip}"
}

output "access_app_command" {
  description = "One-liner command to open the application URL"
  value       = "open http://${aws_eip.app.public_ip}:${var.container_port}"
}
