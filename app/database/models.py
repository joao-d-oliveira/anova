import datetime
from typing import Any, List, override
from pydantic import BaseModel, TypeAdapter
from sqlalchemy import Column, Dialect, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Date, ARRAY, Text, JSON, TypeDecorator, text, DateTime as SQLDateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
import uuid

from app.llmmodels import PlaybookPlay, SituationalAdjustment


SERVER_TS = text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')")


class PydanticType(TypeDecorator):
    """Pydantic type.
    SAVING:
    - Uses SQLAlchemy JSON type under the hood.
    - Acceps the pydantic model and converts it to a dict on save.
    - SQLAlchemy engine JSON-encodes the dict to a string.
    RETRIEVING:
    - Pulls the string from the database.
    - SQLAlchemy engine JSON-decodes the string to a dict.
    - Uses the dict to create a pydantic model.
    """
    
    # If you work with PostgreSQL, you can consider using
    # sqlalchemy.dialects.postgresql.JSONB instead of a
    # generic sa.types.JSON
    #
    # Ref: https://www.postgresql.org/docs/13/datatype-json.html
    impl = JSONB

    def __init__(self, pydantic_type, is_list=False):
        super().__init__()
        self.pydantic_type = pydantic_type
        self.is_list = is_list
        
    def load_dialect_impl(self, dialect):
        # Use JSONB for PostgreSQL and JSON for other databases.
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())

    @override
    def process_bind_param(
        self,
        value: BaseModel | None,
        dialect: Dialect,
    ) -> dict[str, Any] | None:
        if value is None:
            return None

        if self.is_list:
            return [v.model_dump(mode="json", exclude_unset=True) for v in value]

        if not isinstance(value, BaseModel):
            raise TypeError(f'Value "{value!r}" is not a pydantic model.') 

        return value.model_dump(mode="json", exclude_unset=True)

    @override
    def process_result_value(
        self,
        value: list[dict] | dict[str, Any] | None, 
        dialect: Dialect,
    ) -> BaseModel | None:
        if value is None:
            return None

        if self.is_list:
            return [self.pydantic_type(**v) for v in value]

        return self.pydantic_type(**value) if value else None


# pylint: disable=too-many-ancestors
class UTCDateTime(TypeDecorator):
    """Automatically convert datetime objects to UTC for storage and retrieve them in UTC"""
    impl = SQLDateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if value.tzinfo is None:
                value = value.replace(tzinfo=datetime.timezone.utc)
            return value.astimezone(datetime.timezone.utc)
        return value

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=datetime.timezone.utc)
        return value

    def process_literal_param(self, value, dialect):
        """Process literal parameters (required by TypeDecorator)"""
        return str(value)

    @property
    def python_type(self):
        """Return the Python type object expected for this type (required by TypeEngine)"""
        return datetime.datetime

Base = declarative_base()

