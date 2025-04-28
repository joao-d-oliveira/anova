import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import insert_team, insert_game, insert_game_simulation

def test_game_simulation_insert():
    """
    Test inserting a game simulation with long text values
    """
    # Create test teams first
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
    
    # Now create the game
    print("Creating test game...")
    game_id = insert_game(team_id, opponent_id)
    
    if not game_id:
        print("Failed to create test game")
        return False
    
    print(f"Test game created with ID: {game_id}")
    
    # Create simulation data with long text values
    simulation_data = {
        "win_probability": "Scarsdale has a 58% win probability based on 100 simulations.",
        "projected_score": "Scarsdale 54.6 - Arlington 51.2",
        "sim_overall_summary": "Based on 100 simulated games, Scarsdale emerged victorious in 58 games while Arlington won 42, with an average projected score of Scarsdale 54.6 - Arlington 51.2.",
        "sim_success_factors": "- Scarsdale's superior three-point shooting (37.2% vs 35.1%) created a consistent scoring advantage\n- Arlington's balanced scoring attack kept games competitive\n- Scarsdale's excellent free throw shooting (90.9% vs 61.0%) proved decisive in close games",
        "sim_key_matchups": "- Jake Sussberg (24.4 PPG) vs. Jacob Jerome (10.8 PPG): Sussberg's scoring prowess consistently outpaced Jerome\n- Daniel Hoey (15.0 PPG) vs. Gavin Flynn (9.8 PPG): Hoey's all-around game versus Flynn's efficiency created an intriguing battle",
        "sim_win_loss_patterns": "- When Jake Sussberg scored 20+ points, Scarsdale won 76% of those games\n- Arlington won 65% of games where they held Scarsdale under 30% from three-point range"
    }
    
    print("Inserting test simulation data...")
    simulation_id = insert_game_simulation(game_id, simulation_data)
    
    if simulation_id:
        print(f"Test simulation inserted successfully with ID: {simulation_id}")
        return True
    else:
        print("Failed to insert test simulation")
        return False

if __name__ == "__main__":
    success = test_game_simulation_insert()
    print(f"Test {'passed' if success else 'failed'}")
