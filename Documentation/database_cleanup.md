# Database Cleanup

This document summarizes the changes made to clean up the database configuration and use only the AWS RDS PostgreSQL database.

## Changes Made

### 1. Updated docker-compose.yml

- Removed the local PostgreSQL database service (`db`)
- Updated the `app` service environment variables to use the AWS RDS database:
  ```yaml
  environment:
    - DB_HOST=basketball-analysis-db.cgdoswe6ytxj.us-east-1.rds.amazonaws.com
    - DB_NAME=anova
    - DB_USER=anova_user
    - DB_PASSWORD=9lvbbiYkspuG8EKW5gHnU73KZyaCNu3IrSUM6jaB874=
    - ANTHROPICS_API_KEY=${ANTHROPICS_API_KEY}
    - AWS_REGION=${AWS_REGION}
    - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
    - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
  ```
- Removed the `depends_on` section that referenced the local database
- Removed the `volumes` section that defined the PostgreSQL data volume

### 2. Updated app/entrypoint.sh

- Kept the wait-for-PostgreSQL loop but removed the `--drop-tables` flag from the database initialization command
- This prevents accidental data loss in production while still ensuring the database is ready before starting the application

### 3. Updated terraform/main.tf

- Modified the RDS instance to be publicly accessible by setting `publicly_accessible = true`
- Updated the RDS security group to allow connections from anywhere (0.0.0.0/0)
- This allows direct connections to the RDS database from outside the VPC

### 4. Created terraform/deploy_rds_changes.sh

- Created a script to deploy the Terraform changes to make the RDS database publicly accessible
- The script outputs the RDS connection details after deployment

### 5. Updated README.md

- Added a new "Database Configuration" section explaining the AWS RDS setup
- Updated the Quick Start with Docker section to include AWS environment variables
- Updated the Manual Installation section to use the AWS RDS database connection details
- Removed the step to set up a local PostgreSQL database

## AWS RDS Database Details

- **Endpoint**: basketball-analysis-db.cgdoswe6ytxj.us-east-1.rds.amazonaws.com
- **Port**: 5432
- **Database Name**: anova
- **Username**: anova_user
- **Password**: 9lvbbiYkspuG8EKW5gHnU73KZyaCNu3IrSUM6jaB874=
- **Instance Type**: db.t3.small
- **Engine**: PostgreSQL 14
- **Storage**: 20GB gp2
- **Multi-AZ**: Disabled
- **Publicly Accessible**: Yes (changed from No)

## Benefits of Using AWS RDS

1. **Managed Service**: AWS handles backups, patching, and maintenance
2. **Scalability**: Easy to scale up or down based on demand
3. **High Availability**: Option to enable Multi-AZ for production environments
4. **Monitoring**: Built-in monitoring and alerting through CloudWatch
5. **Backup and Recovery**: Automated backups and point-in-time recovery
6. **Centralized Database**: Both local development and AWS deployment use the same database

## Security Considerations

Making the RDS database publicly accessible introduces security risks:

1. The database is exposed to the internet, making it a potential target for attacks
2. Proper security measures should be implemented:
   - Use strong passwords
   - Limit access to specific IP addresses if possible
   - Enable SSL for database connections
   - Regularly monitor database access logs
   - Consider using a VPN for secure access

## Next Steps

1. Deploy the Terraform changes using the `terraform/deploy_rds_changes.sh` script
2. Update the `.env` file with the RDS connection details
3. Test the application with the AWS RDS database to ensure everything works correctly
4. Consider implementing additional security measures
5. Set up automated backups and monitoring for the database
