#!/usr/bin/env python3
from app.tests.dbtests.db_tester_base import DatabaseTesterBase

class ReportsTester(DatabaseTesterBase):
    """Test class for reports table operations"""
    
    def test_creation_deletion_table_reports(self):
        """Test creating and deleting the reports table"""
        print("\n=== Testing Table: reports ===")
        
        if not self.connect():
            return False
            
        try:
            # Drop tables if exist
            self.cur.execute("DROP TABLE IF EXISTS reports CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS games CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS teams CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS users CASCADE;")
            
            # Create dependency tables
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
            
            self.cur.execute("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    cognito_id VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            self.cur.execute("""
                CREATE TABLE games (
                    id SERIAL PRIMARY KEY,
                    home_team_id INTEGER REFERENCES teams(id),
                    away_team_id INTEGER REFERENCES teams(id),
                    user_id INTEGER REFERENCES users(id),
                    date DATE,
                    location VARCHAR(100),
                    home_score INTEGER,
                    away_score INTEGER,
                    status VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert dependency data
            self.cur.execute("""
                INSERT INTO teams (name)
                VALUES (%s) RETURNING id;
            """, ('Test Team',))
            team_id = self.cur.fetchone()[0]
            
            self.cur.execute("""
                INSERT INTO users (cognito_id, email, name)
                VALUES (%s, %s, %s) RETURNING id;
            """, ('test-cognito-id', 'test@example.com', 'Test User'))
            user_id = self.cur.fetchone()[0]
            
            self.cur.execute("""
                INSERT INTO games (home_team_id, away_team_id, user_id, date)
                VALUES (%s, %s, %s, %s) RETURNING id;
            """, (team_id, team_id, user_id, '2023-01-01'))
            game_id = self.cur.fetchone()[0]
            
            # Create reports table
            self.cur.execute("""
                CREATE TABLE reports (
                    id SERIAL PRIMARY KEY,
                    game_id INTEGER REFERENCES games(id),
                    report_type VARCHAR(50),
                    file_path VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert test data
            self.cur.execute("""
                INSERT INTO reports (game_id, report_type, file_path)
                VALUES (%s, %s, %s);
            """, (game_id, 'Analysis', '/path/to/report.pdf'))
            
            # Query data
            self.cur.execute("SELECT * FROM reports;")
            rows = self.cur.fetchall()
            print(f"Inserted {len(rows)} row(s) into reports table")
            
            # Check table structure
            self.check_table_structure("reports")
            
            # Clean up
            self.cur.execute("DROP TABLE IF EXISTS reports CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS games CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS teams CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS users CASCADE;")
            self.conn.commit()
            
            print("Reports table test successful!")
            return True
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error testing reports table: {e}")
            return False
        finally:
            self.disconnect()

def run_test():
    """Run the reports table test"""
    tester = ReportsTester()
    return tester.test_creation_deletion_table_reports()

if __name__ == "__main__":
    success = run_test()
    import sys
    sys.exit(0 if success else 1)
