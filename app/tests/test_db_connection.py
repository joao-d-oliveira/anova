#!/usr/bin/env python3
import os
import sys
import importlib
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("../config/.env")

# Import test modules
from app.tests.dbtests.test_simple_connection import run_test as test_simple_connection
from app.tests.dbtests.test_users_table import run_test as test_users_table
from app.tests.dbtests.test_teams_table import run_test as test_teams_table
from app.tests.dbtests.test_players_table import run_test as test_players_table
from app.tests.dbtests.test_coaches_table import run_test as test_coaches_table
from app.tests.dbtests.test_games_table import run_test as test_games_table
from app.tests.dbtests.test_player_raw_stats_table import run_test as test_player_raw_stats_table
from app.tests.dbtests.test_team_stats_table import run_test as test_team_stats_table
from app.tests.dbtests.test_reports_table import run_test as test_reports_table

def run_all_tests():
    """Run all database tests"""
    print("=== Running All Database Tests ===")
    
    # Start with simple connection test
    if not test_simple_connection():
        print("Basic connection test failed. Aborting further tests.")
        return False
        
    # List of all table tests
    table_tests = {
        "users": test_users_table,
        "teams": test_teams_table,
        "players": test_players_table,
        "coaches": test_coaches_table,
        "games": test_games_table,
        "player_raw_stats": test_player_raw_stats_table,
        "team_stats": test_team_stats_table,
        "reports": test_reports_table
    }
    
    results = {}
    
    # Run test for each table
    for table, test_func in table_tests.items():
        print(f"\nTesting {table} table...")
        results[table] = test_func()
            
    # Print summary
    print("\n=== Test Results Summary ===")
    for table, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"{table}: {status}")
        
    return all(results.values())

def run_specific_test(test_name):
    """Run a specific test by name"""
    test_functions = {
        "simple_connection": test_simple_connection,
        "users": test_users_table,
        "teams": test_teams_table,
        "players": test_players_table,
        "coaches": test_coaches_table,
        "games": test_games_table,
        "player_raw_stats": test_player_raw_stats_table,
        "team_stats": test_team_stats_table,
        "reports": test_reports_table
    }
    
    if test_name in test_functions:
        print(f"Running test for {test_name}...")
        return test_functions[test_name]()
    else:
        print(f"Test for {test_name} not found.")
        print(f"Available tests: {', '.join(test_functions.keys())}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test if provided as argument
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        # Run all tests by default
        success = run_all_tests()
        
    sys.exit(0 if success else 1)
