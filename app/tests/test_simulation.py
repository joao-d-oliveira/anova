import os
import json
import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to sys.path to import app modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.anthropic_api import simulate_game, simulate_game_locally


class TestSimulation(unittest.TestCase):
    """Test class for basketball game simulation functions"""

    def setUp(self):
        """Set up test data by loading JSON files from app/data/analysis_json"""
        # Get the absolute path to the project root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Use hardcoded paths to the JSON files with absolute paths
        team_file_path = os.path.join(project_root, "app/data/analysis_json/Scarsdale_team_analysis_20250427_233648.json")
        opponent_file_path = os.path.join(project_root, "app/data/analysis_json/Arlington High School_opponent_analysis_20250427_233803.json")
        
        # Print paths for debugging
        print(f"Team file path: {team_file_path}")
        print(f"Opponent file path: {opponent_file_path}")
        
        # Check if files exist
        if not os.path.exists(team_file_path) or not os.path.exists(opponent_file_path):
            self.fail(f"Could not find required JSON analysis files: {team_file_path} or {opponent_file_path}")
        
        # Load JSON data
        with open(team_file_path, 'r') as f:
            self.team_analysis = json.load(f)
        
        with open(opponent_file_path, 'r') as f:
            self.opponent_analysis = json.load(f)

    def test_local_simulation(self):
        """Test the local simulation function"""
        # Run local simulation
        simulation_results = simulate_game_locally(self.team_analysis, self.opponent_analysis)
        
        # Verify the simulation results contain expected fields
        self.assertIn("numSimulations", simulation_results)
        self.assertIn("teamAWins", simulation_results)
        self.assertIn("teamBWins", simulation_results)
        self.assertIn("teamAWinPct", simulation_results)
        self.assertIn("teamBWinPct", simulation_results)
        self.assertIn("avgScoreA", simulation_results)
        self.assertIn("avgScoreB", simulation_results)
        
        # Verify the simulation ran the expected number of times
        self.assertEqual(simulation_results["numSimulations"], 100)
        
        # Verify that the total wins equals the number of simulations
        self.assertEqual(
            simulation_results["teamAWins"] + simulation_results["teamBWins"], 
            simulation_results["numSimulations"]
        )
        
        # Verify that win percentages are calculated correctly
        self.assertAlmostEqual(
            simulation_results["teamAWinPct"], 
            (simulation_results["teamAWins"] / simulation_results["numSimulations"]) * 100,
            places=1
        )
        
        self.assertAlmostEqual(
            simulation_results["teamBWinPct"], 
            (simulation_results["teamBWins"] / simulation_results["numSimulations"]) * 100,
            places=1
        )
        
        # Print some simulation results for debugging
        print(f"\nLocal Simulation Results:")
        print(f"Team A ({self.team_analysis['team_name']}) wins: {simulation_results['teamAWins']}")
        print(f"Team B ({self.opponent_analysis['team_name']}) wins: {simulation_results['teamBWins']}")
        print(f"Average score: {simulation_results['avgScoreA']} - {simulation_results['avgScoreB']}")

    def test_llm_simulation(self):
        """Test the LLM simulation function with a real API call"""
        # Skip this test if no API key is available
        if not os.environ.get("ANTHROPICS_API_KEY"):
            self.skipTest("ANTHROPICS_API_KEY environment variable not set")
        
        # Get the absolute path to the project root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Create a temporary prompt file for testing
        prompt_dir = os.path.join(project_root, "app/prompts")
        os.makedirs(prompt_dir, exist_ok=True)
        prompt_path = os.path.join(prompt_dir, "game_simulation_prompt.txt")
        
        # Write the prompt content to the file
 
        # Patch the simulate_game function to use our temporary prompt file
        with patch('app.services.anthropic_api.os.path.join', return_value=prompt_path):
            # Run LLM simulation
            simulation_results = simulate_game(self.team_analysis, self.opponent_analysis, use_local=False)
        
        # Verify the simulation results contain expected fields
        self.assertIn("sim_overall_summary", simulation_results)
        self.assertIn("sim_success_factors", simulation_results)
        self.assertIn("sim_key_matchups", simulation_results)
        self.assertIn("sim_win_loss_patterns", simulation_results)
        self.assertIn("win_probability", simulation_results)
        self.assertIn("projected_score", simulation_results)
        
        # Verify player stats are included (only check for team player stats since our simplified prompt might not include opponent stats)
        self.assertIn("team_p1_name", simulation_results)
        self.assertIn("team_p1_ppg", simulation_results)
        
        # Print some simulation results for debugging
        print(f"\nLLM Simulation Results:")
        print(f"Overall Summary: {simulation_results['sim_overall_summary']}")
        print(f"Win Probability: {simulation_results['win_probability']}")
        print(f"Projected Score: {simulation_results['projected_score']}")

    def test_compare_simulations(self):
        """Compare results from local and LLM simulations"""
        # Skip this test if no API key is available
        if not os.environ.get("ANTHROPICS_API_KEY"):
            self.skipTest("ANTHROPICS_API_KEY environment variable not set")
            
        # Get the absolute path to the project root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Create a temporary prompt file for testing
        prompt_dir = os.path.join(project_root, "app/prompts")
        os.makedirs(prompt_dir, exist_ok=True)
        prompt_path = os.path.join(prompt_dir, "game_simulation_prompt.txt")
                
        # Run local simulation
        local_results = simulate_game_locally(self.team_analysis, self.opponent_analysis)
        
        # Create a formatted win probability string from local results
        team_name = self.team_analysis['team_name']
        opponent_name = self.opponent_analysis['team_name']
        
        team_win_pct = local_results["teamAWinPct"]
        opponent_win_pct = local_results["teamBWinPct"]
        
        local_win_probability = f"{team_name} has a {team_win_pct}% win probability based on 100 simulations."
        local_projected_score = f"{team_name} {local_results['avgScoreA']} - {opponent_name} {local_results['avgScoreB']}"
        
        # Patch the simulate_game function to use our temporary prompt file
        with patch('app.services.anthropic_api.os.path.join', return_value=prompt_path):
            # Run LLM simulation with real API call
            llm_results = simulate_game(self.team_analysis, self.opponent_analysis, use_local=False)
        
        # Compare key metrics
        print(f"\nComparison of Local vs LLM Simulation:")
        print(f"Local win probability: {team_name} {team_win_pct}% - {opponent_name} {opponent_win_pct}%")
        print(f"LLM win probability: {llm_results['win_probability']}")
        print(f"Local projected score: {local_projected_score}")
        print(f"LLM projected score: {llm_results['projected_score']}")
        
        # We can't assert equality since the LLM results will be different from local results
        # Instead, just verify that the LLM results contain the expected fields
        self.assertIn("win_probability", llm_results)
        self.assertIn("projected_score", llm_results)


if __name__ == '__main__':
    unittest.main()
