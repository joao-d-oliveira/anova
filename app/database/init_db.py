import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_db():
    """
    Initialize the database by creating tables
    """
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "anova"),
            user=os.getenv("DB_USER", "anova_user"),
            password=os.getenv("DB_PASSWORD", "anova@bask3t")
        )
        
        # Open a cursor to perform database operations
        cur = conn.cursor()
        
        # Read the SQL script
        script_path = os.path.join(os.path.dirname(__file__), "create_tables.sql")
        with open(script_path, "r") as f:
            sql_script = f.read()
        
        # Execute the SQL script
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

if __name__ == "__main__":
    init_db()
