#!/usr/bin/env python3
from app.tests.dbtests.db_tester_base import DatabaseTesterBase

class PlayerRawStatsTester(DatabaseTesterBase):
    """Test class for player_raw_stats table operations"""
    
    def test_creation_deletion_table_player_raw_stats(self):
        """Test creating and deleting the player_raw_stats table"""
        print("\n=== Testing Table: player_raw_stats ===")
        
        if not self.connect():
            return False
            
        try:
            # Drop tables if exist
            self.cur.execute("DROP TABLE IF EXISTS player_raw_stats CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS players CASCADE;")
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
                INSERT INTO players (team_id, name)
                VALUES (%s, %s) RETURNING id;
            """, (team_id, 'Test Player'))
            player_id = self.cur.fetchone()[0]
            
            self.cur.execute("""
                INSERT INTO games (home_team_id, away_team_id, user_id, date)
                VALUES (%s, %s, %s, %s) RETURNING id;
            """, (team_id, team_id, user_id, '2023-01-01'))
            game_id = self.cur.fetchone()[0]
            
            # Create player_raw_stats table
            self.cur.execute("""
                CREATE TABLE player_raw_stats (
                    id SERIAL PRIMARY KEY,
                    player_id INTEGER REFERENCES players(id),
                    game_id INTEGER REFERENCES games(id),
                    fgm INTEGER,
                    fga INTEGER,
                    fg2m INTEGER,
                    fg2a INTEGER,
                    fg3m INTEGER,
                    fg3a INTEGER,
                    ftm INTEGER,
                    fta INTEGER,
                    total_rebounds INTEGER,
                    offensive_rebounds INTEGER,
                    defensive_rebounds INTEGER,
                    total_assists INTEGER,
                    total_steals INTEGER,
                    total_blocks INTEGER,
                    total_turnovers INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert test data
            self.cur.execute("""
                INSERT INTO player_raw_stats (
                    player_id, game_id, fgm, fga, fg2m, fg2a, fg3m, fg3a, 
                    ftm, fta, total_rebounds, offensive_rebounds, defensive_rebounds,
                    total_assists, total_steals, total_blocks, total_turnovers
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (player_id, game_id, 5, 10, 3, 6, 2, 4, 3, 4, 5, 2, 3, 4, 2, 1, 2))
            
            # Query data
            self.cur.execute("SELECT * FROM player_raw_stats;")
            rows = self.cur.fetchall()
            print(f"Inserted {len(rows)} row(s) into player_raw_stats table")
            
            # Check table structure
            self.check_table_structure("player_raw_stats")
            
            # Clean up
            self.cur.execute("DROP TABLE IF EXISTS player_raw_stats CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS players CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS games CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS teams CASCADE;")
            self.cur.execute("DROP TABLE IF EXISTS users CASCADE;")
            self.conn.commit()
            
            print("Player_raw_stats table test successful!")
            return True
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error testing player_raw_stats table: {e}")
            return False
        finally:
            self.disconnect()

def run_test():
    """Run the player_raw_stats table test"""
    tester = PlayerRawStatsTester()
    return tester.test_creation_deletion_table_player_raw_stats()

if __name__ == "__main__":
    success = run_test()
    import sys
    sys.exit(0 if success else 1)
