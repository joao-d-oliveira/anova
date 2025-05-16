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

from app.services.anthropic_api import post_process_team_stats


class TestTeamDataProcessing(unittest.TestCase):
    """Test class for team data processing functionality"""

    def setUp(self):
        """Set up test data"""
        # Sample team analysis with incomplete stats
        self.incomplete_team_analysis = {
            "team_name": "Test Team",
            "team_record": "10-5",
            "team_stats": {
                "PPG": 65.0,
                "FG%": "42.5%",
                # Missing 3FG%, FT%, etc.
            },
            "players": [
                {
                    "name": "Player 1",
                    "number": "10",
                    "position": "G",
                    "stats": {
                        "GP": 15,
                        "PPG": 18.5,
                        "FGM": 120,
                        "FGA": 250,
                        "2FGM": 80,
                        "2FGA": 150,
                        "3FGM": 40,
                        "3FGA": 100,
                        "FTM": 50,
                        "FTA": 60,
                        "REB": 75,
                        "OREB": 25,
                        "DREB": 50,
                        "AST": 60,
                        "STL": 30,
                        "BLK": 15,
                        "TO": 30
                    }
                },
                {
                    "name": "Player 2",
                    "number": "20",
                    "position": "F",
                    "stats": {
                        "GP": 15,
                        "PPG": 12.0,
                        "FGM": 90,
                        "FGA": 200,
                        "2FGM": 70,
                        "2FGA": 140,
                        "3FGM": 20,
                        "3FGA": 60,
                        "FTM": 30,
                        "FTA": 40,
                        "REB": 120,
                        "OREB": 50,
                        "DREB": 70,
                        "AST": 30,
                        "STL": 20,
                        "BLK": 25,
                        "TO": 15
                    }
                }
            ]
        }
        
        # Sample team analysis with missing team_stats
        self.missing_team_stats_analysis = {
            "team_name": "Missing Stats Team",
            "team_record": "8-7",
            "players": [
                {
                    "name": "Player 1",
                    "number": "10",
                    "position": "G",
                    "stats": {
                        "GP": 15,
                        "PPG": 18.5,
                        "FGM": 120,
                        "FGA": 250,
                        "2FGM": 80,
                        "2FGA": 150,
                        "3FGM": 40,
                        "3FGA": 100,
                        "FTM": 50,
                        "FTA": 60,
                        "REB": 75,
                        "OREB": 25,
                        "DREB": 50,
                        "AST": 60,
                        "STL": 30,
                        "BLK": 15,
                        "TO": 30
                    }
                }
            ]
        }
        
        # Sample team analysis with missing player stats
        self.missing_player_stats_analysis = {
            "team_name": "Missing Player Stats Team",
            "team_record": "12-3",
            "team_stats": {
                "PPG": 70.0,
                "FG%": "45.0%",
                "3FG%": "38.0%",
                "FT%": "75.0%"
            },
            "players": [
                {
                    "name": "Player 1",
                    "number": "10",
                    "position": "G",
                    "stats": {
                        "PPG": 18.5,
                        "RPG": 5.0,
                        "APG": 4.0,
                        "SPG": 2.0,
                        "BPG": 1.0,
                        "TOPG": 2.0
                    }
                }
            ]
        }

    def test_post_process_incomplete_stats(self):
        """Test post-processing of incomplete team statistics"""
        # Process the incomplete team analysis
        processed_analysis = post_process_team_stats(self.incomplete_team_analysis)
        
        # Verify the team_stats dictionary exists
        self.assertIn("team_stats", processed_analysis)
        
        # Verify the original stats are preserved
        self.assertEqual(processed_analysis["team_stats"]["PPG"], 65.0)
        self.assertEqual(processed_analysis["team_stats"]["FG%"], "46.7%")
        
        # Verify calculated field goal percentages
        if "FG%" not in self.incomplete_team_analysis["team_stats"]:
            self.assertIn("FG%", processed_analysis["team_stats"])
        
        # Verify calculated 3-point percentages
        self.assertIn("3FG%", processed_analysis["team_stats"])
        
        # Verify calculated free throw percentages
        self.assertIn("FT%", processed_analysis["team_stats"])
        
        # Verify calculated assist-to-turnover ratio
        self.assertIn("A/TO", processed_analysis["team_stats"])
        
        # Verify calculated rebounds
        self.assertIn("REB", processed_analysis["team_stats"])
        self.assertIn("OREB", processed_analysis["team_stats"])
        self.assertIn("DREB", processed_analysis["team_stats"])
        
        # Verify calculated assists, steals, blocks
        self.assertIn("AST", processed_analysis["team_stats"])
        self.assertIn("STL", processed_analysis["team_stats"])
        self.assertIn("BLK", processed_analysis["team_stats"])

    def test_post_process_missing_team_stats(self):
        """Test post-processing when team_stats is missing"""
        # Process the team analysis with missing team_stats
        processed_analysis = post_process_team_stats(self.missing_team_stats_analysis)
        
        # Verify the team_stats dictionary was created
        self.assertIn("team_stats", processed_analysis)
        
        # Verify calculated field goal percentages
        self.assertIn("FG%", processed_analysis["team_stats"])
        
        # Verify calculated 3-point percentages
        self.assertIn("3FG%", processed_analysis["team_stats"])
        
        # Verify calculated free throw percentages
        self.assertIn("FT%", processed_analysis["team_stats"])
        
        # Verify calculated PPG
        self.assertIn("PPG", processed_analysis["team_stats"])
        
        # Verify calculated rebounds
        self.assertIn("REB", processed_analysis["team_stats"])
        
        # Verify calculated assists, steals, blocks
        self.assertIn("AST", processed_analysis["team_stats"])
        self.assertIn("STL", processed_analysis["team_stats"])
        self.assertIn("BLK", processed_analysis["team_stats"])

    def test_post_process_missing_player_stats(self):
        """Test post-processing when player stats are missing raw values"""
        # Process the team analysis with missing player raw stats
        processed_analysis = post_process_team_stats(self.missing_player_stats_analysis)
        
        # Verify the team_stats dictionary exists
        self.assertIn("team_stats", processed_analysis)
        
        # Verify the original stats are preserved
        self.assertEqual(processed_analysis["team_stats"]["PPG"], 70.0)
        self.assertEqual(processed_analysis["team_stats"]["FG%"], "45.0%")
        self.assertEqual(processed_analysis["team_stats"]["3FG%"], "38.0%")
        self.assertEqual(processed_analysis["team_stats"]["FT%"], "75.0%")
        
        # Verify no errors occurred due to missing raw player stats
        self.assertIn("team_stats", processed_analysis)

    def test_offensive_defensive_rebound_estimation(self):
        """Test estimation of offensive and defensive rebounds when only total rebounds are available"""
        # Create a team analysis with only total rebounds
        team_analysis = {
            "team_name": "Rebound Test Team",
            "team_stats": {
                "REB": 40.0
                # No OREB or DREB
            },
            "players": []
        }
        
        # Process the team analysis
        processed_analysis = post_process_team_stats(team_analysis)
        
        # Verify offensive and defensive rebounds were estimated
        self.assertIn("OREB", processed_analysis["team_stats"])
        self.assertIn("DREB", processed_analysis["team_stats"])
        
        # Verify the estimates follow the typical 30/70 split
        self.assertAlmostEqual(processed_analysis["team_stats"]["OREB"], 40.0 * 0.3, places=1)
        self.assertAlmostEqual(processed_analysis["team_stats"]["DREB"], 40.0 * 0.7, places=1)

    def test_zero_division_handling(self):
        """Test handling of zero division cases"""
        # Create a team analysis with zero attempted shots
        team_analysis = {
            "team_name": "Zero Division Test Team",
            "team_stats": {},
            "players": [
                {
                    "name": "Player 1",
                    "stats": {
                        "FGM": 0,
                        "FGA": 0,
                        "3FGM": 0,
                        "3FGA": 0,
                        "FTM": 0,
                        "FTA": 0,
                        "AST": 5,
                        "TO": 0  # Zero turnovers will cause division by zero for A/TO
                    }
                }
            ]
        }
        
        # Process the team analysis
        processed_analysis = post_process_team_stats(team_analysis)
        
        # Verify no errors occurred due to division by zero
        self.assertIn("team_stats", processed_analysis)
        
        # Verify percentages are handled gracefully
        self.assertIn("FG%", processed_analysis["team_stats"])
        self.assertIn("3FG%", processed_analysis["team_stats"])
        self.assertIn("FT%", processed_analysis["team_stats"])
        
        # Verify assist-to-turnover ratio is handled gracefully
        self.assertIn("A/TO", processed_analysis["team_stats"])


if __name__ == '__main__':
    unittest.main()
