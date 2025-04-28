import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.report_gen import generate_report
from database.connection import insert_team, insert_game, insert_game_simulation

def test_report_generation():
    """
    Test generating a report with various types of data, including non-string values
    """
    print("Creating test teams...")
    team_data = {
        "team_name": "Scarsdale",
        "team_record": "15-5",
        "team_ranking": "3rd in division"
    }
    team_id = insert_team(team_data)
    
    opponent_data = {
        "team_name": "Arlington",
        "team_record": "14-6",
        "team_ranking": "4th in division"
    }
    opponent_id = insert_team(opponent_data)
    
    if not team_id or not opponent_id:
        print("Failed to create test teams")
        return False
    
    print(f"Test teams created with IDs: {team_id}, {opponent_id}")
    
    # Create a game
    print("Creating test game...")
    game_id = insert_game(team_id, opponent_id)
    
    if not game_id:
        print("Failed to create test game")
        return False
    
    print(f"Test game created with ID: {game_id}")
    
    # Create simulation data with various types of values
    simulation_data = {
        "win_probability": "Scarsdale has a 58% win probability based on 100 simulations.",
        "projected_score": "Scarsdale 54.6 - Arlington 51.2",
        "sim_overall_summary": "Based on 100 simulated games, Scarsdale emerged victorious in 58 games while Arlington won 42, with an average projected score of Scarsdale 54.6 - Arlington 51.2.",
        "sim_success_factors": "- Scarsdale's superior three-point shooting (37.2% vs 35.1%) created a consistent scoring advantage\n- Arlington's balanced scoring attack kept games competitive\n- Scarsdale's excellent free throw shooting (90.9% vs 61.0%) proved decisive in close games",
        "sim_key_matchups": "- Jake Sussberg (24.4 PPG) vs. Jacob Jerome (10.8 PPG): Sussberg's scoring prowess consistently outpaced Jerome\n- Daniel Hoey (15.0 PPG) vs. Gavin Flynn (9.8 PPG): Hoey's all-around game versus Flynn's efficiency created an intriguing battle",
        "sim_win_loss_patterns": "- When Jake Sussberg scored 20+ points, Scarsdale won 76% of those games\n- Arlington won 65% of games where they held Scarsdale under 30% from three-point range",
        # Add some non-string values to test our fixes
        "team_p1_ppg": 24.4,
        "team_p1_rpg": 5.2,
        "team_p1_apg": 3.1,
        "team_p1_fg": 0.449,
        "team_p1_3p": 0.372,
        "team_p1_name": "Jake Sussberg",
        "team_p1_role": "Primary scorer"
    }
    
    # Insert simulation data
    print("Inserting test simulation data...")
    simulation_id = insert_game_simulation(game_id, simulation_data)
    
    if not simulation_id:
        print("Failed to insert test simulation")
        return False
    
    print(f"Test simulation inserted successfully with ID: {simulation_id}")
    
    # Create analysis results for report generation
    analysis_results = {
        "team_name": "Scarsdale",
        "opponent_name": "Arlington",
        "matchup_overview": "Game between Scarsdale and Arlington.",
        "team_strengths_summary": "- Strong three-point shooting\n- Excellent free throw shooting\n- Dominant scoring from Jake Sussberg",
        "team_weaknesses_summary": "- Lower field goal percentage\n- Poor assist-to-turnover ratio\n- Limited bench scoring",
        "opponent_strengths_summary": "- Balanced scoring attack\n- Good field goal percentage\n- Strong assist-to-turnover ratio",
        "opponent_weaknesses_summary": "- Lack of dominant scorer\n- Poor free throw shooting\n- Inconsistent three-point shooting",
        "game_factors": 54.6,  # Intentionally using a float here to test our fix
        "offensive_keys": ["Attack the paint", "Find open three-point shooters", "Get to the free throw line"],  # List instead of string
        "defensive_keys": "- Limit Arlington's ball movement\n- Contest shots without fouling\n- Protect the defensive glass",
        "rotation_plan": "Standard rotation with increased minutes for starters in close game situations.",
        "situational_adjustments": "- Use zone defense when Arlington's shooters are cold\n- Push the pace after defensive rebounds\n- Slow the game down in the final minutes if leading",
        "game_keys": "- Win the three-point battle\n- Get to the free throw line\n- Limit turnovers"
    }
    
    # Generate report
    print("Generating test report...")
    try:
        # Add debug output to trace the error
        print("Debug: analysis_results keys:", list(analysis_results.keys()))
        print("Debug: simulation_data keys:", list(simulation_data.keys()))
        
        # Try to identify problematic values
        for key, value in analysis_results.items():
            if isinstance(value, (list, float, int)):
                print(f"Debug: Non-string value in analysis_results: {key} = {value} (type: {type(value)})")
        
        for key, value in simulation_data.items():
            if isinstance(value, (list, float, int)):
                print(f"Debug: Non-string value in simulation_data: {key} = {value} (type: {type(value)})")
        
        report_path = generate_report(analysis_results, simulation_data)
        print(f"Test report generated successfully: {report_path}")
        
        # Check if the file exists
        if os.path.exists(report_path):
            print("Report file exists")
            return True
        else:
            print("Report file does not exist")
            return False
    except Exception as e:
        import traceback
        print(f"Error generating report: {e}")
        print("Traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_report_generation()
    print(f"Test {'passed' if success else 'failed'}")
