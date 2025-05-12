import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app.database
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database.connection import execute_query, insert_team, insert_team_stats

def test_connection():
    """
    Test the database connection and schema
    """
    print("Testing database connection...")
    
    # Test a simple query
    query = "SELECT 1 as test"
    result = execute_query(query)
    
    if result and len(result) > 0 and result[0]["test"] == 1:
        print("Database connection successful!")
    else:
        print("Database connection failed!")
        return False
    
    # Test inserting a team
    team_data = {
        "team_name": "Test Team",
        "team_record": "0-0",
        "team_ranking": "Unranked",
        "playing_style": "Test playing style"
    }
    
    print("\nTesting team insertion...")
    team_id = insert_team(team_data)
    
    if team_id:
        print(f"Team inserted successfully with ID: {team_id}")
    else:
        print("Team insertion failed!")
        return False
    
    # Test inserting team stats
    stats_data = {
        "team_stats": {
            "PPG": 75.5,
            "FG%": "45.2%",
            "3FG%": "35.6%",
            "FT%": "70.8%",
            "REB": 40.2,
            "OREB": 12.5,
            "DREB": 27.7,
            "AST": 15.3,
            "STL": 8.2,
            "BLK": 4.5,
            "TO": 12.1,
            "A/TO": 1.26
        }
    }
    
    print("\nTesting team stats insertion...")
    stats_id = insert_team_stats(team_id, stats_data)
    
    if stats_id:
        print(f"Team stats inserted successfully with ID: {stats_id}")
    else:
        print("Team stats insertion failed!")
        return False
    
    # Clean up the test data
    print("\nCleaning up test data...")
    
    delete_stats_query = "DELETE FROM team_stats WHERE id = %s"
    execute_query(delete_stats_query, (stats_id,), fetch=False)
    
    delete_team_query = "DELETE FROM teams WHERE id = %s"
    execute_query(delete_team_query, (team_id,), fetch=False)
    
    print("Test data cleaned up successfully!")
    
    return True

if __name__ == "__main__":
    success = test_connection()
    
    if success:
        print("\nAll tests passed successfully!")
    else:
        print("\nSome tests failed!")
