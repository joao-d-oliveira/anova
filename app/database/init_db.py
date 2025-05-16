import os
import psycopg2
from config import Config


# Load environment variables
def init_db(config: Config):
    """
    Initialize the database by creating tables
    
    Args:
        drop_tables: Whether to drop existing tables before creating new ones
    """
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=config.db_host,
            port=config.db_port,
            database=config.db_name,
            user=config.db_user,
            password=config.db_password
        )
        
        # Open a cursor to perform database operations
        cur = conn.cursor()
        
        # Read the SQL script
        script_path = os.path.join(os.path.dirname(__file__), "create_tables.sql")
        with open(script_path, "r") as f:
            sql_script = f.read()
        
        # Execute the SQL script to create tables
        print("Creating tables...")
        cur.execute(sql_script)

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