class UserDB(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    phone_number = Column(String(20))
    school = Column(String(100))
    role = Column(String(50))
    password_hash = Column(String(255), nullable=False)
    confirmed = Column(Boolean, default=False)
    created_at = Column(UTCDateTime, server_default=SERVER_TS)
    updated_at = Column(UTCDateTime, server_default=SERVER_TS, server_onupdate=SERVER_TS)
    
    # Relationships
    games = relationship("GameDB", back_populates="user")
    otps = relationship("OneTimePasswordDB", back_populates="user")

class TeamDB(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    record = Column(String(20))
    ranking = Column(String(50))
    record_date = Column(Date)
    created_at = Column(UTCDateTime, server_default=SERVER_TS)
    updated_at = Column(UTCDateTime, server_default=SERVER_TS, server_onupdate=SERVER_TS)
    
    # Relationships
    players = relationship("PlayerDB", back_populates="team")
    coaches = relationship("CoachDB", back_populates="team")
    home_games = relationship("GameDB", foreign_keys="GameDB.home_team_id", back_populates="home_team")
    away_games = relationship("GameDB", foreign_keys="GameDB.away_team_id", back_populates="away_team")
    team_stats = relationship("TeamStatsDB", back_populates="team")
    team_analysis = relationship("TeamAnalysisDB", back_populates="team")

class PlayerDB(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'))
    name = Column(String(100), nullable=False)
    number = Column(String(10))
    position = Column(String(20))
    height = Column(String(10))
    weight = Column(String(10))
    year = Column(String(20))
    strengths = Column(ARRAY(Text))
    weaknesses = Column(ARRAY(Text))
    created_at = Column(UTCDateTime, server_default=SERVER_TS)
    updated_at = Column(UTCDateTime, server_default=SERVER_TS, server_onupdate=SERVER_TS)
    
    # Relationships
    team = relationship("TeamDB", back_populates="players")
    raw_stats = relationship("PlayerRawStatsDB", back_populates="player")
    player_stats = relationship("PlayerStatsDB", back_populates="player")
    player_projections = relationship("PlayerProjectionDB", back_populates="player")

class CoachDB(Base):
    __tablename__ = 'coaches'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'))
    name = Column(String(100), nullable=False)
    role = Column(String(50))
    created_at = Column(UTCDateTime, server_default=SERVER_TS)
    updated_at = Column(UTCDateTime, server_default=SERVER_TS, server_onupdate=SERVER_TS)
    
    # Relationships
    team = relationship("TeamDB", back_populates="coaches")

class GameDB(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID, unique=True, default=uuid.uuid4)
    home_team_id = Column(Integer, ForeignKey('teams.id'))
    away_team_id = Column(Integer, ForeignKey('teams.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    date = Column(Date)
    location = Column(String(100))
    home_score = Column(Integer)
    away_score = Column(Integer)
    status = Column(String(20))
    created_at = Column(UTCDateTime, server_default=SERVER_TS)
    updated_at = Column(UTCDateTime, server_default=SERVER_TS, server_onupdate=SERVER_TS)
    
    # Relationships
    home_team = relationship("TeamDB", foreign_keys=[home_team_id], back_populates="home_games")
    away_team = relationship("TeamDB", foreign_keys=[away_team_id], back_populates="away_games")
    user = relationship("UserDB", back_populates="games")
    player_raw_stats = relationship("PlayerRawStatsDB", back_populates="game")
    team_stats = relationship("TeamStatsDB", back_populates="game")
    player_stats = relationship("PlayerStatsDB", back_populates="game")
    game_simulation = relationship("GameSimulationDB", back_populates="game", uselist=False)
    reports = relationship("ReportDB", back_populates="game")

class PlayerRawStatsDB(Base):
    __tablename__ = 'player_raw_stats'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'))
    game_id = Column(Integer, ForeignKey('games.id'))
    fgm = Column(Integer)
    fga = Column(Integer)
    fg2m = Column(Integer)
    fg2a = Column(Integer)
    fg3m = Column(Integer)
    fg3a = Column(Integer)
    ftm = Column(Integer)
    fta = Column(Integer)
    total_rebounds = Column(Integer)
    offensive_rebounds = Column(Integer)
    defensive_rebounds = Column(Integer)
    total_assists = Column(Integer)
    total_steals = Column(Integer)
    total_blocks = Column(Integer)
    total_turnovers = Column(Integer)
    created_at = Column(UTCDateTime, server_default=SERVER_TS)
    updated_at = Column(UTCDateTime, server_default=SERVER_TS, server_onupdate=SERVER_TS)
    
    # Relationships
    player = relationship("PlayerDB", back_populates="raw_stats")
    game = relationship("GameDB", back_populates="player_raw_stats")
    player_stats = relationship("PlayerStatsDB", back_populates="player_raw_stats")

class TeamStatsDB(Base):
    __tablename__ = 'team_stats'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'))
    game_id = Column(Integer, ForeignKey('games.id'))
    ppg = Column(Numeric(5, 1))
    fg_pct = Column(String(10))
    fg_made = Column(Numeric)
    fg_attempted = Column(Numeric)
    fg3_pct = Column(String(10))
    fg3_made = Column(Numeric)
    fg3_attempted = Column(Numeric)
    ft_pct = Column(String(10))
    ft_made = Column(Numeric)
    ft_attempted = Column(Numeric)
    rebounds = Column(Numeric(5, 1))
    offensive_rebounds = Column(Numeric(5, 1))
    defensive_rebounds = Column(Numeric(5, 1))
    assists = Column(Numeric(5, 1))
    steals = Column(Numeric(5, 1))
    blocks = Column(Numeric(5, 1))
    turnovers = Column(Numeric(5, 1))
    assist_to_turnover = Column(Numeric(5, 2))
    is_season_average = Column(Boolean)
    created_at = Column(UTCDateTime, server_default=SERVER_TS)
    updated_at = Column(UTCDateTime, server_default=SERVER_TS, server_onupdate=SERVER_TS)
    
    # Relationships
    team = relationship("TeamDB", back_populates="team_stats")
    game = relationship("GameDB", back_populates="team_stats")

class PlayerStatsDB(Base):
    __tablename__ = 'player_stats'
    
    id = Column(Integer, primary_key=True)
    player_raw_stats_id = Column(Integer, ForeignKey('player_raw_stats.id'))
    player_id = Column(Integer, ForeignKey('players.id'))
    game_id = Column(Integer, ForeignKey('games.id'))
    games_played = Column(Integer)
    ppg = Column(Numeric(5, 1))
    fg_pct = Column(String(10))
    fg3_pct = Column(String(10))
    ft_pct = Column(String(10))
    rpg = Column(Numeric(5, 1))
    apg = Column(Numeric(5, 1))
    spg = Column(Numeric(5, 1))
    bpg = Column(Numeric(5, 1))
    topg = Column(Numeric(5, 1))
    minutes = Column(Numeric(5, 1))
    is_season_average = Column(Boolean)
    created_at = Column(UTCDateTime, server_default=SERVER_TS)
    updated_at = Column(UTCDateTime, server_default=SERVER_TS, server_onupdate=SERVER_TS)
    
    # Relationships
    player_raw_stats = relationship("PlayerRawStatsDB", back_populates="player_stats")
    player = relationship("PlayerDB", back_populates="player_stats")
    game = relationship("GameDB", back_populates="player_stats")

class TeamAnalysisDB(Base):
    __tablename__ = 'team_analysis'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'))
    strengths = Column(ARRAY(Text))
    weaknesses = Column(ARRAY(Text))
    key_players = Column(ARRAY(Text))
    offensive_keys = Column(ARRAY(Text))
    defensive_keys = Column(ARRAY(Text))
    game_factors = Column(ARRAY(Text))
    rotation_plan = Column(ARRAY(Text))
    situational_adjustments = Column(ARRAY(Text))
    game_keys = Column(ARRAY(Text))
    playing_style = Column(Text)
    created_at = Column(UTCDateTime, server_default=SERVER_TS)
    updated_at = Column(UTCDateTime, server_default=SERVER_TS, server_onupdate=SERVER_TS)
    
    # Relationships
    team = relationship("TeamDB", back_populates="team_analysis")

class GameSimulationDB(Base):
    __tablename__ = 'game_simulations'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    win_probability = Column(String(100))
    projected_score = Column(String(100))
    sim_overall_summary = Column(Text)
    sim_success_factors = Column(Text)
    sim_key_matchups = Column(Text)
    sim_win_loss_patterns = Column(Text)
    sim_critical_advantage = Column(Text)
    sim_keys_to_victory = Column(ARRAY(Text))
    sim_situational_adjustments: list[SituationalAdjustment] = Column(PydanticType(SituationalAdjustment, is_list=True))
    playbook_offensive_plays: list[PlaybookPlay] = Column(PydanticType(PlaybookPlay, is_list=True))
    playbook_defensive_plays: list[PlaybookPlay] = Column(PydanticType(PlaybookPlay, is_list=True))
    playbook_special_situations: list[PlaybookPlay] = Column(PydanticType(PlaybookPlay, is_list=True))
    playbook_inbound_plays: list[PlaybookPlay] = Column(PydanticType(PlaybookPlay, is_list=True))
    playbook_after_timeout_special_plays: list[PlaybookPlay] = Column(PydanticType(PlaybookPlay, is_list=True))
    created_at = Column(UTCDateTime, server_default=SERVER_TS)
    updated_at = Column(UTCDateTime, server_default=SERVER_TS, server_onupdate=SERVER_TS)
    
    # Relationships
    game = relationship("GameDB", back_populates="game_simulation")
    player_projections = relationship("PlayerProjectionDB", back_populates="game_simulation")
    simulation_details = relationship("SimulationDetailsDB", back_populates="game_simulation")

class PlayerProjectionDB(Base):
    __tablename__ = 'player_projections'
    
    id = Column(Integer, primary_key=True)
    game_simulation_id = Column(Integer, ForeignKey('game_simulations.id'))
    player_id = Column(Integer, ForeignKey('players.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    game_id = Column(Integer, ForeignKey('games.id'))
    is_home_team = Column(Boolean)
    ppg = Column(Numeric(5, 1))
    rpg = Column(Numeric(5, 1))
    apg = Column(Numeric(5, 1))
    fg_pct = Column(String(10))
    fg3_pct = Column(String(10))
    role = Column(String(100))
    created_at = Column(UTCDateTime, server_default=SERVER_TS)
    updated_at = Column(UTCDateTime, server_default=SERVER_TS, server_onupdate=SERVER_TS)
    
    # Relationships
    game_simulation = relationship("GameSimulationDB", back_populates="player_projections")
    player = relationship("PlayerDB", back_populates="player_projections")

class SimulationDetailsDB(Base):
    __tablename__ = 'simulation_details'
    
    id = Column(Integer, primary_key=True)
    game_simulation_id = Column(Integer, ForeignKey('game_simulations.id'))
    game_id = Column(Integer, ForeignKey('games.id'))
    home_team_id = Column(Integer, ForeignKey('teams.id'))
    away_team_id = Column(Integer, ForeignKey('teams.id'))
    num_simulations = Column(Integer)
    home_team_wins = Column(Integer)
    away_team_wins = Column(Integer)
    home_team_win_pct = Column(Numeric(5, 1))
    away_team_win_pct = Column(Numeric(5, 1))
    avg_home_score = Column(Numeric(5, 1))
    avg_away_score = Column(Numeric(5, 1))
    closest_game_margin = Column(Integer)
    blowout_game_margin = Column(Integer)
    margin_distribution = Column(JSONB)
    avg_effects = Column(JSONB)
    created_at = Column(UTCDateTime, server_default=SERVER_TS)
    updated_at = Column(UTCDateTime, server_default=SERVER_TS, server_onupdate=SERVER_TS)
    
    # Relationships
    game_simulation = relationship("GameSimulationDB", back_populates="simulation_details")

class ReportDB(Base):
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID, unique=True, default=uuid.uuid4)
    game_id = Column(Integer, ForeignKey('games.id'))
    report_type = Column(String(50))
    file_path = Column(String(255))
    created_at = Column(UTCDateTime, server_default=SERVER_TS)
    updated_at = Column(UTCDateTime, server_default=SERVER_TS, server_onupdate=SERVER_TS)
    
    # Relationships
    game = relationship("GameDB", back_populates="reports")

class OneTimePasswordDB(Base):
    __tablename__ = 'one_time_passwords'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    otp = Column(String(10), unique=True, nullable=False)
    created_at = Column(UTCDateTime, server_default=SERVER_TS)
    
    # Relationships
    user = relationship("UserDB", back_populates="otps")
