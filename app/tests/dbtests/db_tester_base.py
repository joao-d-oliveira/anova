#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseTesterBase:
    """Base class for database testing with common methods"""
    
    def __init__(self):
        # Get database connection parameters from environment variables
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = os.getenv("DB_PORT", "5432")  # Use 5433 for local tunnel
        self.db_name = os.getenv("DB_NAME")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.conn = None
        self.cur = None
        
    def connect(self):
        """Connect to the PostgreSQL database"""
        print(f"Connecting to: {self.db_host}:{self.db_port}")
        print(f"Database: {self.db_name}")
        print(f"User: {self.db_user}")
        
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password
            )
            self.cur = self.conn.cursor()
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False
            
    def disconnect(self):
        """Close the database connection"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
            print("Database connection closed.")
            
    def check_table_structure(self, table_name):
        """Check the structure of a table"""
        print(f"\nChecking structure of table: {table_name}")
        
        if not self.cur:
            print("No database cursor available.")
            return False
            
        try:
            # Get columns
            self.cur.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """)
            
            columns = self.cur.fetchall()
            print(f"Table {table_name} has {len(columns)} columns:")
            for col in columns:
                print(f"- {col[0]} ({col[1]}, nullable: {col[2]})")
                
            # Get constraints
            self.cur.execute(f"""
                SELECT c.conname, c.contype, pg_get_constraintdef(c.oid)
                FROM pg_constraint c
                JOIN pg_namespace n ON n.oid = c.connamespace
                WHERE conrelid = '{table_name}'::regclass
                AND n.nspname = 'public';
            """)
            
            constraints = self.cur.fetchall()
            if constraints:
                print(f"\nTable {table_name} constraints:")
                for con in constraints:
                    con_type = {
                        'p': 'PRIMARY KEY',
                        'f': 'FOREIGN KEY',
                        'u': 'UNIQUE',
                        'c': 'CHECK'
                    }.get(con[1], 'OTHER')
                    print(f"- {con[0]} ({con_type}): {con[2]}")
                    
            return True
            
        except Exception as e:
            print(f"Error checking table structure: {e}")
            return False
            
    def list_all_tables(self):
        """List all tables in the database"""
        print("\n=== Listing All Tables ===")
        
        if not self.connect():
            return False
            
        try:
            self.cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            tables = self.cur.fetchall()
            print(f"Found {len(tables)} tables:")
            for table in tables:
                print(f"- {table[0]}")
                
            return [table[0] for table in tables]
            
        except Exception as e:
            print(f"Error listing tables: {e}")
            return []
        finally:
            self.disconnect()
