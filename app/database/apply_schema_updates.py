import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app.database
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database.connection import execute_query

def apply_schema_updates():
    """
    Apply schema updates to the database
    """
    print("Applying schema updates...")
    
    # List of SQL files to apply
    update_files = [
        Path(__file__).parent / "update_schema_fields.sql",
        Path(__file__).parent / "update_schema_users.sql",
        Path(__file__).parent / "update_schema_user_reports.sql"
    ]
    
    success = True
    
    # Process each file
    for update_file in update_files:
        if not update_file.exists():
            print(f"Warning: Update file {update_file} does not exist, skipping")
            continue
        
        print(f"Processing file: {update_file}")
        
        with open(update_file, "r") as f:
            sql = f.read()
        
        # Split the SQL into individual statements
        statements = sql.split(";")
        
        # Execute each statement
        for statement in statements:
            # Skip empty statements
            if not statement.strip():
                continue
            
            print(f"Executing: {statement.strip()}")
            result = execute_query(statement, fetch=False)
            
            if result is None:
                print(f"Error executing statement: {statement.strip()}")
                success = False
    
    if success:
        print("Schema updates applied successfully")
    else:
        print("Some schema updates failed")
    
    return success

if __name__ == "__main__":
    apply_schema_updates()
