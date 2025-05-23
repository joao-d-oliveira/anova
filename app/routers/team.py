import datetime
import uuid
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.config import Config
from app.database.common import get_db
from app.database.models import GameDB, TeamAnalysisDB, TeamDB, TeamStatsDB, UserDB
from app.routers.util import get_verified_user_email


config = Config()

router = APIRouter(
    prefix="/team",
    tags=["team"],
    responses={404: {"description": "Not found"}},
)

class LatestTeamAnalysis(BaseModel):
    analysis_date: datetime.datetime
    team_name: str
    team_uuid: str

@router.get("/latest-home-team-analysis", response_model=LatestTeamAnalysis)
def get_latest_home_team_analysis(user_email: str = Depends(get_verified_user_email), db: Session = Depends(get_db)):
    # We're doing the join just to make sure we have a full analysis for the team
    result = db.query(GameDB, TeamDB, TeamAnalysisDB).join(TeamDB, GameDB.home_team_id == TeamDB.id).join(TeamAnalysisDB).join(UserDB).where(UserDB.email == user_email).order_by(GameDB.id.desc()).limit(1).first()
    if result is None:
        return None
    
    _, team, analysis = result
    return LatestTeamAnalysis(
        analysis_date=analysis.created_at,
        team_name=team.name,
        team_uuid=str(team.uuid)
    )