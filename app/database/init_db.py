import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_db(drop_tables=False):
    """
    Initialize the database by creating tables
    
    Args:
        drop_tables: Whether to drop existing tables before creating new ones
    """
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "anova"),
            user=os.getenv("DB_USER", "anova_user"),
            password=os.getenv("DB_PASSWORD", "anova@bask3t")
        )
        
        # Open a cursor to perform database operations
        cur = conn.cursor()
        
        if drop_tables:
            print("Dropping existing tables...")
            # Drop tables in reverse order to avoid foreign key constraints
            drop_script = """
            DROP TABLE IF EXISTS reports CASCADE;
            DROP TABLE IF EXISTS game_simulations CASCADE;
            DROP TABLE IF EXISTS team_analysis CASCADE;
            DROP TABLE IF EXISTS player_stats CASCADE;
            DROP TABLE IF EXISTS team_stats CASCADE;
            DROP TABLE IF EXISTS games CASCADE;
            DROP TABLE IF EXISTS coaches CASCADE;
            DROP TABLE IF EXISTS players CASCADE;
            DROP TABLE IF EXISTS teams CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
            """
            cur.execute(drop_script)
            print("Tables dropped successfully!")
        
        # Read the SQL script
        script_path = os.path.join(os.path.dirname(__file__), "create_tables.sql")
        with open(script_path, "r") as f:
            sql_script = f.read()
        
        # Execute the SQL script
        print("Creating tables...")
        cur.execute(sql_script)
        
        # Read and execute the users schema update script
        users_script_path = os.path.join(os.path.dirname(__file__), "update_schema_users.sql")
        if os.path.exists(users_script_path):
            print("Updating schema with users table...")
            with open(users_script_path, "r") as f:
                users_sql_script = f.read()
            cur.execute(users_sql_script)
        
        # Commit the changes
        conn.commit()
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        
        print("Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Initialize the database')
    parser.add_argument('--drop-tables', action='store_true', help='Drop existing tables before creating new ones')
    args = parser.parse_args()
    
    init_db(drop_tables=args.drop_tables)
