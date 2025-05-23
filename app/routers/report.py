import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.config import Config
from app.database.common import get_db
from app.database.connection import ReportSummary, get_game_by_uuid, get_game_simulation, get_projected_player_for_game, get_report_by_game_id, get_report_summaries_by_user_id, get_team_analysis_by_team_id, get_team_by_id, get_team_stats_from_game, get_user_by_email
from app.models import GameSimulationResponse, PlayerProjectionResponse, TeamResponse, TeamStatsResponse, TeamAnalysisResponse
from app.routers.util import get_verified_user_email


config = Config()

router = APIRouter(
    prefix="/report",
    tags=["report"],
    responses={404: {"description": "Not found"}},
)

class OverallReport(BaseModel):
    created_at: datetime.datetime
    
    game_uuid: str    
    game_simulation: GameSimulationResponse
    
    team: TeamResponse
    team_stats: TeamStatsResponse
    team_analysis: TeamAnalysisResponse
    team_player_analysis: List[PlayerProjectionResponse]

    opponent: TeamResponse
    opponent_stats: TeamStatsResponse
    opponent_analysis: TeamAnalysisResponse
    opponent_player_analysis: List[PlayerProjectionResponse]


@router.get("/summaries", response_model=List[ReportSummary])
async def get_report_summaries(user_email: str = Depends(get_verified_user_email), db: Session = Depends(get_db)):
    # Get user ID from email
    user = get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get report summaries
    summaries = get_report_summaries_by_user_id(db, user.id)
    
    return summaries

@router.get("/{game_uuid}", response_model=OverallReport)
async def get_full_game_report(game_uuid: str, user_email: str = Depends(get_verified_user_email), db: Session = Depends(get_db)):
    # get game
    user = get_user_by_email(db, user_email)
    game = get_game_by_uuid(db, game_uuid)
    if not game or game.user_id != user.id:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # get game report
    game_simulation_db = get_game_simulation(db, game.id)
    game_simulation = GameSimulationResponse(**game_simulation_db.__dict__)

    # get team analysis
    team_db = get_team_by_id(db, game.home_team_id)
    team = TeamResponse.model_validate(team_db.__dict__)
    team_stats = TeamStatsResponse.model_validate(get_team_stats_from_game(db, game.id, team_db.id).__dict__)
    team_analysis = TeamAnalysisResponse.model_validate(get_team_analysis_by_team_id(db, team_db.id).__dict__)
    team_player_analysis = [PlayerProjectionResponse.model_validate(player.__dict__) for player in get_projected_player_for_game(db, game.id, team_db.id)]
    
    # get opponent analysis
    opponent_db = get_team_by_id(db, game.away_team_id)
    opponent = TeamResponse.model_validate(opponent_db.__dict__)
    opponent_stats = TeamStatsResponse.model_validate(get_team_stats_from_game(db, game.id, opponent_db.id).__dict__)
    opponent_analysis = TeamAnalysisResponse.model_validate(get_team_analysis_by_team_id(db, opponent_db.id).__dict__)
    opponent_player_analysis = [PlayerProjectionResponse.model_validate(player.__dict__) for player in get_projected_player_for_game(db, game.id, opponent_db.id)]

    return OverallReport(
        game_uuid=str(game.uuid),
        created_at=game.created_at,
        game_simulation=game_simulation,

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
async def download_game_report(game_uuid: str, user_email: str = Depends(get_verified_user_email), db: Session = Depends(get_db)):
    game = get_game_by_uuid(db, game_uuid)
    if not game or game.user_id != user_email:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_report = get_report_by_game_id(db, game.id, "game_analysis")

    return FileResponse(game_report.file_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
