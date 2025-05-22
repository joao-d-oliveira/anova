import datetime
import json
import os
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

from pydantic import BaseModel
from app.config import Config
from app.models import GameSimulation, PlaybookPlay, Player, PlayerStats, SituationalAdjustment, TeamAnalysis, TeamDetails, TeamStats

# Set up logging
logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Get a connection to the PostgreSQL database
    
    Returns:
        Connection object
    """
    try:
        config = Config()
        logger.info(f"Connecting to database: {config.db_host}:{config.db_port}/{config.db_name}")
        
        conn = psycopg2.connect(
            host=config.db_host,
            port=config.db_port,
            database=config.db_name,
            user=config.db_user,
            password=config.db_password,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def execute_query(query, params=None, fetch=True):
    """
    Execute a SQL query
    
    Args:
        query: SQL query string
        params: Parameters for the query
        fetch: Whether to fetch results
        
    Returns:
        Query results if fetch is True, otherwise None
    """
    conn = get_db_connection()
    if not conn:
        print("ERROR: Could not get database connection")
        return None
    
    try:
        with conn.cursor() as cur:
            # print(f"DEBUG - Executing query: {query[:10]}")
            # print(f"DEBUG - With params: {params}")
            cur.execute(query, params)
            
            # Always commit changes, regardless of fetch
            conn.commit()
            print("DEBUG - Changes committed to database")
            
            if fetch:
                results = cur.fetchall()
                # print(f"DEBUG - Query results: {results}")
                return results
            else:
                print("DEBUG - Query executed successfully")
                return None
    except Exception as e:
        print(f"Error executing query: {e}")
        conn.rollback()  # Rollback in case of error
        print("DEBUG - Transaction rolled back due to error")
        return None
    finally:
        conn.close()

def insert_team(team_details: TeamDetails, team_analysis: TeamAnalysis):
    """
    Insert a team into the database
    
    Args:
        team_data: Dictionary containing team data
        
    Returns:
        Team ID if successful, None otherwise
    """
    query = """
    INSERT INTO teams (name, record, ranking, record_date)
    VALUES (%s, %s, %s, %s)
    RETURNING id
    """
    
    # Parse record_date if it exists, otherwise use current date
    from datetime import datetime
    record_date = None
    if "record_date" in team_analysis:
        try:
            record_date = datetime.strptime(team_analysis["record_date"], "%Y-%m-%d").date()
        except:
            record_date = datetime.now().date()
    else:
        record_date = datetime.now().date()
    
    params = (
        team_details.team_name,
        team_details.record,
        team_details.team_ranking,
        record_date
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None
def insert_team_stats(team_id, stats_data: TeamStats, game_id=None, is_season_average=True):
    """
    Insert team statistics into the database
    
    Args:
        team_id: Team ID
        stats_data: TeamStats object containing team statistics
        game_id: Game ID (optional)
        is_season_average: Whether these stats are season averages
        
    Returns:
        Stats ID if successful, None otherwise
    """
    query = """
    INSERT INTO team_stats (
        team_id, game_id, is_season_average, ppg, fg_pct, 
        fg_made, fg_attempted, fg3_pct, fg3_made, fg3_attempted,
        ft_pct, ft_made, ft_attempted, rebounds, offensive_rebounds, 
        defensive_rebounds, assists, steals, blocks, turnovers, assist_to_turnover
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    
    print("DEBUG - Attempting to insert team stats with exact column names from database schema")
    
    # Calculate assist to turnover ratio
    assist_to_turnover = 0
    if stats_data.TO > 0:
        assist_to_turnover = round(stats_data.AST / stats_data.TO, 2)
    else:
        assist_to_turnover = stats_data.A_TO
    
    params = (
        team_id,
        game_id,
        is_season_average,
        stats_data.PPG,
        stats_data.FG_percent,
        stats_data.FGM, 
        stats_data.FGA,  
        stats_data.FG3_percent,
        stats_data.FGM3,  
        stats_data.FGA3,
        stats_data.FT_percent,
        stats_data.FTM,  
        stats_data.FTA,  
        stats_data.REB,
        stats_data.OREB,
        stats_data.DREB,
        stats_data.AST,
        stats_data.STL,
        stats_data.BLK,
        stats_data.TO,
        assist_to_turnover
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def update_team_stats_game_id(team_stats_id, game_id):
    query = """
    UPDATE team_stats
    SET game_id = %s
    WHERE id = %s
    """
    execute_query(query, (game_id, team_stats_id), fetch=False)

def insert_player(team_id, player_data: Player):
    """
    Insert a player into the database
    
    Args:
        team_id: Team ID
        player_data: Dictionary containing player data
        
    Returns:
        Player ID if successful, None otherwise
    """
    query = """
    INSERT INTO players (team_id, name, number, position, height, weight, year, strengths, weaknesses)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    
    params = (
        team_id,
        player_data.name,
        player_data.number,
        player_data.position,
        player_data.height,
        player_data.weight,
        player_data.year,
        player_data.strengths,
        player_data.weaknesses,
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def insert_player_stats(player_id, stats_data: PlayerStats, game_id=None, is_season_average=True, player_raw_stats_id=None):
    """
    Insert player statistics into the database
    
    Args:
        player_id: Player ID
        stats_data: Dictionary containing player statistics
        game_id: Game ID (optional)
        is_season_average: Whether these stats are season averages
        player_raw_stats_id: ID of raw stats record (optional)
        
    Returns:
        Stats ID if successful, None otherwise
    """
    query = """
    INSERT INTO player_stats (
        player_id, player_raw_stats_id, game_id, games_played, ppg, fg_pct, fg3_pct, ft_pct,
        rpg, apg, spg, bpg, topg, minutes, is_season_average
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    
    params = (
        player_id,
        player_raw_stats_id,
        game_id,
        stats_data.GP,
        stats_data.PPG,
        stats_data.FG_percent,
        stats_data.FG3_percent,
        stats_data.FT_percent,
        stats_data.RPG,
        stats_data.APG,
        stats_data.SPG,
        stats_data.BPG,
        stats_data.TOPG,
        stats_data.MINS,
        is_season_average
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def insert_team_analysis(team_id, analysis_data: TeamAnalysis):
    """
    Insert team analysis into the database
    
    Args:
        team_id: Team ID
        analysis_data: Dictionary containing team analysis
        
    Returns:
        Analysis ID if successful, None otherwise
    """
    query = """
    INSERT INTO team_analysis (
        team_id, playing_style, strengths, weaknesses, key_players,
        offensive_keys, defensive_keys, game_factors,
        rotation_plan, situational_adjustments, game_keys
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    
    params = (
        team_id,
        analysis_data.playing_style,
        analysis_data.team_strengths,
        analysis_data.team_weaknesses,
        analysis_data.key_players,
        analysis_data.offensive_keys,
        analysis_data.defensive_keys,
        analysis_data.game_factors,
        analysis_data.rotation_plan,
        analysis_data.situational_adjustments,
        analysis_data.game_keys
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def get_or_create_user(cognito_id, email, name, phone_number=None, school=None, role=None):
    """
    Get or create a user in the database based on Cognito ID
    
    Args:
        cognito_id: Cognito user ID
        email: User email
        name: User name
        phone_number: User phone number (optional)
        school: User school (optional)
        role: User role (optional)
        
    Returns:
        User ID if successful, None otherwise
    """
    # First try to get the user
    query = """
    SELECT id FROM users
    WHERE cognito_id = %s
    """
    
    result = execute_query(query, (cognito_id,))
    
    if result and len(result) > 0:
        return result[0]["id"]
    
    # If user doesn't exist, create it
    query = """
    INSERT INTO users (cognito_id, email, name, phone_number, school, role)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    
    params = (
        cognito_id,
        email,
        name,
        phone_number,
        school,
        role
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def insert_game(home_team_id, away_team_id, user_id=None, date=None, location=None):
    """
    Insert a game into the database
    
    Args:
        home_team_id: Home team ID
        away_team_id: Away team ID
        user_id: User ID (optional)
        date: Game date (optional)
        location: Game location (optional)
        
    Returns:
        Game ID if successful, None otherwise
    """
    query = """
    INSERT INTO games (home_team_id, away_team_id, user_id, date, location)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id, uuid
    """
    
    params = (
        home_team_id,
        away_team_id,
        user_id,
        date,
        location
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"], result[0]["uuid"]
    return None

def insert_game_simulation(game_id, simulation_data: GameSimulation):
    """
    Insert game simulation into the database
    
    Args:
        game_id: Game ID
        simulation_data: GameSimulation object containing simulation data
        
    Returns:
        Simulation ID if successful, None otherwise
    """
    query = """
    INSERT INTO game_simulations (
        game_id, win_probability, projected_score,
        sim_overall_summary, sim_success_factors,
        sim_key_matchups, sim_win_loss_patterns,
        sim_critical_advantage, sim_keys_to_victory,
        sim_situational_adjustments, playbook_offensive_plays,
        playbook_defensive_plays, playbook_special_situations,
        playbook_inbound_plays, playbook_after_timeout_special_plays
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb)
    RETURNING id
    """
    
    print(f"DEBUG - Simulation data: {simulation_data}")
    params = (
        game_id,
        simulation_data.win_probability,
        simulation_data.projected_score,
        simulation_data.sim_overall_summary,
        simulation_data.sim_success_factors,
        simulation_data.sim_key_matchups,
        simulation_data.sim_win_loss_patterns,
        simulation_data.sim_critical_advantage,
        simulation_data.sim_keys_to_victory,
        json.dumps([adj.model_dump(mode="json") for adj in simulation_data.sim_situational_adjustments]),
        json.dumps([play.model_dump(mode="json") for play in simulation_data.playbook_offensive_plays]),
        json.dumps([play.model_dump(mode="json") for play in simulation_data.playbook_defensive_plays]),
        json.dumps([play.model_dump(mode="json") for play in simulation_data.playbook_special_situations]),
        json.dumps([play.model_dump(mode="json") for play in simulation_data.playbook_inbound_plays]),
        json.dumps([play.model_dump(mode="json") for play in simulation_data.playbook_after_timeout_special_plays]),
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def insert_report(game_id, report_type, file_path):
    """
    Insert a report into the database
    
    Args:
        game_id: Game ID
        report_type: Report type (team_analysis, opponent_analysis, game_analysis)
        file_path: Path to the report file
        
    Returns:
        (Report ID, Report UUID) if successful, None otherwise
    """
    query = """
    INSERT INTO reports (game_id, report_type, file_path)
    VALUES (%s, %s, %s)
    RETURNING id, uuid
    """
    
    params = (
        game_id,
        report_type,
        file_path
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"], result[0]["uuid"]
    return None

def get_report(report_id: int):
    query = """
    SELECT id, uuid, game_id, report_type, file_path FROM reports
    WHERE id = %s
    """
    result = execute_query(query, (report_id,))
    return result[0]

def get_report_by_game_id(game_id: int, report_type: str):
    query = """
    SELECT id, uuid, game_id, report_type, file_path FROM reports
    WHERE game_id = %s AND report_type = %s
    """
    result = execute_query(query, (game_id, report_type))
    return result[0]

def insert_player_raw_stats(player_id, stats_data: PlayerStats, game_id=None):
    """
    Insert raw player statistics into the database
    
    Args:
        player_id: Player ID
        stats_data: Dictionary containing player statistics
        game_id: Game ID (optional)
        
    Returns:
        Raw stats ID if successful, None otherwise
    """
    query = """
    INSERT INTO player_raw_stats (
        player_id, game_id, fgm, fga, fg2m, fg2a, fg3m, fg3a,
        ftm, fta, total_rebounds, offensive_rebounds, defensive_rebounds,
        total_assists, total_steals, total_blocks, total_turnovers
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    
    params = (
        player_id,
        game_id,
        stats_data.FGM,
        stats_data.FGA,
        stats_data.FGM2,
        stats_data.FGA2,
        stats_data.FGM3,
        stats_data.FGA3,
        stats_data.FTM,
        stats_data.FTA,
        stats_data.REB,
        stats_data.OREB,
        stats_data.DREB,
        stats_data.AST,
        stats_data.STL,
        stats_data.BLK,
        stats_data.TO
    )
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def insert_player_projections(game_simulation_id, player_id, team_id, game_id, projection_data, is_home_team):
    """
    Insert player projection data into the database
    
    Args:
        game_simulation_id: Game simulation ID
        player_id: Player ID
        team_id: Team ID
        game_id: Game ID
        projection_data: Dictionary containing player projection data
        is_home_team: Whether the player is on the home team
        
    Returns:
        Projection ID if successful, None otherwise
    """
    query = """
    INSERT INTO player_projections (
        game_simulation_id, player_id, team_id, game_id, is_home_team,
        ppg, rpg, apg, fg_pct, fg3_pct, role
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    
    params = (
        game_simulation_id,
        player_id,
        team_id,
        game_id,
        is_home_team,
        float(projection_data.get("ppg", 0)),
        float(projection_data.get("rpg", 0)),
        float(projection_data.get("apg", 0)),
        projection_data.get("fg", "0%"),
        projection_data.get("3p", "0%"),
        projection_data.get("role", "")
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def insert_simulation_details(game_simulation_id, game_id, home_team_id, away_team_id, simulation_data):
    """
    Insert detailed simulation results into the database
    
    Args:
        game_simulation_id: Game simulation ID
        game_id: Game ID
        home_team_id: Home team ID
        away_team_id: Away team ID
        simulation_data: Dictionary containing simulation data
        
    Returns:
        Simulation details ID if successful, None otherwise
    """
    query = """
    INSERT INTO simulation_details (
        game_simulation_id, game_id, home_team_id, away_team_id,
        num_simulations, home_team_wins, away_team_wins,
        home_team_win_pct, away_team_win_pct,
        avg_home_score, avg_away_score,
        closest_game_margin, blowout_game_margin,
        margin_distribution, avg_effects
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    
    # Convert margin_distribution and avg_effects to JSONB
    import json
    margin_distribution = json.dumps(simulation_data.get("marginDistribution", {}))
    avg_effects = json.dumps(simulation_data.get("avgEffects", {}))
    
    params = (
        game_simulation_id,
        game_id,
        home_team_id,
        away_team_id,
        simulation_data.get("numSimulations", 0),
        simulation_data.get("teamAWins", 0),
        simulation_data.get("teamBWins", 0),
        simulation_data.get("teamAWinPct", 0),
        simulation_data.get("teamBWinPct", 0),
        simulation_data.get("avgScoreA", 0),
        simulation_data.get("avgScoreB", 0),
        simulation_data.get("closestGame", {}).get("margin", 0),
        simulation_data.get("blowoutGame", {}).get("margin", 0),
        margin_distribution,
        avg_effects
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def find_player_by_name(player_name, team_id):
    """
    Find a player by name in a specific team
    
    Args:
        player_name: Player name
        team_id: Team ID
        
    Returns:
        Player ID if found, None otherwise
    """
    query = """
    SELECT id FROM players
    WHERE team_id = %s AND name LIKE %s
    LIMIT 1
    """
    
    # Remove jersey number if present
    name_only = player_name.split('#')[0].strip()
    
    result = execute_query(query, (team_id, f"%{name_only}%"))
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def get_recent_analyses(limit=5, user_id=None):
    """
    Get recent analyses from the database
    
    Args:
        limit: Maximum number of analyses to return
        user_id: User ID to filter by (optional)
        
    Returns:
        List of analyses
    """
    if user_id:
        query = """
        SELECT g.id as game_id, 
               ht.name as home_team, 
               at.name as away_team, 
               gs.projected_score, 
               gs.win_probability,
               r.id as report_id,
               r.file_path as report_path,
               tr1.file_path as team_report_path,
               tr2.file_path as opponent_report_path,
               g.created_at
        FROM games g
        JOIN teams ht ON g.home_team_id = ht.id
        JOIN teams at ON g.away_team_id = at.id
        LEFT JOIN game_simulations gs ON g.id = gs.game_id
        LEFT JOIN reports r ON g.id = r.game_id AND r.report_type = 'game_analysis'
        LEFT JOIN reports tr1 ON g.id = tr1.game_id AND tr1.report_type = 'team_analysis'
        LEFT JOIN reports tr2 ON g.id = tr2.game_id AND tr2.report_type = 'opponent_analysis'
        WHERE g.user_id = %s
        ORDER BY g.created_at DESC
        LIMIT %s
        """
        return execute_query(query, (user_id, limit))
    else:
        query = """
        SELECT g.id as game_id, 
               ht.name as home_team, 
               at.name as away_team, 
               gs.projected_score, 
               gs.win_probability,
               r.id as report_id,
               r.file_path as report_path,
               tr1.file_path as team_report_path,
               tr2.file_path as opponent_report_path,
               g.created_at
        FROM games g
        JOIN teams ht ON g.home_team_id = ht.id
        JOIN teams at ON g.away_team_id = at.id
        LEFT JOIN game_simulations gs ON g.id = gs.game_id
        LEFT JOIN reports r ON g.id = r.game_id AND r.report_type = 'game_analysis'
        LEFT JOIN reports tr1 ON g.id = tr1.game_id AND tr1.report_type = 'team_analysis'
        LEFT JOIN reports tr2 ON g.id = tr2.game_id AND tr2.report_type = 'opponent_analysis'
        ORDER BY g.created_at DESC
        LIMIT %s
        """
        return execute_query(query, (limit,))

def create_user(email: str, password_hash: str, name: str, phone_number: str = None, school: str = None, role: str = None):
    """
    Create a new user in the database
    
    Args:
        email: User email
        password_hash: Hashed password
        name: User name
        phone_number: User phone number (optional)
        school: User school (optional)
        role: User role (optional)
        
    Returns:
        User ID if successful, None otherwise
    """
    query = """
    INSERT INTO users (email, password_hash, name, phone_number, school, role)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    
    params = (
        email,
        password_hash,
        name,
        phone_number,
        school,
        role
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def get_user_by_email(email: str):
    """
    Get a user by email
    
    Args:
        email: User email
        
    Returns:
        User data if found, None otherwise
    """
    query = """
    SELECT id, email, password_hash, name, phone_number, school, role, confirmed
    FROM users
    WHERE email = %s
    """
    
    result = execute_query(query, (email,))
    if result and len(result) > 0:
        return result[0]
    return None

def get_public_user_by_email(email: str):
    """
    Get only public user information by email, no id or password hash
    """
    query = """
    SELECT email, name, phone_number, school, role
    FROM users
    WHERE email = %s
    """
    result = execute_query(query, (email,))
    if result and len(result) > 0:
        return result[0]
    return None

def update_user_password(user_id: int, password_hash: str):
    """
    Update a user's password
    
    Args:
        user_id: User ID
        password_hash: New hashed password
        
    Returns:
        True if successful, False otherwise
    """
    query = """
    UPDATE users
    SET password_hash = %s
    WHERE id = %s
    """
    
    result = execute_query(query, (password_hash, user_id), fetch=False)
    return result is not None

def confirm_user(user_id: int):
    """
    Confirm a user's email
    """
    query = """
    UPDATE users
    SET confirmed = TRUE
    WHERE id = %s
    """
    result = execute_query(query, (user_id), fetch=False)
    return result is not None

def create_session(user_id: int, session_token: str, expires_at: str):
    """
    Create a new session for a user
    
    Args:
        user_id: User ID
        session_token: Session token
        expires_at: Session expiration timestamp
        
    Returns:
        Session ID if successful, None otherwise
    """
    query = """
    INSERT INTO sessions (user_id, session_token, expires_at)
    VALUES (%s, %s, %s)
    RETURNING id
    """
    
    params = (
        user_id,
        session_token,
        expires_at
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def get_session(session_token: str):
    """
    Get a session by token
    
    Args:
        session_token: Session token
        
    Returns:
        Session data if found and not expired, None otherwise
    """
    query = """
    SELECT s.*, u.email, u.name, u.role
    FROM sessions s
    JOIN users u ON s.user_id = u.id
    WHERE s.session_token = %s AND s.expires_at > NOW()
    """
    
    result = execute_query(query, (session_token,))
    if result and len(result) > 0:
        return result[0]
    return None

def delete_session(session_token: str):
    """
    Delete a session
    
    Args:
        session_token: Session token
        
    Returns:
        True if successful, False otherwise
    """
    query = """
    DELETE FROM sessions
    WHERE session_token = %s
    """
    
    result = execute_query(query, (session_token,), fetch=False)
    return result is not None

def delete_expired_sessions():
    """
    Delete all expired sessions
    
    Returns:
        True if successful, False otherwise
    """
    query = """
    DELETE FROM sessions
    WHERE expires_at <= NOW()
    """
    
    result = execute_query(query, fetch=False)
    return result is not None

def create_otp(user_id: int, otp: str):
    """
    Create a unique token for a user
    """
    query = """
    INSERT INTO one_time_passwords (user_id, otp)
    VALUES (%s, %s)
    """
    execute_query(query, (user_id, otp))

def verify_otp(user_id: int, otp: str):
    """
    Verify a unique token and return associated user_id
    """
    query = """
    SELECT user_id FROM one_time_passwords WHERE user_id = %s AND otp = %s
    """
    result = execute_query(query, (user_id, otp))
    if result and len(result) > 0:
        return True
    return False

def delete_otp(user_id: int, otp: str):

    """
    Delete a unique token
    """
    query = """
    DELETE FROM one_time_passwords WHERE user_id = %s AND otp = %s
    """
    result = execute_query(query, (user_id, otp), fetch=False)


class TeamResponse(BaseModel):
    id: int
    name: str
    record: Optional[str]
    ranking: Optional[str]

def get_team_by_id(team_id: int) -> Optional[TeamResponse]:
    """
    Get a team by its ID
    
    Args:
        team_id: Team ID
        
    Returns:
        Team object if found, None otherwise
    """
    query = """
    SELECT * FROM teams WHERE id = %s
    """
    results = execute_query(query, (team_id,))
    if results and len(results) > 0:
        return TeamResponse(**results[0])
    return None

class TeamStatsResponse(BaseModel):
    ppg: Optional[float]
    fg_pct: Optional[str]
    fg_made: Optional[float]
    fg_attempted: Optional[float]
    fg3_pct: Optional[str]
    fg3_made: Optional[float]
    fg3_attempted: Optional[float]
    ft_pct: Optional[str]
    ft_made: Optional[float]
    ft_attempted: Optional[float]
    rebounds: Optional[float]
    offensive_rebounds: Optional[float]
    defensive_rebounds: Optional[float]
    assists: Optional[float]
    steals: Optional[float]
    blocks: Optional[float]
    turnovers: Optional[float]
    assist_to_turnover: Optional[float]
    is_season_average: Optional[bool]

def get_team_stats_from_game(game_id: int, team_id: int) -> Optional[TeamStatsResponse]:
    """
    Get team statistics for a specific game
    
    Args:
        game_id: Game ID
        
    Returns:
        List of TeamStats objects
    """
    query = """
    SELECT * FROM team_stats WHERE game_id = %s AND team_id = %s LIMIT 1
    """
    results = execute_query(query, (game_id, team_id))
    if results:
        return TeamStatsResponse(**results[0])
    return None


class TeamAnalysisResponse(BaseModel):
    playing_style: str
    strengths: List[str]
    weaknesses: List[str]
    key_players: List[str]
    offensive_keys: List[str]
    defensive_keys: List[str]
    game_factors: List[str]
    rotation_plan: List[str]
    situational_adjustments: List[str]
    game_keys: List[str]
    

def get_team_analysis_by_team_id(team_id: int) -> Optional[TeamAnalysisResponse]:
    """
    Get team analysis by team ID
    
    Args:
        team_id: Team ID
        
    Returns:
        TeamAnalysisResponse object if found, None otherwise
    """
    query = """
    SELECT * FROM team_analysis WHERE team_id = %s ORDER BY created_at DESC LIMIT 1
    """
    results = execute_query(query, (team_id,))
    if results and len(results) > 0:
        return TeamAnalysisResponse.model_validate(results[0])
    return None


class Game(BaseModel):
    id: int
    uuid: str
    home_team_id: int
    away_team_id: int
    user_id: Optional[int]
    location: Optional[str]
    home_score: Optional[int]
    away_score: Optional[int]
    status: Optional[str]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]

def get_game_by_uuid(game_uuid: str) -> Optional[Game]:
    """
    Get a game by its UUID
    
    Args:
        game_uuid: Game UUID
        
    Returns:
        Game object if found, None otherwise
    """
    query = """
    SELECT * FROM games WHERE uuid = %s
    """
    results = execute_query(query, (game_uuid,))
    if results and len(results) > 0:
        return Game(**results[0])
    return None


class GameSimulationResponse(BaseModel):
    id: Optional[int]
    game_id: int
    win_probability: Optional[str]
    projected_score: Optional[str]
    sim_overall_summary: Optional[str]
    sim_success_factors: Optional[str]
    sim_key_matchups: Optional[str]
    sim_win_loss_patterns: Optional[str]
    sim_critical_advantage: Optional[str]
    sim_keys_to_victory: List[str]
    sim_situational_adjustments: List[SituationalAdjustment]
    playbook_offensive_plays: List[PlaybookPlay]
    playbook_defensive_plays: List[PlaybookPlay]
    playbook_special_situations: List[PlaybookPlay]
    playbook_inbound_plays: List[PlaybookPlay]
    playbook_after_timeout_special_plays: List[PlaybookPlay]


def get_game_simulation(game_id: int) -> Optional[GameSimulationResponse]:
    """
    Get game simulation data for a specific game
    
    Args:
        game_id: Game ID
        
    Returns:
        GameSimulationResponse object if found, None otherwise
    """
    query = """
    SELECT * FROM game_simulations WHERE game_id = %s
    """
    results = execute_query(query, (game_id,))
    if results and len(results) > 0:
        return GameSimulationResponse.model_validate(results[0])
    return None

class ProjectedPlayer(BaseModel):
    id: int
    player_id: int
    team_id: int
    game_id: int
    name: str
    number: int
    is_home_team: bool
    ppg: float
    rpg: float
    apg: float
    fg_pct: str
    fg3_pct: str
    role: str
    strengths: List[str]
    weaknesses: List[str]
    actual_ppg: Optional[float]
    actual_rpg: Optional[float]
    actual_apg: Optional[float]
    actual_fg_pct: Optional[str]
    actual_fg3_pct: Optional[str]
    actual_ft_pct: Optional[str]
    actual_spg: Optional[float]
    actual_bpg: Optional[float]
    actual_topg: Optional[float]
    actual_minutes: Optional[float]

def get_projected_player_for_game(game_id: int, team_id: int) -> Optional[List[ProjectedPlayer]]:
    """
    Get projected player statistics for a specific game and team
    
    Args:
        game_id: Game ID
        team_id: Team ID
        
    Returns:
        List of ProjectedPlayer objects if found, None otherwise
    """
    query = """
    SELECT 
        p.name,
        p.number,
        p.strengths,
        p.weaknesses,
        pp.*,
        ps.ppg as actual_ppg,
        ps.rpg as actual_rpg,
        ps.apg as actual_apg,
        ps.fg_pct as actual_fg_pct,
        ps.fg3_pct as actual_fg3_pct,
        ps.ft_pct as actual_ft_pct,
        ps.spg as actual_spg,
        ps.bpg as actual_bpg,
        ps.topg as actual_topg,
        ps.minutes as actual_minutes
    FROM player_projections pp
    LEFT JOIN player_stats ps ON pp.player_id = ps.player_id
    JOIN players p ON pp.player_id = p.id
    WHERE pp.game_id = %s AND pp.team_id = %s
    """
    
    results = execute_query(query, (game_id, team_id))
    if results:
        return [ProjectedPlayer(**result) for result in results]
    return None


class ReportSummary(BaseModel):
    id: int
    game_uuid: str
    home_team_id: int
    away_team_id: int
    home_team: str
    away_team: str
    created_at: datetime.datetime
    

def get_report_summaries_by_user_id(user_id: int) -> List[ReportSummary]:
    """
    Get report summaries for a user
    
    Args:
        user_id: User ID to get report summaries for
        
    Returns:
        List of ReportSummary objects containing report metadata
    """
    query = """
    SELECT 
        r.id,
        g.uuid as game_uuid,
        g.home_team_id,
        g.away_team_id,
        ht.name as home_team,
        at.name as away_team,
        r.created_at
    FROM reports r
    JOIN games g ON r.game_id = g.id
    JOIN teams ht ON g.home_team_id = ht.id
    JOIN teams at ON g.away_team_id = at.id
    WHERE g.user_id = %s
    ORDER BY r.created_at DESC
    """
    
    results = execute_query(query, (user_id,))
    if results:
        return [ReportSummary(**result) for result in results]
    return []
