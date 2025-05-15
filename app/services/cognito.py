import os
import boto3
import json
import base64
import time
from typing import Dict, Any, Optional
from jose import jwk, jwt
from jose.utils import base64url_decode
import logging
from app.config import Config

# Set up logging
logger = logging.getLogger(__name__)

# Initialize configuration
config = Config()

# Get Cognito configuration
REGION = config.aws_region
USER_POOL_ID = config.cognito_user_pool_id
CLIENT_ID = config.cognito_client_id
CLIENT_SECRET = config.cognito_client_secret

logger.info(f"Cognito configuration loaded - Region: {REGION}, User Pool ID: {USER_POOL_ID}")

# Initialize Cognito Identity Provider client
try:
    # Try to use the default credentials provider chain
    cognito_idp = boto3.client('cognito-idp', region_name=REGION)
except Exception as e:
    print(f"Error initializing Cognito client with default credentials: {str(e)}")
    # Fall back to using the profile if available
    try:
        import botocore.session
        from botocore.config import Config
        
        # Load the default configuration
        session = botocore.session.get_session()
        config = Config(region_name=REGION)
        
        # Create the client with the session
        cognito_idp = boto3.client('cognito-idp', config=config)
        print("Successfully initialized Cognito client with session configuration")
    except Exception as e2:
        print(f"Error initializing Cognito client with session configuration: {str(e2)}")
        # Last resort: try without any profile
        cognito_idp = boto3.client('cognito-idp', region_name=REGION, aws_access_key_id=None, aws_secret_access_key=None)

def get_cognito_public_keys():
    """
    Get the public keys from AWS Cognito for JWT verification
    
    Returns:
        Dict of public keys
    """
    if not USER_POOL_ID:
        print("ERROR: COGNITO_USER_POOL_ID environment variable is not set")
        print(f"Current environment variables: REGION={REGION}, USER_POOL_ID={USER_POOL_ID}, CLIENT_ID={CLIENT_ID}")
        return {}
        
    keys_url = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"
    print(f"Attempting to fetch Cognito public keys from: {keys_url}")
    
    import urllib.request
    try:
        with urllib.request.urlopen(keys_url) as f:
            response = f.read()
        keys = json.loads(response.decode('utf-8'))['keys']
        print(f"Successfully retrieved {len(keys)} Cognito public keys")
        return {key['kid']: key for key in keys}
    except urllib.error.HTTPError as e:
        print(f"ERROR: Failed to fetch Cognito public keys. HTTP Error {e.code}: {e.reason}")
        print(f"Please verify that the USER_POOL_ID '{USER_POOL_ID}' is correct and exists in region '{REGION}'")
        print(f"Current environment variables: REGION={REGION}, USER_POOL_ID={USER_POOL_ID}, CLIENT_ID={CLIENT_ID}")
        # Return empty dict to allow application to start with limited functionality
        return {}
    except Exception as e:
        print(f"ERROR: Failed to fetch Cognito public keys: {str(e)}")
        print(f"Current environment variables: REGION={REGION}, USER_POOL_ID={USER_POOL_ID}, CLIENT_ID={CLIENT_ID}")
        return {}

# Cache the public keys
try:
    cognito_public_keys = get_cognito_public_keys()
    if not cognito_public_keys:
        print("WARNING: No Cognito public keys were retrieved. Authentication will not work properly.")
