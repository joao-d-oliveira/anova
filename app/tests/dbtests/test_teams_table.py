#!/usr/bin/env python3
from app.tests.dbtests.db_tester_base import DatabaseTesterBase

class TeamsTester(DatabaseTesterBase):
    """Test class for teams table operations"""
    
    def test_creation_deletion_table_teams(self):
        """Test creating and deleting the teams table"""
        print("\n=== Testing Table: teams ===")
        
        if not self.connect():
            return False
            
        try:
            # Drop table if exists
            self.cur.execute("DROP TABLE IF EXISTS teams CASCADE;")
            
            # Create table
            self.cur.execute("""
                CREATE TABLE teams (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    record VARCHAR(20),
                    ranking VARCHAR(50),
                    playing_style TEXT,
                    record_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert test data
            self.cur.execute("""
                INSERT INTO teams (name, record, ranking, playing_style, record_date)
                VALUES (%s, %s, %s, %s, %s);
            """, ('Test Team', '10-5', 'A', 'Aggressive', '2023-01-01'))
            
            # Query data
            self.cur.execute("SELECT * FROM teams;")
            rows = self.cur.fetchall()
            print(f"Inserted {len(rows)} row(s) into teams table")
            
            # Check table structure
            self.check_table_structure("teams")
            
            # Clean up
            self.cur.execute("DROP TABLE IF EXISTS teams CASCADE;")
            self.conn.commit()
            
            print("Teams table test successful!")
            return True
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error testing teams table: {e}")
            return False
        finally:
            self.disconnect()

def run_test():
    """Run the teams table test"""
    tester = TeamsTester()
    return tester.test_creation_deletion_table_teams()

if __name__ == "__main__":
    success = run_test()
    import sys
    sys.exit(0 if success else 1)
