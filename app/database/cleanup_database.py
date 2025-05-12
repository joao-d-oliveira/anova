import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app.database
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database.connection import execute_query, get_db_connection
from app.database.check_schema import check_table_schema
from app.database.apply_schema_updates import apply_schema_updates

def check_column_exists(table_name, column_name):
    """
    Check if a column exists in a table
    
    Args:
        table_name: Name of the table to check
        column_name: Name of the column to check
        
    Returns:
        True if the column exists, False otherwise
    """
    columns = check_table_schema(table_name)
    
    if not columns:
        return False
    
    for column in columns:
        if column["column_name"] == column_name:
            return True
    
    return False

def cleanup_database():
    """
    Clean up the database by checking and updating the schema
    """
    print("Starting database cleanup...")
    
    # Check if the problematic columns exist
    print("\nChecking for problematic columns...")
    
    team_stats_fg_percentage_exists = check_column_exists("team_stats", "fg_percentage")
    team_stats_fg_pct_exists = check_column_exists("team_stats", "fg_pct")
    players_jersey_number_exists = check_column_exists("players", "jersey_number")
    players_number_exists = check_column_exists("players", "number")
    
    print(f"team_stats.fg_percentage exists: {team_stats_fg_percentage_exists}")
    print(f"team_stats.fg_pct exists: {team_stats_fg_pct_exists}")
    print(f"players.jersey_number exists: {players_jersey_number_exists}")
    print(f"players.number exists: {players_number_exists}")
    
    # Determine what updates are needed
    updates_needed = []
    
    if team_stats_fg_pct_exists and not team_stats_fg_percentage_exists:
        updates_needed.append("Rename team_stats.fg_pct to fg_percentage")
    
    if players_number_exists and not players_jersey_number_exists:
        updates_needed.append("Rename players.number to jersey_number")
    
    # Check for missing columns in team_stats
    for column in ["fg_made", "fg_attempted", "three_pt_made", "three_pt_attempted", "ft_made", "ft_attempted"]:
        if not check_column_exists("team_stats", column):
            updates_needed.append(f"Add column team_stats.{column}")
    
    if not updates_needed:
        print("\nNo schema updates needed!")
        return True
    
    print("\nThe following updates are needed:")
    for update in updates_needed:
        print(f"- {update}")
    
    # Apply schema updates
    print("\nApplying schema updates...")
    success = apply_schema_updates()
    
    if not success:
        print("Failed to apply schema updates")
        return False
    
    # Verify the updates
    print("\nVerifying schema updates...")
    
    team_stats_fg_percentage_exists = check_column_exists("team_stats", "fg_percentage")
    players_jersey_number_exists = check_column_exists("players", "jersey_number")
    
    print(f"team_stats.fg_percentage exists: {team_stats_fg_percentage_exists}")
    print(f"players.jersey_number exists: {players_jersey_number_exists}")
    
    # Check for columns in team_stats
    for column in ["fg_made", "fg_attempted", "three_pt_made", "three_pt_attempted", "ft_made", "ft_attempted"]:
        exists = check_column_exists("team_stats", column)
        print(f"team_stats.{column} exists: {exists}")
        if not exists:
            print(f"Warning: Column team_stats.{column} was not created")
    
    # Final check
    all_columns_exist = (
        team_stats_fg_percentage_exists and
        players_jersey_number_exists and
        all(check_column_exists("team_stats", col) for col in ["fg_made", "fg_attempted", "three_pt_made", "three_pt_attempted", "ft_made", "ft_attempted"])
    )
    
    if all_columns_exist:
        print("\nDatabase schema cleanup completed successfully!")
    else:
        print("\nWarning: Some schema updates may not have been applied correctly")
    
    return all_columns_exist

if __name__ == "__main__":
    cleanup_database()
