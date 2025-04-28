-- Create tables for Basketball Analysis Pipeline

-- Teams Table
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    record VARCHAR(20),
    ranking VARCHAR(50),
    playing_style TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Players Table
CREATE TABLE IF NOT EXISTS players (
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

-- Coaches Table
CREATE TABLE IF NOT EXISTS coaches (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Games Table
CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    home_team_id INTEGER REFERENCES teams(id),
    away_team_id INTEGER REFERENCES teams(id),
    date DATE,
    location VARCHAR(100),
    home_score INTEGER,
    away_score INTEGER,
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, completed, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Team Stats Table
CREATE TABLE IF NOT EXISTS team_stats (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    game_id INTEGER REFERENCES games(id) NULL, -- NULL for season averages
    ppg NUMERIC(5,1),
    fg_pct VARCHAR(10),
    fg3_pct VARCHAR(10),
    ft_pct VARCHAR(10),
    rebounds NUMERIC(5,1),
    offensive_rebounds NUMERIC(5,1),
    defensive_rebounds NUMERIC(5,1),
    assists NUMERIC(5,1),
    steals NUMERIC(5,1),
    blocks NUMERIC(5,1),
    turnovers NUMERIC(5,1),
    assist_to_turnover NUMERIC(5,2),
    is_season_average BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Player Stats Table
CREATE TABLE IF NOT EXISTS player_stats (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    game_id INTEGER REFERENCES games(id) NULL, -- NULL for season averages
    games_played INTEGER,
    ppg NUMERIC(5,1),
    fg_pct VARCHAR(10),
    fg3_pct VARCHAR(10),
    ft_pct VARCHAR(10),
    rpg NUMERIC(5,1),
    apg NUMERIC(5,1),
    spg NUMERIC(5,1),
    bpg NUMERIC(5,1),
    topg NUMERIC(5,1),
    minutes NUMERIC(5,1),
    is_season_average BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Team Analysis Table
CREATE TABLE IF NOT EXISTS team_analysis (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    strengths TEXT[],
    weaknesses TEXT[],
    key_players TEXT[],
    offensive_keys TEXT[],
    defensive_keys TEXT[],
    game_factors TEXT[],
    rotation_plan TEXT,
    situational_adjustments TEXT[],
    game_keys TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Game Simulations Table
CREATE TABLE IF NOT EXISTS game_simulations (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id),
    win_probability VARCHAR(100),
    projected_score VARCHAR(100),
    sim_overall_summary TEXT,
    sim_success_factors TEXT,
    sim_key_matchups TEXT,
    sim_win_loss_patterns TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports Table
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id),
    report_type VARCHAR(50), -- team_analysis, opponent_analysis, game_analysis
    file_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
