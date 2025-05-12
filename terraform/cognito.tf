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

# Output the Cognito User Pool ID and Client ID
output "cognito_user_pool_id" {
  value       = aws_cognito_user_pool.anova_pool.id
  description = "The ID of the Cognito User Pool"
}

output "cognito_client_id" {
  value       = aws_cognito_user_pool_client.anova_client.id
  description = "The ID of the Cognito User Pool Client"
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