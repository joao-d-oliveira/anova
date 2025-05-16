#!/usr/bin/env python3
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("../config/.env")

# Add the parent directory to sys.path to import app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.anthropic_api import analyze_team_pdf, encode_pdf_to_base64


class TestPDFProcessing(unittest.TestCase):
    """Test class for PDF processing functionality"""

    def setUp(self):
        """Set up test data"""
        # Define paths to test PDF files
        self.team_pdf_path = os.path.join(
            os.path.dirname(__file__), 
            "..", "data", "input_samples", 
            "SCARSDALE Last 5 games individual stats.pdf"
        )
        self.opponent_pdf_path = os.path.join(
            os.path.dirname(__file__), 
            "..", "data", "input_samples", 
            "ARLINGTON Last 5 games INDIVIDUAL stats.pdf"
        )
        
        # Verify test files exist
        if not os.path.exists(self.team_pdf_path):
            self.fail(f"Test file not found: {self.team_pdf_path}")
        if not os.path.exists(self.opponent_pdf_path):
            self.fail(f"Test file not found: {self.opponent_pdf_path}")
        
        # Mock Anthropic API response
        self.mock_team_analysis = {
            "team_name": "Scarsdale",
            "team_record": "15-5",
            "team_ranking": "3rd in Division",
            "team_stats": {
                "PPG": 68.5,
                "FG%": "45.2%",
                "3FG%": "36.8%",
                "FT%": "72.5%",
                "REB": 32.4,
                "AST": 14.2,
                "STL": 7.8,
                "BLK": 3.5,
                "TO": 11.3
            },
            "team_strengths": [
                "Strong perimeter shooting",
                "Balanced scoring attack",
                "Good ball movement"
            ],
            "team_weaknesses": [
                "Inconsistent rebounding",
                "Turnover prone under pressure",
                "Defensive lapses"
            ],
            "players": [
                {
                    "name": "John Smith",
                    "number": "23",
                    "position": "G",
                    "stats": {
                        "PPG": 18.5,
                        "RPG": 4.2,
                        "APG": 5.7,
                        "FG%": "48.3%",
                        "3FG%": "41.2%",
                        "FT%": "85.7%"
                    }
                }
            ]
        }

    def test_pdf_encoding(self):
        """Test PDF encoding to base64"""
        # Encode the PDF file
        encoded_pdf = encode_pdf_to_base64(self.team_pdf_path)
        
        # Verify the encoding is not empty
        self.assertIsNotNone(encoded_pdf)
        self.assertTrue(len(encoded_pdf) > 0)
        
        # Verify it's a valid base64 string
        import base64
        try:
            decoded = base64.b64decode(encoded_pdf)
            self.assertTrue(len(decoded) > 0)
        except Exception as e:
            self.fail(f"Failed to decode base64 string: {e}")

    @patch('app.services.anthropic_api.client')
    def test_team_pdf_analysis(self, mock_client):
        """Test team PDF analysis"""
        # Configure the mock to return a successful response
        mock_message = MagicMock()
        mock_message.content = [MagicMock()]
        mock_message.content[0].text = json.dumps(self.mock_team_analysis)
        mock_client.messages.create.return_value = mock_message
        
        # Call the analyze_team_pdf function
        result = analyze_team_pdf(self.team_pdf_path, is_our_team=True)
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result["team_name"], "Scarsdale")
        self.assertEqual(result["team_record"], "15-5")
        
        # Verify team stats
        self.assertIn("team_stats", result)
        self.assertEqual(result["team_stats"]["PPG"], 68.5)
        self.assertEqual(result["team_stats"]["FG%"], "45.2%")
        
        # Verify players
        self.assertIn("players", result)
        self.assertTrue(len(result["players"]) > 0)
        
        # Verify the Anthropic API was called with the correct parameters
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args[1]
        self.assertEqual(call_args["model"], "claude-3-7-sonnet-20250219")
        self.assertEqual(call_args["temperature"], 0.0)
        self.assertIn("system", call_args)
        self.assertIn("messages", call_args)

    @patch('app.services.anthropic_api.client')
    def test_opponent_pdf_analysis(self, mock_client):
        """Test opponent PDF analysis"""
        # Configure the mock to return a successful response
        mock_message = MagicMock()
        mock_message.content = [MagicMock()]
        mock_message.content[0].text = json.dumps(self.mock_team_analysis)
        mock_client.messages.create.return_value = mock_message
        
        # Call the analyze_team_pdf function
        result = analyze_team_pdf(self.opponent_pdf_path, is_our_team=False)
        
        # Verify the result
        self.assertIsNotNone(result)
        
        # Verify the Anthropic API was called with the correct parameters
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args[1]
        self.assertEqual(call_args["model"], "claude-3-7-sonnet-20250219")
        
        # Verify the system prompt indicates this is an opponent team
        self.assertIn("system", call_args)
        self.assertIn("opponent team", call_args["system"])

    @patch('app.services.anthropic_api.client')
    def test_error_handling(self, mock_client):
        """Test error handling in PDF analysis"""
        # Configure the mock to raise an exception
        mock_client.messages.create.side_effect = Exception("API Error")
        
        # Call the analyze_team_pdf function
        result = analyze_team_pdf(self.team_pdf_path, is_our_team=True)
        
        # Verify the result is an empty dict on error
        self.assertEqual(result, {})

    @patch('app.services.anthropic_api.client')
    def test_invalid_json_response(self, mock_client):
        """Test handling of invalid JSON response"""
        # Configure the mock to return an invalid JSON response
        mock_message = MagicMock()
        mock_message.content = [MagicMock()]
        mock_message.content[0].text = "This is not valid JSON"
        mock_client.messages.create.return_value = mock_message
        
        # Call the analyze_team_pdf function
        result = analyze_team_pdf(self.team_pdf_path, is_our_team=True)
        
        # Verify the result is an empty dict on error
        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
