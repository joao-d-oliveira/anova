import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from config import Config

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

def insert_team(team_data):
    """
    Insert a team into the database
    
    Args:
        team_data: Dictionary containing team data
        
    Returns:
        Team ID if successful, None otherwise
    """
    query = """
    INSERT INTO teams (name, record, ranking, playing_style, record_date)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id
    """
    
    # Parse record_date if it exists, otherwise use current date
    from datetime import datetime
    record_date = None
    if "record_date" in team_data:
        try:
            record_date = datetime.strptime(team_data["record_date"], "%Y-%m-%d").date()
        except:
            record_date = datetime.now().date()
    else:
        record_date = datetime.now().date()
    
    params = (
        team_data.get("team_name"),
        team_data.get("team_record"),
        team_data.get("team_ranking"),
        team_data.get("playing_style"),
        record_date
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def insert_team_stats(team_id, stats_data, game_id=None, is_season_average=True):
    """
    Insert team statistics into the database
    
    Args:
        team_id: Team ID
        stats_data: Dictionary containing team statistics
        game_id: Game ID (optional)
        is_season_average: Whether these stats are season averages
        
    Returns:
        Stats ID if successful, None otherwise
    """
    # Using the exact column names from the database schema
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
    
    team_stats = stats_data.get("team_stats", {})
    
    # Convert numeric values
    ppg = float(team_stats.get("PPG", 0))
    rebounds = float(team_stats.get("REB", 0))
    offensive_rebounds = float(team_stats.get("OREB", 0))
    defensive_rebounds = float(team_stats.get("DREB", 0))
    assists = float(team_stats.get("AST", 0))
    steals = float(team_stats.get("STL", 0))
    blocks = float(team_stats.get("BLK", 0))
    turnovers = float(team_stats.get("TO", 0))
    
    # Calculate assist to turnover ratio
    assist_to_turnover = 0
    if turnovers > 0:
        assist_to_turnover = round(assists / turnovers, 2)
    else:
        assist_to_turnover = team_stats.get("A/TO", 0)
    
    # Extract percentages
    fg_pct = team_stats.get("FG%", "0%")
    fg3_pct = team_stats.get("3FG%", "0%")
    ft_pct = team_stats.get("FT%", "0%")
    
    # Extract made and attempted values if available
    fg_made = team_stats.get("FGM", 0)
    fg_attempted = team_stats.get("FGA", 0)
    fg3_made = team_stats.get("3FGM", 0)
    fg3_attempted = team_stats.get("3FGA", 0)
    ft_made = team_stats.get("FTM", 0)
    ft_attempted = team_stats.get("FTA", 0)
    
    params = (
        team_id,
        game_id,
        is_season_average,
        ppg,
        fg_pct,
        fg_made,
        fg_attempted,
        fg3_pct,
        fg3_made,
        fg3_attempted,
        ft_pct,
        ft_made,
        ft_attempted,
        rebounds,
        offensive_rebounds,
        defensive_rebounds,
        assists,
        steals,
        blocks,
        turnovers,
        assist_to_turnover
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def insert_player(team_id, player_data):
    """
    Insert a player into the database
    
    Args:
        team_id: Team ID
        player_data: Dictionary containing player data
        
    Returns:
        Player ID if successful, None otherwise
    """
    query = """
    INSERT INTO players (team_id, name, number, position, height, weight, year)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    
    params = (
        team_id,
        player_data.get("name"),
        player_data.get("number"),
        player_data.get("position"),
        player_data.get("height"),
        player_data.get("weight"),
        player_data.get("year")
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def insert_player_stats(player_id, stats_data, game_id=None, is_season_average=True, player_raw_stats_id=None):
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
    
    player_stats = stats_data.get("stats", {})
    
    params = (
        player_id,
        player_raw_stats_id,
        game_id,
        int(player_stats.get("GP", 0)),
        float(player_stats.get("PPG", 0)),
        player_stats.get("FG%", "0%"),
        player_stats.get("3FG%", "0%"),
        player_stats.get("FT%", "0%"),
        float(player_stats.get("RPG", 0)),
        float(player_stats.get("APG", 0)),
        float(player_stats.get("SPG", 0)),
        float(player_stats.get("BPG", 0)),
        float(player_stats.get("TOPG", 0)),
        float(player_stats.get("MINS", 0)),
        is_season_average
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def insert_team_analysis(team_id, analysis_data):
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
        team_id, strengths, weaknesses, key_players,
        offensive_keys, defensive_keys, game_factors,
        rotation_plan, situational_adjustments, game_keys
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    
    params = (
        team_id,
        analysis_data.get("team_strengths", []),
        analysis_data.get("team_weaknesses", []),
        analysis_data.get("key_players", []),
        analysis_data.get("offensive_keys", []),
        analysis_data.get("defensive_keys", []),
        analysis_data.get("game_factors", []),
        analysis_data.get("rotation_plan"),
        analysis_data.get("situational_adjustments", []),
        analysis_data.get("game_keys", [])
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
    RETURNING id
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
        return result[0]["id"]
    return None

def insert_game_simulation(game_id, simulation_data):
    """
    Insert game simulation into the database
    
    Args:
        game_id: Game ID
        simulation_data: Dictionary containing simulation data
        
    Returns:
        Simulation ID if successful, None otherwise
    """
    query = """
    INSERT INTO game_simulations (
        game_id, win_probability, projected_score,
        sim_overall_summary, sim_success_factors,
        sim_key_matchups, sim_win_loss_patterns
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    
    print(f"DEBUG - Simulation data: {simulation_data}")
    
    # Extract simulation data with detailed logging
    win_probability = simulation_data.get("win_probability")
    projected_score = simulation_data.get("projected_score")
    sim_overall_summary = simulation_data.get("sim_overall_summary")
    sim_success_factors = simulation_data.get("sim_success_factors")
    sim_key_matchups = simulation_data.get("sim_key_matchups")
    sim_win_loss_patterns = simulation_data.get("sim_win_loss_patterns")
    
    print(f"DEBUG - Win probability: {win_probability}")
    print(f"DEBUG - Projected score: {projected_score}")
    print(f"DEBUG - Overall summary: {sim_overall_summary}")
    
    params = (
        game_id,
        win_probability,
        projected_score,
        sim_overall_summary,
        sim_success_factors,
        sim_key_matchups,
        sim_win_loss_patterns
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
        Report ID if successful, None otherwise
    """
    query = """
    INSERT INTO reports (game_id, report_type, file_path)
    VALUES (%s, %s, %s)
    RETURNING id
    """
    
    params = (
        game_id,
        report_type,
        file_path
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def insert_player_raw_stats(player_id, stats_data, game_id=None):
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
    
    player_stats = stats_data.get("stats", {})
    
    params = (
        player_id,
        game_id,
        player_stats.get("FGM", 0),
        player_stats.get("FGA", 0),
        player_stats.get("2FGM", 0),
        player_stats.get("2FGA", 0),
        player_stats.get("3FGM", 0),
        player_stats.get("3FGA", 0),
        player_stats.get("FTM", 0),
        player_stats.get("FTA", 0),
        player_stats.get("REB", 0),
        player_stats.get("OREB", 0),
        player_stats.get("DREB", 0),
        player_stats.get("AST", 0),
        player_stats.get("STL", 0),
        player_stats.get("BLK", 0),
        player_stats.get("TO", 0)
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
    SELECT id, email, password_hash, name, phone_number, school, role
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


def create_unique_token(user_id: int, token: str):
    """
    Create a unique token for a user
    """
    query = """
    INSERT INTO one_time_tokens (user_id, token)
    VALUES (%s, %s)
    """
    result = execute_query(query, (user_id, token))
    return result is not None

def verify_unique_token(token: str):
    """
    Verify a unique token and return associated user_id
    """
    query = """
    SELECT user_id FROM one_time_tokens WHERE token = %s
    """
    result = execute_query(query, (token,))
    if result and len(result) > 0:
        return result[0]["user_id"]
    return None
