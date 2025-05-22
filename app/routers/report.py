import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.config import Config
from app.database.connection import GameSimulationResponse, ProjectedPlayer, ReportSummary, TeamAnalysisResponse, TeamResponse, TeamStatsResponse, get_game_by_uuid, get_game_simulation, get_projected_player_for_game, get_report_by_game_id, get_report_summaries_by_user_id, get_team_analysis_by_team_id, get_team_by_id, get_team_stats_from_game, get_user_by_email
from app.models import TeamAnalysis
from app.routers.util import get_verified_user_email


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
    game_simulation: GameSimulationResponse
    
    team: TeamResponse
    team_stats: TeamStatsResponse
    team_analysis: TeamAnalysisResponse
    team_player_analysis: List[ProjectedPlayer]

    opponent: TeamResponse
    opponent_stats: TeamStatsResponse
    opponent_analysis: TeamAnalysisResponse
    opponent_player_analysis: List[ProjectedPlayer]




@router.get("/summaries", response_model=List[ReportSummary])
async def get_report_summaries(user_email: str = Depends(get_verified_user_email)):
    # Get user ID from email
    user = get_user_by_email(user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get report summaries
    summaries = get_report_summaries_by_user_id(user["id"])
    
    return summaries

@router.get("/{game_uuid}", response_model=OverallReport)
async def get_full_game_report(game_uuid: str, user_email: str = Depends(get_verified_user_email)):
    # get game
    user = get_user_by_email(user_email)
    game = get_game_by_uuid(game_uuid)
    if not game or game.user_id != user["id"]:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # get game report
    game_report = get_game_simulation(game.id)

    # get team analysis
    team = get_team_by_id(game.home_team_id)
    team_stats = get_team_stats_from_game(game.id, team.id)
    team_analysis = get_team_analysis_by_team_id(team.id)
    team_player_analysis = get_projected_player_for_game(game.id, team.id)
    
    # get opponent analysis
    opponent = get_team_by_id(game.away_team_id)
    opponent_stats = get_team_stats_from_game(game.id, opponent.id)
    opponent_analysis = get_team_analysis_by_team_id(opponent.id)
    opponent_player_analysis = get_projected_player_for_game(game.id, opponent.id)

    return OverallReport(
        game_uuid=game.uuid,
        created_at=game.created_at,
        game_simulation=game_report,

        team=team,
        team_stats=team_stats,
        team_player_analysis=team_player_analysis,
        team_analysis=team_analysis,

        opponent=opponent,
        opponent_stats=opponent_stats,
        opponent_player_analysis=opponent_player_analysis,
        opponent_analysis=opponent_analysis
    )

@router.get("/{game_uuid}/download")
async def download_game_report(game_uuid: str, user_email: str = Depends(get_verified_user_email)):
    game = get_game_by_uuid(game_uuid)
    if not game or game.user_id != user_email:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_report = get_report_by_game_id(game.id, "game_analysis")

    return FileResponse(game_report["file_path"], media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