except Exception as e:
    print(f"ERROR initializing Cognito public keys: {str(e)}")
    cognito_public_keys = {}

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify a JWT token from AWS Cognito
    
    Args:
        token: JWT token
        
    Returns:
        Dict containing user information
        
    Raises:
        Exception: If token is invalid
    """
    # Get the header from the token
    header = jwt.get_unverified_header(token)
    
    # Get the key id from the header
    kid = header['kid']
    
    # Get the public key for this kid
    if kid not in cognito_public_keys:
        # Refresh the public keys
        cognito_public_keys.update(get_cognito_public_keys())
        if kid not in cognito_public_keys:
            raise Exception('Public key not found')
    
    public_key = cognito_public_keys[kid]
    
    # Get the last two sections of the token
    message, encoded_signature = token.rsplit('.', 1)
    
    # Decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    
    # Verify the signature
    public_key_obj = jwk.construct(public_key)
    if not public_key_obj.verify(message.encode('utf-8'), decoded_signature):
        raise Exception('Signature verification failed')
    
    # Verify the claims
    claims = jwt.get_unverified_claims(token)
    if time.time() > claims['exp']:
        raise Exception('Token is expired')
    
    if claims['aud'] != CLIENT_ID:
        raise Exception('Token was not issued for this audience')
    
    return claims

# Function to get fresh configuration
def get_fresh_config():
    """
    Get fresh configuration values
    
    Returns:
        Dict containing configuration values
    """
    # Create a new Config instance to get fresh values
    fresh_config = Config()
    
    return {
        "REGION": fresh_config.aws_region,
        "USER_POOL_ID": fresh_config.cognito_user_pool_id,
        "CLIENT_ID": fresh_config.cognito_client_id,
        "CLIENT_SECRET": fresh_config.cognito_client_secret
    }

def register_user(email: str, password: str, name: str, phone_number: str, school: str, role: str) -> Dict[str, Any]:
    """
    Register a new user in AWS Cognito
    
    Args:
        email: User's email
        password: User's password
        name: User's full name
        phone_number: User's phone number
        school: User's school
        role: User's role
        
    Returns:
        Dict containing registration response
        
    Raises:
        Exception: If registration fails
    """
    try:
        # Get fresh configuration
        fresh_config = get_fresh_config()
        client_id = fresh_config["CLIENT_ID"]
        client_secret = fresh_config["CLIENT_SECRET"]
        
        # Calculate secret hash with fresh credentials
        secret_hash = calculate_secret_hash(email, client_id, client_secret)
        
        # Only include standard attributes that are allowed by the client
        user_attributes = [
            {
                'Name': 'name',
                'Value': name
            },
            {
                'Name': 'phone_number',
                'Value': phone_number
            }
        ]
        
        response = cognito_idp.sign_up(
            ClientId=client_id,
            SecretHash=secret_hash,
            Username=email,
            Password=password,
            UserAttributes=user_attributes
        )
        return response
    except Exception as e:
        print(f"Error registering user: {e}")
        raise

def confirm_registration(email: str, confirmation_code: str) -> Dict[str, Any]:
    """
    Confirm user registration with verification code
    
    Args:
        email: User's email
        confirmation_code: Verification code sent to user's email
        
    Returns:
        Dict containing confirmation response
        
    Raises:
        Exception: If confirmation fails
    """
    try:
        # Get fresh configuration
        fresh_config = get_fresh_config()
        client_id = fresh_config["CLIENT_ID"]
        client_secret = fresh_config["CLIENT_SECRET"]
        
        # Calculate secret hash with fresh credentials
        secret_hash = calculate_secret_hash(email, client_id, client_secret)
        
        response = cognito_idp.confirm_sign_up(
            ClientId=client_id,
            SecretHash=secret_hash,
            Username=email,
            ConfirmationCode=confirmation_code
        )
        return response
    except Exception as e:
        print(f"Error confirming registration: {e}")
        raise

def login(email: str, password: str) -> Dict[str, Any]:
    """
    Authenticate a user with AWS Cognito

    Args:
        email: User's email
        password: User's password

    Returns:
        Dict containing authentication tokens

    Raises:
        Exception: If authentication fails
    """
    try:
        print(f"Login attempt for user: {email}")
        
        # Get fresh configuration
        fresh_config = get_fresh_config()
        client_id = fresh_config["CLIENT_ID"]
        client_secret = fresh_config["CLIENT_SECRET"]
        
        print(f"Using CLIENT_ID: {client_id}")
        
        # Check if CLIENT_SECRET is available
        if not client_secret:
            print("WARNING: COGNITO_CLIENT_SECRET is not set in environment variables")
            raise ValueError("Authentication configuration is incomplete: Missing client secret")
        
        # Use the fresh client secret for calculating the hash
        secret_hash = calculate_secret_hash(email, client_id, client_secret)
        if secret_hash:
            print(f"Generated SECRET_HASH: {secret_hash[:10]}...")
        else:
            print("WARNING: Could not generate SECRET_HASH")
            raise ValueError("Authentication configuration is incomplete: Could not generate secret hash")
        
        response = cognito_idp.initiate_auth(
            ClientId=client_id,  # Use the fresh client_id
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password,
                'SECRET_HASH': secret_hash
            }
        )
        
        if 'AuthenticationResult' not in response:
            print(f"Authentication response missing AuthenticationResult: {response}")
            raise ValueError("Invalid authentication response format")
            
        print("Authentication successful")
        return response['AuthenticationResult']
    except ValueError as e:
        # Re-raise our custom validation errors
        print(f"Authentication configuration error: {str(e)}")
        raise
    except Exception as e:
        print(f"Error authenticating user: {e}")
        print(f"Error type: {type(e)}")
        print(f"Error args: {e.args}")
        # Raise a more user-friendly error
        raise ValueError(f"Login failed: {str(e)}")

def refresh_token(refresh_token: str) -> Dict[str, Any]:
    """
    Refresh authentication tokens
    
    Args:
        refresh_token: Refresh token from previous authentication
        
    Returns:
        Dict containing new authentication tokens
        
    Raises:
        Exception: If token refresh fails
    """
    try:
        # Get fresh configuration
        fresh_config = get_fresh_config()
        client_id = fresh_config["CLIENT_ID"]
        client_secret = fresh_config["CLIENT_SECRET"]
        
        # Check if CLIENT_SECRET is available
        if not client_secret:
            print("WARNING: COGNITO_CLIENT_SECRET is not set in environment variables")
            raise ValueError("Authentication configuration is incomplete: Missing client secret")
            
        username = get_username_from_token(refresh_token)
        if not username:
            print("WARNING: Could not extract username from refresh token")
            raise ValueError("Invalid refresh token: Could not extract username")
            
        secret_hash = calculate_secret_hash(username, client_id, client_secret)
        if not secret_hash:
            print("WARNING: Could not generate SECRET_HASH")
            raise ValueError("Authentication configuration is incomplete: Could not generate secret hash")
        
        response = cognito_idp.initiate_auth(
            ClientId=client_id,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token,
                'SECRET_HASH': secret_hash
            }
        )
        
        if 'AuthenticationResult' not in response:
            print(f"Token refresh response missing AuthenticationResult: {response}")
            raise ValueError("Invalid token refresh response format")
            
        return response['AuthenticationResult']
    except ValueError as e:
        # Re-raise our custom validation errors
        print(f"Token refresh configuration error: {str(e)}")
        raise
    except Exception as e:
        print(f"Error refreshing token: {e}")
        # Raise a more user-friendly error
        raise ValueError(f"Token refresh failed: {str(e)}")

def forgot_password(email: str) -> Dict[str, Any]:
    """
    Initiate password reset process
    
    Args:
        email: User's email
        
    Returns:
        Dict containing response
        
    Raises:
        Exception: If password reset initiation fails
    """
    try:
        # Get fresh configuration
        fresh_config = get_fresh_config()
        client_id = fresh_config["CLIENT_ID"]
        client_secret = fresh_config["CLIENT_SECRET"]
        
        # Calculate secret hash with fresh credentials
        secret_hash = calculate_secret_hash(email, client_id, client_secret)
        
        response = cognito_idp.forgot_password(
            ClientId=client_id,
            SecretHash=secret_hash,
            Username=email
        )
        return response
    except Exception as e:
        print(f"Error initiating password reset: {e}")
        raise

def confirm_forgot_password(email: str, confirmation_code: str, new_password: str) -> Dict[str, Any]:
    """
    Complete password reset process
    
    Args:
        email: User's email
        confirmation_code: Verification code sent to user's email
        new_password: New password
        
    Returns:
        Dict containing response
        
    Raises:
        Exception: If password reset confirmation fails
    """
    try:
        # Get fresh configuration
        fresh_config = get_fresh_config()
        client_id = fresh_config["CLIENT_ID"]
        client_secret = fresh_config["CLIENT_SECRET"]
        
        # Calculate secret hash with fresh credentials
        secret_hash = calculate_secret_hash(email, client_id, client_secret)
        
        response = cognito_idp.confirm_forgot_password(
            ClientId=client_id,
            SecretHash=secret_hash,
            Username=email,
            ConfirmationCode=confirmation_code,
            Password=new_password
        )
        return response
    except Exception as e:
        print(f"Error confirming password reset: {e}")
        raise

def calculate_secret_hash(username: str, client_id: str = None, client_secret: str = None) -> str:
    """
    Calculate the secret hash for Cognito API calls
    
    Args:
        username: User's username (email)
        client_id: Optional client ID to use (defaults to global CLIENT_ID)
        client_secret: Optional client secret to use (defaults to global CLIENT_SECRET)
        
    Returns:
        Secret hash string
    """
    # Use provided values or fall back to globals
    actual_client_id = client_id if client_id is not None else CLIENT_ID
    actual_client_secret = client_secret if client_secret is not None else CLIENT_SECRET
    
    if not actual_client_secret:
        print("WARNING: CLIENT_SECRET is not set")
        return None
        
    import hmac
    import hashlib
    
    # Print debug information
    print(f"Calculating secret hash for username: {username}")
    print(f"Using CLIENT_ID: {actual_client_id}")
    print(f"Using CLIENT_SECRET: {actual_client_secret[:5]}...{actual_client_secret[-5:]}")
    
    # Ensure username and CLIENT_ID are strings
    username_str = str(username)
    client_id_str = str(actual_client_id)
    
    message = username_str + client_id_str
    print(f"Message to hash: {message}")
    
    try:
        dig = hmac.new(
            key=actual_client_secret.encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        result = base64.b64encode(dig).decode()
        print(f"Generated hash: {result[:10]}...")
        return result
    except Exception as e:
        print(f"Error calculating secret hash: {str(e)}")
        raise

def get_username_from_token(token: str) -> Optional[str]:
    """
    Extract username from a JWT token
    
    Args:
        token: JWT token
        
    Returns:
        Username (email) or None if not found
    """
    try:
        claims = jwt.get_unverified_claims(token)
        return claims.get('email') or claims.get('cognito:username')
    except:
        return None

def get_user(email: str) -> Dict[str, Any]:
    """
    Get user information from AWS Cognito
    
    Args:
        email: User's email
        
    Returns:
        Dict containing user information
        
    Raises:
        Exception: If user retrieval fails
    """
    try:
        response = cognito_idp.admin_get_user(
            UserPoolId=USER_POOL_ID,
            Username=email
        )
        return response
    except Exception as e:
        print(f"Error getting user: {e}")
        raise

def logout(access_token: str) -> Dict[str, Any]:
    """
    Logout a user by revoking their tokens
    
    Args:
        access_token: Access token from authentication
        
    Returns:
        Dict containing response
        
    Raises:
        Exception: If logout fails
    """
    try:
        response = cognito_idp.global_sign_out(
            AccessToken=access_token
        )
        return response
    except Exception as e:
        print(f"Error logging out user: {e}")
        raise
