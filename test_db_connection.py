#!/usr/bin/env python3
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_db_connection():
    """Test connection to the PostgreSQL database"""
    print("Testing database connection...")
    
    # Get database connection parameters from environment variables
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")  # Use 5433 for local tunnel
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    
    print(f"Connecting to: {db_host}:{db_port}")
    print(f"Database: {db_name}")
    print(f"User: {db_user}")
    
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Execute a simple query
        cur.execute("SELECT version();")
        
        # Get the result
        version = cur.fetchone()
        print(f"PostgreSQL version: {version[0]}")
        
        # Test if we can query the tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        print("\nDatabase tables:")
        for table in tables:
            print(f"- {table[0]}")
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        
        print("\nDatabase connection test successful!")
        return True
        
    except Exception as e:
        print(f"\nError connecting to database: {e}")
        return False

if __name__ == "__main__":
    success = test_db_connection()
    sys.exit(0 if success else 1)