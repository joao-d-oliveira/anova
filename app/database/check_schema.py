import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app.database
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database.connection import execute_query

def check_table_schema(table_name):
    """
    Check the schema of a table
    
    Args:
        table_name: Name of the table to check
        
    Returns:
        List of column information
    """
    query = """
    SELECT column_name, data_type, character_maximum_length
    FROM information_schema.columns
    WHERE table_name = %s
    ORDER BY ordinal_position
    """
    
    return execute_query(query, (table_name,))

def check_all_tables():
    """
    Check the schema of all tables in the database
    """
    # Get list of tables
    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    ORDER BY table_name
    """
    
    tables = execute_query(query)
    
    if not tables:
        print("No tables found in the database")
        return
    
    # Check each table
    for table in tables:
        table_name = table["table_name"]
        print(f"\n=== Table: {table_name} ===")
        
        columns = check_table_schema(table_name)
        
        if not columns:
            print(f"No columns found for table {table_name}")
            continue
        
        # Print column information
        for column in columns:
            column_name = column["column_name"]
            data_type = column["data_type"]
            max_length = column["character_maximum_length"]
            
            if max_length:
                print(f"{column_name}: {data_type}({max_length})")
            else:
                print(f"{column_name}: {data_type}")

if __name__ == "__main__":
    check_all_tables()
