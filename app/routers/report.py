import datetime
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.config import Config
from app.database.connection import GameSimulation, ProjectedPlayer, Team, TeamStats, get_game_by_uuid, get_game_simulation, get_projected_player_for_game, get_team_by_id, get_team_stats_from_game


config = Config()

router = APIRouter(
    prefix="/report",
    tags=["report"],
    responses={404: {"description": "Not found"}},
)


# class PlayerStats(BaseModel):
#     GP: int
#     PPG: float
#     FG_percent: str = Field(alias="FG%")
#     three_FG_percent: str = Field(alias="3FG%")
#     FT_percent: str = Field(alias="FT%")
#     RPG: float
#     APG: float
#     SPG: float
#     BPG: float
#     TOPG: float
#     MINS: float
#     FGM: int
#     FGA: int
#     two_FGM: int = Field(alias="2FGM")
#     two_FGA: int = Field(alias="2FGA")
#     three_FGM: int = Field(alias="3FGM")
#     three_FGA: int = Field(alias="3FGA")
#     FTM: int
#     FTA: int
#     AST: int
#     TO: int
#     STL: int
#     BLK: int
#     REB: int
#     OREB: int
#     DREB: int


# class Player(BaseModel):
#     name: str
#     number: str
#     position: str
#     stats: PlayerStats
#     strengths: List[str]
#     weaknesses: List[str]


# class TeamStats(BaseModel):
#     PPG: float
#     FG_percent: str = Field(alias="FG%")
#     three_FG_percent: str = Field(alias="3FG%")
#     FT_percent: str = Field(alias="FT%")
#     REB: float
#     OREB: float
#     DREB: float
#     AST: float
#     STL: float
#     BLK: float
#     TO: float
#     A_TO: float = Field(alias="A/TO")
#     two_FG_percent: str = Field(alias="2FG%")


# class TeamAnalysis(BaseModel):
#     team_name: str
#     record_date: str
#     team_ranking: str
#     team_stats: TeamStats
#     players: List[Player]
#     team_strengths: List[str]
#     team_weaknesses: List[str]
#     key_players: List[str]
#     playing_style: str
#     offensive_keys: List[str]
#     defensive_keys: List[str]
#     game_factors: List[str]
#     rotation_plan: str
#     situational_adjustments: List[str]
#     game_keys: List[str]


class OverallReport(BaseModel):
    created_at: datetime.datetime
    
    game_uuid: str    
    game_simulation: GameSimulation
    
    team: Team
    team_stats: TeamStats
    team_player_analysis: List[ProjectedPlayer]
    opponent: Team
    opponent_stats: TeamStats
    opponent_player_analysis: List[ProjectedPlayer]


@router.get("/{game_uuid}", response_model=OverallReport)
async def get_full_game_report(game_uuid: str):
    # get game
    game = get_game_by_uuid(game_uuid)
    
    # get game report
    game_report = get_game_simulation(game.id)

    # get team analysis
    team = get_team_by_id(game.home_team_id)
    team_analysis = get_team_stats_from_game(game.id)
    team_player_analysis = get_projected_player_for_game(game.id, team.id)
    
    # get opponent analysis
    opponent = get_team_by_id(game.away_team_id)
    opponent_analysis = get_team_stats_from_game(game.id)
    opponent_player_analysis = get_projected_player_for_game(game.id, opponent.id)

    return OverallReport(
        game_uuid=game.uuid,
        created_at=game.created_at,
        game_simulation=game_report,

        team=team,
        team_stats=team_analysis,
        team_player_analysis=team_player_analysis,

        opponent=opponent,
        opponent_stats=opponent_analysis,
        opponent_player_analysis=opponent_player_analysis
    )
