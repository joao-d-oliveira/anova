from typing import List, Optional
from pydantic import BaseModel

from app.llmmodels import PlaybookPlay, SituationalAdjustment

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

class TeamResponse(BaseModel):
    name: str
    record: str
    ranking: str

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
    

class PlayerProjectionResponse(BaseModel):
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
    actual_ppg: float
    actual_rpg: float
    actual_apg: float
    actual_fg_pct: str
    actual_fg3_pct: str
    actual_ft_pct: str
    actual_spg: float
    actual_bpg: float
    actual_topg: float
    actual_minutes: float
