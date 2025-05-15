#!/usr/bin/env python3
from app.tests.dbtests.db_tester_base import DatabaseTesterBase

class TeamStatsTester(DatabaseTesterBase):
    """Test class for team_stats table operations"""
    
    def test_creation_deletion_table_team_stats(self):
        """Test creating and deleting the team_stats table"""
        print("\n=== Testing Table: team_stats ===")
        
        if not self.connect():
            return False
            
        try:
            # Drop tables if exist
            self.cur.execute("DROP TABLE IF EXISTS team_stats CASCADE;")
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
            
            # Create team_stats table
            self.cur.execute("""
                CREATE TABLE team_stats (
                    id SERIAL PRIMARY KEY,
                    team_id INTEGER REFERENCES teams(id),
                    game_id INTEGER REFERENCES games(id),
                    ppg NUMERIC(5,1),
                    fg_pct VARCHAR(10),
                    fg_made NUMERIC,
                    fg_attempted NUMERIC,
                    fg3_pct VARCHAR(10),
                    fg3_made NUMERIC,
                    fg3_attempted NUMERIC,
                    ft_pct VARCHAR(10),
                    ft_made NUMERIC,
                    ft_attempted NUMERIC,
                    rebounds NUMERIC(5,1),
                    offensive_rebounds NUMERIC(5,1),
                    defensive_rebounds NUMERIC(5,1),
                    assists NUMERIC(5,1),
                    steals NUMERIC(5,1),
                    blocks NUMERIC(5,1),
                    turnovers NUMERIC(5,1),
                    assist_to_turnover NUMERIC(5,2),
                    is_season_average BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert test data
            self.cur.execute("""
                INSERT INTO team_stats (
                    team_id, game_id, ppg, fg_pct, fg_made, fg_attempted,
                    fg3_pct, fg3_made, fg3_attempted, ft_pct, ft_made, ft_attempted,
                    rebounds, offensive_rebounds, defensive_rebounds, assists,
                    steals, blocks, turnovers, assist_to_turnover, is_season_average
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (team_id, game_id, 85.5, '45.2%', 32, 71, '36.8%', 7, 19, '75.0%', 14, 18, 
                  40.5, 12.5, 28.0, 18.5, 7.5, 4.5, 12.5, 1.48, True))
            
            # Query data
            self.cur.execute("SELECT * FROM team_stats;")
            rows = self.cur.fetchall()
            print(f"Inserted {len(rows)} row(s) into team_stats table")
            
            # Check table structure
            self.check_table_structure("team_stats")
            
            # Clean up
            self.cur.execute("DROP TABLE IF EXISTS team_stats CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS games CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS teams CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS users CASCADE;")
            self.conn.commit()
            
            print("Team_stats table test successful!")
            return True
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error testing team_stats table: {e}")
            return False
        finally:
            self.disconnect()

def run_test():
    """Run the team_stats table test"""
    tester = TeamStatsTester()
    return tester.test_creation_deletion_table_team_stats()

if __name__ == "__main__":
    success = run_test()
    import sys
    sys.exit(0 if success else 1)
