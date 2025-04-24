import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """
    Get a connection to the PostgreSQL database
    
    Returns:
        Connection object
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "anova"),
            user=os.getenv("DB_USER", "anova_user"),
            password=os.getenv("DB_PASSWORD", "anova@bask3t"),
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
            print(f"DEBUG - Executing query: {query}")
            print(f"DEBUG - With params: {params}")
            cur.execute(query, params)
            
            # Always commit changes, regardless of fetch
            conn.commit()
            print("DEBUG - Changes committed to database")
            
            if fetch:
                results = cur.fetchall()
                print(f"DEBUG - Query results: {results}")
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
    INSERT INTO teams (name, record, ranking, playing_style)
    VALUES (%s, %s, %s, %s)
    RETURNING id
    """
    
    params = (
        team_data.get("team_name"),
        team_data.get("team_record"),
        team_data.get("team_ranking"),
        team_data.get("playing_style")
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
        team_id, game_id, is_season_average, ppg, fg_percentage, 
        fg_made, fg_attempted, three_pt_percentage, three_pt_made, three_pt_attempted,
        ft_percentage, ft_made, ft_attempted, rebounds, offensive_rebounds, 
        defensive_rebounds, assists, steals, blocks, turnovers, assist_to_turnover_ratio
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
    three_pt_pct = team_stats.get("3FG%", "0%")
    ft_pct = team_stats.get("FT%", "0%")
    
    # Estimate made and attempted values (these are not in the original data)
    # We'll use placeholder values since we don't have the actual data
    fg_made = 0
    fg_attempted = 0
    three_pt_made = 0
    three_pt_attempted = 0
    ft_made = 0
    ft_attempted = 0
    
    params = (
        team_id,
        game_id,
        is_season_average,
        ppg,
        fg_pct,
        fg_made,
        fg_attempted,
        three_pt_pct,
        three_pt_made,
        three_pt_attempted,
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
    INSERT INTO players (team_id, name, jersey_number, position)
    VALUES (%s, %s, %s, %s)
    RETURNING id
    """
    
    params = (
        team_id,
        player_data.get("name"),
        player_data.get("number"),
        player_data.get("position")
    )
    
    result = execute_query(query, params)
    if result and len(result) > 0:
        return result[0]["id"]
    return None

def insert_player_stats(player_id, stats_data, game_id=None, is_season_average=True):
    """
    Insert player statistics into the database
    
    Args:
        player_id: Player ID
        stats_data: Dictionary containing player statistics
        game_id: Game ID (optional)
        is_season_average: Whether these stats are season averages
        
    Returns:
        Stats ID if successful, None otherwise
    """
    query = """
    INSERT INTO player_stats (
        player_id, game_id, games_played, ppg, fg_pct, fg3_pct, ft_pct,
        rpg, apg, spg, bpg, topg, minutes, is_season_average
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    
    player_stats = stats_data.get("stats", {})
    
    params = (
        player_id,
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

def insert_game(home_team_id, away_team_id, date=None, location=None):
    """
    Insert a game into the database
    
    Args:
        home_team_id: Home team ID
        away_team_id: Away team ID
        date: Game date (optional)
        location: Game location (optional)
        
    Returns:
        Game ID if successful, None otherwise
    """
    query = """
    INSERT INTO games (home_team_id, away_team_id, date, location)
    VALUES (%s, %s, %s, %s)
    RETURNING id
    """
    
    params = (
        home_team_id,
        away_team_id,
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

def get_recent_analyses(limit=5):
    """
    Get recent analyses from the database
    
    Args:
        limit: Maximum number of analyses to return
        
    Returns:
        List of analyses
    """
    query = """
    SELECT g.id as game_id, 
           ht.name as home_team, 
           at.name as away_team, 
           gs.projected_score, 
           gs.win_probability,
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
