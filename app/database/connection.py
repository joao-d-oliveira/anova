import datetime
import json
import os
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, aliased
import logging

from pydantic import BaseModel
from app.config import Config
from app.llmmodels import (
    GameSimulation,
    PlaybookPlay,
    Player,
    PlayerStats,
    SituationalAdjustment,
    TeamAnalysis,
    TeamDetails,
    TeamStats,
)
from app.database.models import (
    UserDB,
    TeamDB,
    PlayerDB,
    GameDB,
    PlayerRawStatsDB,
    TeamStatsDB,
    PlayerStatsDB,
    TeamAnalysisDB,
    GameSimulationDB,
    PlayerProjectionDB,
    SimulationDetailsDB,
    ReportDB,
    OneTimePasswordDB,
)
from app.models import PlayerProjectionResponse

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
        logger.info(
            f"Connecting to database: {config.db_host}:{config.db_port}/{config.db_name}"
        )

        conn = psycopg2.connect(
            host=config.db_host,
            port=config.db_port,
            database=config.db_name,
            user=config.db_user,
            password=config.db_password,
            cursor_factory=RealDictCursor,
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


def get_or_create_user(
    db: Session,
    cognito_id: str,
    email: str,
    name: str,
    phone_number: str = None,
    school: str = None,
    role: str = None,
):
    """
    Get or create a user in the database based on Cognito ID

    Args:
        db: SQLAlchemy database session
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
    user = db.query(UserDB).filter(UserDB.cognito_id == cognito_id).first()

    if user:
        return user.id

    # If user doesn't exist, create it
    new_user = UserDB(
        cognito_id=cognito_id,
        email=email,
        name=name,
        phone_number=phone_number,
        school=school,
        role=role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.id


def insert_team(db: Session, team_details: TeamDetails):
    """
    Insert a team into the database

    Args:
        db: SQLAlchemy database session
        team_details: TeamDetails object containing team data
        team_analysis: TeamAnalysis object containing team analysis

    Returns:
        Team ID if successful, None otherwise
    """
    # Parse record_date if it exists, otherwise use current date
    record_date = None
    try:
        record_date = datetime.datetime.strptime(
            team_details.record_date, "%Y-%m-%d"
        ).date()
    except:
        record_date = datetime.datetime.now().date()

    new_team = TeamDB(
        name=team_details.team_name,
        record=team_details.record,
        ranking=team_details.team_ranking,
        record_date=record_date,
    )

    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return new_team.id


def insert_team_stats(
    db: Session,
    team_id: int,
    stats_data: TeamStats,
    game_id: int = None,
    is_season_average: bool = True,
):
    """
    Insert team statistics into the database

    Args:
        db: SQLAlchemy database session
        team_id: Team ID
        stats_data: TeamStats object containing team statistics
        game_id: Game ID (optional)
        is_season_average: Whether these stats are season averages

    Returns:
        Stats ID if successful, None otherwise
    """
    # Calculate assist to turnover ratio
    assist_to_turnover = 0
    if stats_data.TO > 0:
        assist_to_turnover = round(stats_data.AST / stats_data.TO, 2)
    else:
        assist_to_turnover = stats_data.A_TO

    new_team_stats = TeamStatsDB(
        team_id=team_id,
        game_id=game_id,
        is_season_average=is_season_average,
        ppg=stats_data.PPG,
        fg_pct=stats_data.FG_percent,
        fg_made=stats_data.FGM,
        fg_attempted=stats_data.FGA,
        fg3_pct=stats_data.FG3_percent,
        fg3_made=stats_data.FGM3,
        fg3_attempted=stats_data.FGA3,
        ft_pct=stats_data.FT_percent,
        ft_made=stats_data.FTM,
        ft_attempted=stats_data.FTA,
        rebounds=stats_data.REB,
        offensive_rebounds=stats_data.OREB,
        defensive_rebounds=stats_data.DREB,
        assists=stats_data.AST,
        steals=stats_data.STL,
        blocks=stats_data.BLK,
        turnovers=stats_data.TO,
        assist_to_turnover=assist_to_turnover,
    )

    db.add(new_team_stats)
    db.commit()
    db.refresh(new_team_stats)
    return new_team_stats.id


def update_team_stats_game_id(db: Session, team_stats_id: int, game_id: int):
    """
    Update the game_id for a team stats record

    Args:
        db: SQLAlchemy database session
        team_stats_id: Team stats ID
        game_id: Game ID to set
    """
    team_stats = db.query(TeamStatsDB).filter(TeamStatsDB.id == team_stats_id).first()
    if team_stats:
        team_stats.game_id = game_id
        db.commit()


def insert_player(db: Session, team_id: int, player_data: Player):
    """
    Insert a player into the database

    Args:
        db: SQLAlchemy database session
        team_id: Team ID
        player_data: Player object containing player data

    Returns:
        Player ID if successful, None otherwise
    """
    new_player = PlayerDB(
        team_id=team_id,
        name=player_data.name,
        number=player_data.number,
        position=player_data.position,
        height=player_data.height,
        weight=player_data.weight,
        year=player_data.year,
        strengths=player_data.strengths,
        weaknesses=player_data.weaknesses,
    )

    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player.id


def insert_player_stats(
    db: Session,
    player_id: int,
    stats_data: PlayerStats,
    game_id: int = None,
    is_season_average: bool = True,
    player_raw_stats_id: int = None,
):
    """
    Insert player statistics into the database

    Args:
        db: SQLAlchemy database session
        player_id: Player ID
        stats_data: PlayerStats object containing player statistics
        game_id: Game ID (optional)
        is_season_average: Whether these stats are season averages
        player_raw_stats_id: ID of raw stats record (optional)

    Returns:
        Stats ID if successful, None otherwise
    """
    new_player_stats = PlayerStatsDB(
        player_id=player_id,
        player_raw_stats_id=player_raw_stats_id,
        game_id=game_id,
        games_played=stats_data.GP,
        ppg=stats_data.PPG,
        fg_pct=stats_data.FG_percent,
        fg3_pct=stats_data.FG3_percent,
        ft_pct=stats_data.FT_percent,
        rpg=stats_data.RPG,
        apg=stats_data.APG,
        spg=stats_data.SPG,
        bpg=stats_data.BPG,
        topg=stats_data.TOPG,
        minutes=stats_data.MINS,
        is_season_average=is_season_average,
    )

    db.add(new_player_stats)
    db.commit()
    db.refresh(new_player_stats)
    return new_player_stats.id


def insert_team_analysis(db: Session, team_id: int, analysis_data: TeamAnalysis):
    """
    Insert team analysis into the database

    Args:
        db: SQLAlchemy database session
        team_id: Team ID
        analysis_data: TeamAnalysis object containing team analysis

    Returns:
        Analysis ID if successful, None otherwise
    """
    new_team_analysis = TeamAnalysisDB(
        team_id=team_id,
        playing_style=analysis_data.playing_style,
        strengths=analysis_data.team_strengths,
        weaknesses=analysis_data.team_weaknesses,
        key_players=analysis_data.key_players,
        offensive_keys=analysis_data.offensive_keys,
        defensive_keys=analysis_data.defensive_keys,
        game_factors=analysis_data.game_factors,
        rotation_plan=analysis_data.rotation_plan,
        situational_adjustments=analysis_data.situational_adjustments,
        game_keys=analysis_data.game_keys,
    )

    db.add(new_team_analysis)
    db.commit()
    db.refresh(new_team_analysis)
    return new_team_analysis.id


def insert_game(
    db: Session,
    home_team_id: int,
    away_team_id: int,
    user_id: int = None,
    date: datetime.date = None,
    location: str = None,
):
    """
    Insert a game into the database

    Args:
        db: SQLAlchemy database session
        home_team_id: Home team ID
        away_team_id: Away team ID
        user_id: User ID (optional)
        date: Game date (optional)
        location: Game location (optional)

    Returns:
        (Game ID, Game UUID) if successful, None otherwise
    """
    new_game = GameDB(
        home_team_id=home_team_id,
        away_team_id=away_team_id,
        user_id=user_id,
        date=date,
        location=location,
    )

    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    return new_game.id, str(new_game.uuid)


def insert_game_simulation(db: Session, game_id: int, simulation_data: GameSimulation):
    """
    Insert game simulation into the database

    Args:
        db: SQLAlchemy database session
        game_id: Game ID
        simulation_data: GameSimulation object containing simulation data

    Returns:
        Simulation ID if successful, None otherwise
    """
    new_simulation = GameSimulationDB(
        game_id=game_id,
        win_probability=simulation_data.win_probability,
        projected_score=simulation_data.projected_score,
        sim_overall_summary=simulation_data.sim_overall_summary,
        sim_success_factors=simulation_data.sim_success_factors,
        sim_key_matchups=simulation_data.sim_key_matchups,
        sim_win_loss_patterns=simulation_data.sim_win_loss_patterns,
        sim_critical_advantage=simulation_data.sim_critical_advantage,
        sim_keys_to_victory=simulation_data.sim_keys_to_victory,
        sim_situational_adjustments=simulation_data.sim_situational_adjustments,
        playbook_offensive_plays=simulation_data.playbook_offensive_plays,
        playbook_defensive_plays=simulation_data.playbook_defensive_plays,
        playbook_special_situations=simulation_data.playbook_special_situations,
        playbook_inbound_plays=simulation_data.playbook_inbound_plays,
        playbook_after_timeout_special_plays=simulation_data.playbook_after_timeout_special_plays,
    )

    db.add(new_simulation)
    db.commit()
    db.refresh(new_simulation)
    return new_simulation.id


def insert_report(db: Session, game_id: int, report_type: str, file_path: str):
    """
    Insert a report into the database

    Args:
        db: SQLAlchemy database session
        game_id: Game ID
        report_type: Report type (team_analysis, opponent_analysis, game_analysis)
        file_path: Path to the report file

    Returns:
        (Report ID, Report UUID) if successful, None otherwise
    """
    new_report = ReportDB(game_id=game_id, report_type=report_type, file_path=file_path)

    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report.id, new_report.uuid


def get_report(db: Session, report_id: int):
    """
    Get a report by ID

    Args:
        db: SQLAlchemy database session
        report_id: Report ID

    Returns:
        Report object if found, None otherwise
    """
    return db.query(ReportDB).filter(ReportDB.id == report_id).first()


def get_report_by_game_id(db: Session, game_id: int, report_type: str):
    """
    Get a report by game ID and type

    Args:
        db: SQLAlchemy database session
        game_id: Game ID
        report_type: Report type

    Returns:
        Report object if found, None otherwise
    """
    return (
        db.query(ReportDB)
        .filter(ReportDB.game_id == game_id, ReportDB.report_type == report_type)
        .first()
    )


def insert_player_raw_stats(
    db: Session, player_id: int, stats_data: PlayerStats, game_id: int = None
):
    """
    Insert raw player statistics into the database

    Args:
        db: SQLAlchemy database session
        player_id: Player ID
        stats_data: PlayerStats object containing player statistics
        game_id: Game ID (optional)

    Returns:
        Raw stats ID if successful, None otherwise
    """
    new_raw_stats = PlayerRawStatsDB(
        player_id=player_id,
        game_id=game_id,
        fgm=stats_data.FGM,
        fga=stats_data.FGA,
        fg2m=stats_data.FGM2,
        fg2a=stats_data.FGA2,
        fg3m=stats_data.FGM3,
        fg3a=stats_data.FGA3,
        ftm=stats_data.FTM,
        fta=stats_data.FTA,
        total_rebounds=stats_data.REB,
        offensive_rebounds=stats_data.OREB,
        defensive_rebounds=stats_data.DREB,
        total_assists=stats_data.AST,
        total_steals=stats_data.STL,
        total_blocks=stats_data.BLK,
        total_turnovers=stats_data.TO,
    )

    db.add(new_raw_stats)
    db.commit()
    db.refresh(new_raw_stats)
    return new_raw_stats.id


def insert_player_projections(
    db: Session,
    game_simulation_id: int,
    player_id: int,
    team_id: int,
    game_id: int,
    projection_data: dict,
    is_home_team: bool,
):
    """
    Insert player projection data into the database

    Args:
        db: SQLAlchemy database session
        game_simulation_id: Game simulation ID
        player_id: Player ID
        team_id: Team ID
        game_id: Game ID
        projection_data: Dictionary containing player projection data
        is_home_team: Whether the player is on the home team

    Returns:
        Projection ID if successful, None otherwise
    """
    new_projection = PlayerProjectionDB(
        game_simulation_id=game_simulation_id,
        player_id=player_id,
        team_id=team_id,
        game_id=game_id,
        is_home_team=is_home_team,
        ppg=float(projection_data.get("ppg", 0)),
        rpg=float(projection_data.get("rpg", 0)),
        apg=float(projection_data.get("apg", 0)),
        fg_pct=projection_data.get("fg", "0%"),
        fg3_pct=projection_data.get("3p", "0%"),
        role=projection_data.get("role", ""),
    )

    db.add(new_projection)
    db.commit()
    db.refresh(new_projection)
    return new_projection.id


def insert_simulation_details(
    db: Session,
    game_simulation_id: int,
    game_id: int,
    home_team_id: int,
    away_team_id: int,
    simulation_data: dict,
):
    """
    Insert detailed simulation results into the database

    Args:
        db: SQLAlchemy database session
        game_simulation_id: Game simulation ID
        game_id: Game ID
        home_team_id: Home team ID
        away_team_id: Away team ID
        simulation_data: Dictionary containing simulation data

    Returns:
        Simulation details ID if successful, None otherwise
    """
    new_simulation_details = SimulationDetailsDB(
        game_simulation_id=game_simulation_id,
        game_id=game_id,
        home_team_id=home_team_id,
        away_team_id=away_team_id,
        num_simulations=simulation_data.get("numSimulations", 0),
        home_team_wins=simulation_data.get("teamAWins", 0),
        away_team_wins=simulation_data.get("teamBWins", 0),
        home_team_win_pct=simulation_data.get("teamAWinPct", 0),
        away_team_win_pct=simulation_data.get("teamBWinPct", 0),
        avg_home_score=simulation_data.get("avgScoreA", 0),
        avg_away_score=simulation_data.get("avgScoreB", 0),
        closest_game_margin=simulation_data.get("closestGame", {}).get("margin", 0),
        blowout_game_margin=simulation_data.get("blowoutGame", {}).get("margin", 0),
        margin_distribution=simulation_data.get("marginDistribution", {}),
        avg_effects=simulation_data.get("avgEffects", {}),
    )

    db.add(new_simulation_details)
    db.commit()
    db.refresh(new_simulation_details)
    return new_simulation_details.id


def find_player_by_name(db: Session, player_name: str, team_id: int) -> PlayerDB | None:
    """
    Find a player by name in a specific team

    Args:
        db: SQLAlchemy database session
        player_name: Player name
        team_id: Team ID

    Returns:
        Player ID if found, None otherwise
    """
    # Remove jersey number if present
    name_only = player_name.split("#")[0].strip()

    player = (
        db.query(PlayerDB)
        .filter(PlayerDB.team_id == team_id, PlayerDB.name.ilike(f"%{name_only}%"))
        .first()
    )

    return player


def get_recent_analyses(db: Session, limit: int = 5, user_id: int = None):
    """
    Get recent analyses from the database

    Args:
        db: SQLAlchemy database session
        limit: Maximum number of analyses to return
        user_id: User ID to filter by (optional)

    Returns:
        List of analyses
    """
    query = (
        db.query(
            GameDB.id.label("game_id"),
            TeamDB.name.label("home_team"),
            TeamDB.name.label("away_team"),
            GameSimulationDB.projected_score,
            GameSimulationDB.win_probability,
            ReportDB.id.label("report_id"),
            ReportDB.file_path.label("report_path"),
            ReportDB.file_path.label("team_report_path"),
            ReportDB.file_path.label("opponent_report_path"),
            GameDB.created_at,
        )
        .join(TeamDB, GameDB.home_team_id == TeamDB.id)
        .join(TeamDB, GameDB.away_team_id == TeamDB.id)
        .outerjoin(GameSimulationDB, GameDB.id == GameSimulationDB.game_id)
        .outerjoin(ReportDB, GameDB.id == ReportDB.game_id)
    )

    if user_id:
        query = query.filter(GameDB.user_id == user_id)

    return query.order_by(GameDB.created_at.desc()).limit(limit).all()


def create_user(
    db: Session,
    email: str,
    password_hash: str,
    name: str,
    phone_number: str = None,
    school: str = None,
    role: str = None,
):
    """
    Create a new user in the database

    Args:
        db: SQLAlchemy database session
        email: User email
        password_hash: Hashed password
        name: User name
        phone_number: User phone number (optional)
        school: User school (optional)
        role: User role (optional)

    Returns:
        User ID if successful, None otherwise
    """
    new_user = UserDB(
        email=email,
        password_hash=password_hash,
        name=name,
        phone_number=phone_number,
        school=school,
        role=role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.id


def get_user_by_email(db: Session, email: str) -> Optional[UserDB]:
    """
    Get a user by email

    Args:
        db: SQLAlchemy database session
        email: User email

    Returns:
        User data if found, None otherwise
    """
    return db.query(UserDB).filter(UserDB.email == email).first()


def get_public_user_by_email(db: Session, email: str) -> Optional[UserDB]:
    """
    Get only public user information by email, no id or password hash

    Args:
        db: SQLAlchemy database session
        email: User email

    Returns:
        Public user data if found, None otherwise
    """
    return (
        db.query(UserDB)
        .filter(UserDB.email == email)
        .first()
    )


def update_user_password(db: Session, user_id: int, password_hash: str):
    """
    Update a user's password

    Args:
        db: SQLAlchemy database session
        user_id: User ID
        password_hash: New hashed password

    Returns:
        True if successful, False otherwise
    """
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if user:
        user.password_hash = password_hash
        user.confirmed = True
        db.commit()
        return True
    return False


def confirm_user(db: Session, user_id: int):
    """
    Confirm a user's email

    Args:
        db: SQLAlchemy database session
        user_id: User ID

    Returns:
        True if successful, False otherwise
    """
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if user:
        user.confirmed = True
        db.commit()
        return True
    return False


def create_otp(db: Session, user_id: int, otp: str):
    """
    Create a unique token for a user

    Args:
        db: SQLAlchemy database session
        user_id: User ID
        otp: One-time password
    """
    new_otp = OneTimePasswordDB(user_id=user_id, otp=otp)

    db.add(new_otp)
    db.commit()


def verify_otp(db: Session, user_id: int, otp: str):
    """
    Verify a unique token and return associated user_id

    Args:
        db: SQLAlchemy database session
        user_id: User ID
        otp: One-time password

    Returns:
        True if valid, False otherwise
    """
    return (
        db.query(OneTimePasswordDB)
        .filter(OneTimePasswordDB.user_id == user_id, OneTimePasswordDB.otp == otp)
        .first()
        is not None
    )


def delete_otp(db: Session, user_id: int, otp: str):
    """
    Delete a unique token

    Args:
        db: SQLAlchemy database session
        user_id: User ID
        otp: One-time password
    """
    db.query(OneTimePasswordDB).filter(
        OneTimePasswordDB.user_id == user_id, OneTimePasswordDB.otp == otp
    ).delete()
    db.commit()


def get_team_by_id(db: Session, team_id: int) -> Optional[TeamDB]:
    """
    Get a team by its ID

    Args:
        db: SQLAlchemy database session
        team_id: Team ID

    Returns:
        Team object if found, None otherwise
    """
    return db.query(TeamDB).filter(TeamDB.id == team_id).first()


def get_team_stats_from_game(
    db: Session, game_id: int, team_id: int
) -> Optional[TeamStatsDB]:
    """
    Get team statistics for a specific game

    Args:
        db: SQLAlchemy database session
        game_id: Game ID
        team_id: Team ID

    Returns:
        TeamStatsResponse object if found, None otherwise
    """
    stats = (
        db.query(TeamStatsDB)
        .filter(TeamStatsDB.game_id == game_id, TeamStatsDB.team_id == team_id)
        .first()
    )

    return stats


def get_team_analysis_by_team_id(db: Session, team_id: int) -> Optional[TeamAnalysisDB]:
    """
    Get team analysis by team ID

    Args:
        db: SQLAlchemy database session
        team_id: Team ID

    Returns:
        TeamAnalysisResponse object if found, None otherwise
    """
    analysis = (
        db.query(TeamAnalysisDB)
        .filter(TeamAnalysisDB.team_id == team_id)
        .order_by(TeamAnalysisDB.created_at.desc())
        .first()
    )

    return analysis


def get_game_by_uuid(db: Session, game_uuid: str) -> Optional[GameDB]:
    """
    Get a game by its UUID

    Args:
        db: SQLAlchemy database session
        game_uuid: Game UUID

    Returns:
        Game object if found, None otherwise
    """
    game = db.query(GameDB).filter(GameDB.uuid == game_uuid).first()
    return game


def get_game_simulation(db: Session, game_id: int) -> Optional[GameSimulationDB]:
    """
    Get game simulation data for a specific game

    Args:
        db: SQLAlchemy database session
        game_id: Game ID

    Returns:
        GameSimulationResponse object if found, None otherwise
    """
    simulation = (
        db.query(GameSimulationDB).filter(GameSimulationDB.game_id == game_id).first()
    )

    return simulation

def get_projected_player_for_game(
    db: Session, game_id: int, team_id: int
) -> Optional[List[PlayerProjectionResponse]]:
    """
    Get projected player statistics for a specific game and team

    Args:
        db: SQLAlchemy database session
        game_id: Game ID
        team_id: Team ID

    Returns:
        List of ProjectedPlayer objects if found, None otherwise
    """
    response: List[Tuple[PlayerProjectionDB, PlayerDB, PlayerStatsDB]] = (
        db.query(PlayerProjectionDB, PlayerDB, PlayerStatsDB)
        .join(PlayerDB, PlayerProjectionDB.player_id == PlayerDB.id)
        .outerjoin(
            PlayerStatsDB, PlayerProjectionDB.player_id == PlayerStatsDB.player_id
        )
        .filter(
            PlayerProjectionDB.game_id == game_id, PlayerProjectionDB.team_id == team_id
        )
        .all()
    )

    if response:
        return [
            PlayerProjectionResponse(
                name=player.name,
                number=player.number,
                is_home_team=player_projection.is_home_team,
                ppg=player_projection.ppg,
                rpg=player_projection.rpg,
                apg=player_projection.apg,
                fg_pct=player_projection.fg_pct,
                fg3_pct=player_projection.fg3_pct,
                role=player_projection.role,
                strengths=player.strengths,
                weaknesses=player.weaknesses,
                actual_ppg=player_stats.ppg if player_stats else None,
                actual_rpg=player_stats.rpg if player_stats else None,
                actual_apg=player_stats.apg if player_stats else None,
                actual_fg_pct=player_stats.fg_pct if player_stats else None,
                actual_fg3_pct=player_stats.fg3_pct if player_stats else None,
                actual_ft_pct=player_stats.ft_pct if player_stats else None,
                actual_spg=player_stats.spg if player_stats else None,
                actual_bpg=player_stats.bpg if player_stats else None,
                actual_topg=player_stats.topg if player_stats else None,
                actual_minutes=player_stats.minutes if player_stats else None,
            )
            for (player_projection, player, player_stats) in response
        ]
    return None


class ReportSummary(BaseModel):
    game_uuid: str
    home_team_id: int
    away_team_id: int
    home_team: str
    away_team: str
    created_at: datetime.datetime


def get_report_summaries_by_user_id(db: Session, user_id: int) -> List[ReportSummary]:
    """
    Get report summaries for a user

    Args:
        db: SQLAlchemy database session
        user_id: User ID to get report summaries for

    Returns:
        List of ReportSummary objects containing report metadata
    """
    HomeTeam = aliased(TeamDB)
    AwayTeam = aliased(TeamDB)
    
    response: List[Tuple[ReportDB, GameDB, TeamDB, TeamDB]] = (
        db.query(ReportDB, GameDB, HomeTeam, AwayTeam)
        .join(GameDB, ReportDB.game_id == GameDB.id)
        .join(HomeTeam, GameDB.home_team_id == HomeTeam.id)
        .join(AwayTeam, GameDB.away_team_id == AwayTeam.id)
        .filter(GameDB.user_id == user_id, ReportDB.report_type == "game_analysis")
        .order_by(ReportDB.created_at.desc())
        .all()
    )

    return [
        ReportSummary(
            game_uuid=str(game.uuid),
            home_team_id=game.home_team_id,
            away_team_id=game.away_team_id,
            home_team=home_team.name,
            away_team=away_team.name,
            created_at=report.created_at,
        )
        for (report, game, home_team, away_team) in response
    ]
