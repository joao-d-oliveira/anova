#!/usr/bin/env python3
from app.tests.dbtests.db_tester_base import DatabaseTesterBase

class CoachesTester(DatabaseTesterBase):
    """Test class for coaches table operations"""
    
    def test_creation_deletion_table_coaches(self):
        """Test creating and deleting the coaches table"""
        print("\n=== Testing Table: coaches ===")
        
        if not self.connect():
            return False
            
        try:
            # Drop tables if exist
            self.cur.execute("DROP TABLE IF EXISTS coaches CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS teams CASCADE;")
            
            # Create teams table first (dependency)
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
            
            # Insert team data
            self.cur.execute("""
                INSERT INTO teams (name)
                VALUES (%s) RETURNING id;
            """, ('Test Team',))
            team_id = self.cur.fetchone()[0]
            
            # Create coaches table
            self.cur.execute("""
                CREATE TABLE coaches (
                    id SERIAL PRIMARY KEY,
                    team_id INTEGER REFERENCES teams(id),
                    name VARCHAR(100) NOT NULL,
                    role VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert test data
            self.cur.execute("""
                INSERT INTO coaches (team_id, name, role)
                VALUES (%s, %s, %s);
            """, (team_id, 'Test Coach', 'Head Coach'))
            
            # Query data
            self.cur.execute("SELECT * FROM coaches;")
            rows = self.cur.fetchall()
            print(f"Inserted {len(rows)} row(s) into coaches table")
            
            # Check table structure
            self.check_table_structure("coaches")
            
            # Clean up
            self.cur.execute("DROP TABLE IF EXISTS coaches CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS teams CASCADE;")
            self.conn.commit()
            
            print("Coaches table test successful!")
            return True
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error testing coaches table: {e}")
            return False
        finally:
            self.disconnect()

def run_test():
    """Run the coaches table test"""
    tester = CoachesTester()
    return tester.test_creation_deletion_table_coaches()

if __name__ == "__main__":
    success = run_test()
    import sys
    sys.exit(0 if success else 1)
