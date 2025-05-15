#!/usr/bin/env python3
from app.tests.dbtests.db_tester_base import DatabaseTesterBase

class PlayersTester(DatabaseTesterBase):
    """Test class for players table operations"""
    
    def test_creation_deletion_table_players(self):
        """Test creating and deleting the players table"""
        print("\n=== Testing Table: players ===")
        
        if not self.connect():
            return False
            
        try:
            # Drop tables if exist
            self.cur.execute("DROP TABLE IF EXISTS players CASCADE;")
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
            
            # Create players table
            self.cur.execute("""
                CREATE TABLE players (
                    id SERIAL PRIMARY KEY,
                    team_id INTEGER REFERENCES teams(id),
                    name VARCHAR(100) NOT NULL,
                    number VARCHAR(10),
                    position VARCHAR(20),
                    height VARCHAR(10),
                    weight VARCHAR(10),
                    year VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert test data
            self.cur.execute("""
                INSERT INTO players (team_id, name, number, position, height, weight, year)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (team_id, 'Test Player', '23', 'Guard', '6\'2"', '185', 'Senior'))
            
            # Query data
            self.cur.execute("SELECT * FROM players;")
            rows = self.cur.fetchall()
            print(f"Inserted {len(rows)} row(s) into players table")
            
            # Check table structure
            self.check_table_structure("players")
            
            # Clean up
            self.cur.execute("DROP TABLE IF EXISTS players CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS teams CASCADE;")
            self.conn.commit()
            
            print("Players table test successful!")
            return True
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error testing players table: {e}")
            return False
        finally:
            self.disconnect()

def run_test():
    """Run the players table test"""
    tester = PlayersTester()
    return tester.test_creation_deletion_table_players()

if __name__ == "__main__":
    success = run_test()
    import sys
    sys.exit(0 if success else 1)
