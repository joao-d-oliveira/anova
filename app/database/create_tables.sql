-- Create users table (new)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    school VARCHAR(100),
    role VARCHAR(50),
    password_hash VARCHAR(255) NOT NULL,
    confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create teams table (updated with record_date)
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    record VARCHAR(20),
    ranking VARCHAR(50),
    record_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create players table
CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    name VARCHAR(100) NOT NULL,
    number VARCHAR(10),
    position VARCHAR(20),
    height VARCHAR(10),
    weight VARCHAR(10),
    year VARCHAR(20),
    strengths TEXT[],
    weaknesses TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create coaches table
CREATE TABLE IF NOT EXISTS coaches (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create games table (updated with user_id)
CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
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

-- Create player_raw_stats table (new)
CREATE TABLE IF NOT EXISTS player_raw_stats (
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

-- Create team_stats table (updated with additional fields)
CREATE TABLE IF NOT EXISTS team_stats (
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

-- Create player_stats table (updated with player_raw_stats_id)
CREATE TABLE IF NOT EXISTS player_stats (
    id SERIAL PRIMARY KEY,
    player_raw_stats_id INTEGER REFERENCES player_raw_stats(id),
    player_id INTEGER REFERENCES players(id),
    game_id INTEGER REFERENCES games(id),
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
    is_season_average BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create team_analysis table
CREATE TABLE IF NOT EXISTS team_analysis (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    strengths TEXT[],
    weaknesses TEXT[],
    key_players TEXT[],
    offensive_keys TEXT[],
    defensive_keys TEXT[],
    game_factors TEXT[],
    rotation_plan TEXT[],
    situational_adjustments TEXT[],
    game_keys TEXT[],
    playing_style TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create game_simulations table
CREATE TABLE IF NOT EXISTS game_simulations (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id),
    win_probability VARCHAR(100),
    projected_score VARCHAR(100),
    sim_overall_summary TEXT,
    sim_success_factors TEXT,
    sim_key_matchups TEXT,
    sim_win_loss_patterns TEXT,
    sim_critical_advantage TEXT,
    sim_keys_to_victory TEXT[],
    sim_situational_adjustments JSONB, -- TODO: add the python type
    playbook_offensive_plays JSONB,
    playbook_defensive_plays JSONB,
    playbook_special_situations JSONB,
    playbook_inbound_plays JSONB,
    playbook_after_timeout_special_plays JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create player_projections table (new)
CREATE TABLE IF NOT EXISTS player_projections (
    id SERIAL PRIMARY KEY,
    game_simulation_id INTEGER REFERENCES game_simulations(id),
    player_id INTEGER REFERENCES players(id),
    team_id INTEGER REFERENCES teams(id),
    game_id INTEGER REFERENCES games(id),
    is_home_team BOOLEAN,
    ppg NUMERIC(5,1),
    rpg NUMERIC(5,1),
    apg NUMERIC(5,1),
    fg_pct VARCHAR(10),
    fg3_pct VARCHAR(10),
    role VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create simulation_details table (new)
CREATE TABLE IF NOT EXISTS simulation_details (
    id SERIAL PRIMARY KEY,
    game_simulation_id INTEGER REFERENCES game_simulations(id),
    game_id INTEGER REFERENCES games(id),
    home_team_id INTEGER REFERENCES teams(id),
    away_team_id INTEGER REFERENCES teams(id),
    num_simulations INTEGER,
    home_team_wins INTEGER,
    away_team_wins INTEGER,
    home_team_win_pct NUMERIC(5,1),
    away_team_win_pct NUMERIC(5,1),
    avg_home_score NUMERIC(5,1),
    avg_away_score NUMERIC(5,1),
    closest_game_margin INTEGER,
    blowout_game_margin INTEGER,
    margin_distribution JSONB,
    avg_effects JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    game_id INTEGER REFERENCES games(id),
    report_type VARCHAR(50),
    file_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create one_time_passwords table
CREATE TABLE IF NOT EXISTS one_time_passwords (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    otp VARCHAR(10) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add comments to tables for documentation
COMMENT ON TABLE users IS 'Stores information about application users';
COMMENT ON TABLE teams IS 'Stores information about basketball teams';
COMMENT ON TABLE players IS 'Stores information about individual players';
COMMENT ON TABLE coaches IS 'Stores information about team coaches';
COMMENT ON TABLE games IS 'Stores information about scheduled or completed games';
COMMENT ON TABLE player_raw_stats IS 'Stores raw statistical data for individual players';
COMMENT ON TABLE team_stats IS 'Stores statistical data for teams';
COMMENT ON TABLE player_stats IS 'Stores statistical data for individual players';
COMMENT ON TABLE team_analysis IS 'Stores analysis results for teams';
COMMENT ON TABLE game_simulations IS 'Stores game simulation results';
COMMENT ON TABLE player_projections IS 'Stores player projection data from game simulations';
COMMENT ON TABLE simulation_details IS 'Stores detailed simulation results';
COMMENT ON TABLE reports IS 'Stores generated reports';
COMMENT ON TABLE one_time_passwords IS 'Stores one-time password tokens for user verification and password reset';

-- Create indexes for performance optimization
CREATE INDEX idx_players_team_id ON players(team_id);
CREATE INDEX idx_coaches_team_id ON coaches(team_id);
CREATE INDEX idx_games_home_team_id ON games(home_team_id);
CREATE INDEX idx_games_away_team_id ON games(away_team_id);
CREATE INDEX idx_games_user_id ON games(user_id);
CREATE INDEX idx_team_stats_team_id ON team_stats(team_id);
CREATE INDEX idx_team_stats_game_id ON team_stats(game_id);
CREATE INDEX idx_player_raw_stats_player_id ON player_raw_stats(player_id);
CREATE INDEX idx_player_raw_stats_game_id ON player_raw_stats(game_id);
CREATE INDEX idx_player_stats_player_id ON player_stats(player_id);
CREATE INDEX idx_player_stats_game_id ON player_stats(game_id);
CREATE INDEX idx_player_stats_player_raw_stats_id ON player_stats(player_raw_stats_id);
CREATE INDEX idx_team_analysis_team_id ON team_analysis(team_id);
CREATE INDEX idx_game_simulations_game_id ON game_simulations(game_id);
CREATE INDEX idx_player_projections_game_simulation_id ON player_projections(game_simulation_id);
CREATE INDEX idx_player_projections_player_id ON player_projections(player_id);
CREATE INDEX idx_player_projections_team_id ON player_projections(team_id);
CREATE INDEX idx_player_projections_game_id ON player_projections(game_id);
CREATE INDEX idx_simulation_details_game_simulation_id ON simulation_details(game_simulation_id);
CREATE INDEX idx_simulation_details_game_id ON simulation_details(game_id);
CREATE INDEX idx_simulation_details_home_team_id ON simulation_details(home_team_id);
CREATE INDEX idx_simulation_details_away_team_id ON simulation_details(away_team_id);
CREATE INDEX idx_reports_game_id ON reports(game_id);
CREATE INDEX idx_one_time_passwords_user_id ON one_time_passwords(user_id);
CREATE INDEX idx_one_time_passwords_otp ON one_time_passwords(otp);
