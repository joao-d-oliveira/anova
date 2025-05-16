#!/usr/bin/env python3
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import boto3
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("../config/.env")

# Add the parent directory to sys.path to import app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.cognito import register_user, confirm_registration, login
from app.database.connection import execute_query, get_or_create_user


class TestUserCreation(unittest.TestCase):
    """Test class for user creation functionality"""

    def setUp(self):
        """Set up test data"""
        # Test user data
        self.test_user = {
            "email": f"test_user_{os.urandom(4).hex()}@example.com",
            "password": "Test@Password123",
            "name": "Test User",
            "phone_number": "+15555555555",
            "school": "Test School",
            "role": "coach"
        }
        
        # Mock Cognito response for register_user
        self.mock_register_response = {
            "UserConfirmed": False,
            "UserSub": "test-user-sub-123",
            "CodeDeliveryDetails": {
                "Destination": self.test_user["email"],
                "DeliveryMedium": "EMAIL",
                "AttributeName": "email"
            }
        }
        
        # Mock Cognito response for login
        self.mock_login_response = {
            "IdToken": "mock-id-token",
            "AccessToken": "mock-access-token",
            "RefreshToken": "mock-refresh-token",
            "ExpiresIn": 3600
        }

    @patch('app.services.cognito.cognito_idp')
    def test_register_user(self, mock_cognito):
        """Test user registration"""
        # Configure the mock to return a successful response
        mock_cognito.sign_up.return_value = self.mock_register_response
        
        # Call the register_user function
        response = register_user(
            self.test_user["email"],
            self.test_user["password"],
            self.test_user["name"],
            self.test_user["phone_number"],
            self.test_user["school"],
            self.test_user["role"]
        )
        
        # Verify the response
        self.assertEqual(response["UserConfirmed"], False)
        self.assertEqual(response["UserSub"], "test-user-sub-123")
        self.assertEqual(response["CodeDeliveryDetails"]["Destination"], self.test_user["email"])
        
        # Verify the cognito_idp.sign_up was called with the correct parameters
        mock_cognito.sign_up.assert_called_once()
        call_args = mock_cognito.sign_up.call_args[1]
        self.assertEqual(call_args["Username"], self.test_user["email"])
        self.assertEqual(call_args["Password"], self.test_user["password"])
        
        # Verify user attributes were passed correctly
        user_attributes = call_args["UserAttributes"]
        name_attr = next((attr for attr in user_attributes if attr["Name"] == "name"), None)
        phone_attr = next((attr for attr in user_attributes if attr["Name"] == "phone_number"), None)
        
        self.assertIsNotNone(name_attr)
        self.assertEqual(name_attr["Value"], self.test_user["name"])
        self.assertIsNotNone(phone_attr)
        self.assertEqual(phone_attr["Value"], self.test_user["phone_number"])

    @patch('app.services.cognito.cognito_idp')
    def test_confirm_registration(self, mock_cognito):
        """Test confirmation of user registration"""
        # Configure the mock to return a successful response
        mock_cognito.confirm_sign_up.return_value = {}
        
        # Call the confirm_registration function
        response = confirm_registration(self.test_user["email"], "123456")
        
        # Verify the cognito_idp.confirm_sign_up was called with the correct parameters
        mock_cognito.confirm_sign_up.assert_called_once()
        call_args = mock_cognito.confirm_sign_up.call_args[1]
        self.assertEqual(call_args["Username"], self.test_user["email"])
        self.assertEqual(call_args["ConfirmationCode"], "123456")

    @patch('app.services.cognito.cognito_idp')
    @patch('app.services.cognito.verify_token')
    def test_login_and_database_creation(self, mock_verify_token, mock_cognito):
        """Test user login and database record creation"""
        # Configure the mocks
        mock_cognito.initiate_auth.return_value = {"AuthenticationResult": self.mock_login_response}
        mock_verify_token.return_value = {
            "sub": "test-user-sub-123",
            "email": self.test_user["email"],
            "name": self.test_user["name"],
            "phone_number": self.test_user["phone_number"],
            "custom:school": self.test_user["school"],
            "custom:role": self.test_user["role"]
        }
        
        try:
            # Call the login function
            response = login(self.test_user["email"], self.test_user["password"])
            
            # Verify the response
            self.assertEqual(response["IdToken"], "mock-id-token")
            self.assertEqual(response["AccessToken"], "mock-access-token")
            self.assertEqual(response["RefreshToken"], "mock-refresh-token")
            
            # Verify the cognito_idp.initiate_auth was called with the correct parameters
            mock_cognito.initiate_auth.assert_called_once()
            call_args = mock_cognito.initiate_auth.call_args[1]
            self.assertEqual(call_args["AuthFlow"], "USER_PASSWORD_AUTH")
            auth_params = call_args["AuthParameters"]
            self.assertEqual(auth_params["USERNAME"], self.test_user["email"])
            self.assertEqual(auth_params["PASSWORD"], self.test_user["password"])
        except Exception as e:
            self.fail(f"Login function raised exception: {str(e)}")
        
        # Test database user creation
        try:
            user_id = get_or_create_user(
                "test-user-sub-123",
                self.test_user["email"],
                self.test_user["name"]
            )
            
            # Verify the user was created in the database
            self.assertIsNotNone(user_id)
            
            # Query the database to verify the user exists
            query = "SELECT * FROM users WHERE cognito_id = %s"
            result = execute_query(query, ("test-user-sub-123",))
            
            # Verify the user record
            if result:
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0]["email"], self.test_user["email"])
                self.assertEqual(result[0]["name"], self.test_user["name"])
            else:
                self.fail("User not found in database")
        except Exception as e:
            self.fail(f"Database operation failed: {str(e)}")

    def test_password_validation(self):
        """Test password validation"""
        from app.routers.auth import validate_password
        
        # Test valid password
        is_valid, _ = validate_password("Test@Password123")
        self.assertTrue(is_valid)
        
        # Test password too short
        is_valid, error = validate_password("Short1!")
        self.assertFalse(is_valid)
        self.assertIn("at least 8 characters", error)
        
        # Test password without uppercase
        is_valid, error = validate_password("test@password123")
        self.assertFalse(is_valid)
        self.assertIn("uppercase", error)
        
        # Test password without lowercase
        is_valid, error = validate_password("TEST@PASSWORD123")
        self.assertFalse(is_valid)
        self.assertIn("lowercase", error)
        
        # Test password without digits
        is_valid, error = validate_password("Test@Password")
        self.assertFalse(is_valid)
        self.assertIn("numeric", error)
        
        # Test password without symbols
        is_valid, error = validate_password("TestPassword123")
        self.assertFalse(is_valid)
        self.assertIn("symbol", error)


if __name__ == '__main__':
    unittest.main()
