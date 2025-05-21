from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# Team Analysis
class PlayerStats(BaseModel):
    GP: int
    PPG: float
    FG_percent: str
    FG3_percent: str
    FT_percent: str
    RPG: float
    APG: float
    SPG: float
    BPG: float
    TOPG: float
    MINS: float
    FGM: int
    FGA: int
    FGM2: int
    FGA2: int
    FGM3: int
    FGA3: int
    FTM: int
    FTA: int
    AST: int
    TO: int
    STL: int
    BLK: int
    REB: int
    OREB: int
    DREB: int

class Player(BaseModel):
    name: str
    number: str
    position: str
    height: Optional[str] = None
    weight: Optional[str] = None
    year: Optional[str] = None
    stats: PlayerStats
    strengths: List[str]
    weaknesses: List[str]

class TeamStats(BaseModel):
    PPG: float
    FG_percent: str
    FG2_percent: str
    FG3_percent: str
    FT_percent: str
    REB: float
    OREB: float
    DREB: float
    AST: float
    STL: float
    BLK: float
    TO: float
    A_TO: float
    FGM: int
    FGA: int
    FGM2: int
    FGA2: int
    FGM3: int
    FGA3: int
    FTM: int
    FTA: int

class TeamDetails(BaseModel):
    team_name: str
    record: str = Field(description="The record of the team (e.g. 5-2)")
    record_date: str
    team_ranking: str
    players: List[Player]

class TeamAnalysis(BaseModel):
    playing_style: str
    team_strengths: List[str]
    team_weaknesses: List[str]
    key_players: List[str]
    offensive_keys: List[str]
    defensive_keys: List[str]
    game_factors: List[str]
    rotation_plan: str
    situational_adjustments: List[str]
    game_keys: List[str]

class TeamWrapper(BaseModel):
    team_analysis: TeamAnalysis
    team_details: TeamDetails
    team_stats: TeamStats

# Game Simulation
class SituationalAdjustment(BaseModel):
    scenario: str
    adjustment: str
    outcome: str
    
class PlaybookPlay(BaseModel):
    play_name: str
    purpose: str
    execution: str
    counter: str

class GameSimulation(BaseModel):
    win_probability: str = Field(description="The win probability for each team based on simulations (e.g., 'Team A has a 65% win probability')")
    projected_score: str = Field(description="The average projected score (e.g., 'Team A 78 - 72 Team B')")
    sim_overall_summary: str = Field(description="A 1-2 sentence summary of the simulation results, including the number of wins for each team and the average score")
    sim_success_factors: str = Field(description="A bullet list of 3-5 key factors that contributed to each team's success in the simulations")
    sim_key_matchups: str = Field(description="A bullet list of 3-5 critical player-vs-player or positional matchups that significantly impacted the game outcomes")
    sim_win_loss_patterns: str = Field(description="A bullet list of 3-5 key patterns observed in the wins and losses")
    sim_critical_advantage: str = Field(description="The most significant advantage that could determine the game outcome")
    sim_keys_to_victory: List[str] = Field(description="List of 4-6 key factors that will lead to victory")
        
    sim_situational_adjustments: List[SituationalAdjustment] = Field(description="Situational adjustments for the game")
    playbook_offensive_plays: List[PlaybookPlay] = Field(description="Offensive plays for the game")
    playbook_defensive_plays: List[PlaybookPlay] = Field(description="Defensive plays for the game")
    playbook_special_situations: List[PlaybookPlay] = Field(description="Special situations for the game")
    playbook_inbound_plays: List[PlaybookPlay] = Field(description="Inbound plays for the game")
    playbook_after_timeout_special_plays: List[PlaybookPlay] = Field(description="After Timeout / Special Scoring Plays")

    team_p1_name: str = Field(description="Name of team's player 1")
    team_p1_ppg: float = Field(description="Projected points per game for team's player 1")
    team_p1_rpg: float = Field(description="Projected rebounds per game for team's player 1")
    team_p1_apg: float = Field(description="Projected assists per game for team's player 1")
    team_p1_fg: str = Field(description="Projected field goal percentage for team's player 1")
    team_p1_3p: str = Field(description="Projected three-point percentage for team's player 1")
    team_p1_role: str = Field(description="Role description for team's player 1 in the game")

    team_p2_name: str = Field(description="Name of team's player 2")
    team_p2_ppg: float = Field(description="Projected points per game for team's player 2")
    team_p2_rpg: float = Field(description="Projected rebounds per game for team's player 2")
    team_p2_apg: float = Field(description="Projected assists per game for team's player 2")
    team_p2_fg: str = Field(description="Projected field goal percentage for team's player 2")
    team_p2_3p: str = Field(description="Projected three-point percentage for team's player 2")
    team_p2_role: str = Field(description="Role description for team's player 2 in the game")

    team_p3_name: str = Field(description="Name of team's player 3")
    team_p3_ppg: float = Field(description="Projected points per game for team's player 3")
    team_p3_rpg: float = Field(description="Projected rebounds per game for team's player 3")
    team_p3_apg: float = Field(description="Projected assists per game for team's player 3")
    team_p3_fg: str = Field(description="Projected field goal percentage for team's player 3")
    team_p3_3p: str = Field(description="Projected three-point percentage for team's player 3")
    team_p3_role: str = Field(description="Role description for team's player 3 in the game")

    team_p4_name: str = Field(description="Name of team's player 4")
    team_p4_ppg: float = Field(description="Projected points per game for team's player 4")
    team_p4_rpg: float = Field(description="Projected rebounds per game for team's player 4")
    team_p4_apg: float = Field(description="Projected assists per game for team's player 4")
    team_p4_fg: str = Field(description="Projected field goal percentage for team's player 4")
    team_p4_3p: str = Field(description="Projected three-point percentage for team's player 4")
    team_p4_role: str = Field(description="Role description for team's player 4 in the game")

    team_p5_name: str = Field(description="Name of team's player 5")
    team_p5_ppg: float = Field(description="Projected points per game for team's player 5")
    team_p5_rpg: float = Field(description="Projected rebounds per game for team's player 5")
    team_p5_apg: float = Field(description="Projected assists per game for team's player 5")
    team_p5_fg: str = Field(description="Projected field goal percentage for team's player 5")
    team_p5_3p: str = Field(description="Projected three-point percentage for team's player 5")
    team_p5_role: str = Field(description="Role description for team's player 5 in the game")

    team_p6_name: str = Field(description="Name of team's player 6")
    team_p6_ppg: float = Field(description="Projected points per game for team's player 6")
    team_p6_rpg: float = Field(description="Projected rebounds per game for team's player 6")
    team_p6_apg: float = Field(description="Projected assists per game for team's player 6")
    team_p6_fg: str = Field(description="Projected field goal percentage for team's player 6")
    team_p6_3p: str = Field(description="Projected three-point percentage for team's player 6")
    team_p6_role: str = Field(description="Role description for team's player 6 in the game")

    opp_p1_name: str = Field(description="Name of opponent's player 1")
    opp_p1_ppg: float = Field(description="Projected points per game for opponent's player 1")
    opp_p1_rpg: float = Field(description="Projected rebounds per game for opponent's player 1")
    opp_p1_apg: float = Field(description="Projected assists per game for opponent's player 1")
    opp_p1_fg: str = Field(description="Projected field goal percentage for opponent's player 1")
    opp_p1_3p: str = Field(description="Projected three-point percentage for opponent's player 1")
    opp_p1_role: str = Field(description="Role description for opponent's player 1 in the game")

    opp_p2_name: str = Field(description="Name of opponent's player 2")
    opp_p2_ppg: float = Field(description="Projected points per game for opponent's player 2")
    opp_p2_rpg: float = Field(description="Projected rebounds per game for opponent's player 2")
    opp_p2_apg: float = Field(description="Projected assists per game for opponent's player 2")
    opp_p2_fg: str = Field(description="Projected field goal percentage for opponent's player 2")
    opp_p2_3p: str = Field(description="Projected three-point percentage for opponent's player 2")
    opp_p2_role: str = Field(description="Role description for opponent's player 2 in the game")

    opp_p3_name: str = Field(description="Name of opponent's player 3")
    opp_p3_ppg: float = Field(description="Projected points per game for opponent's player 3")
    opp_p3_rpg: float = Field(description="Projected rebounds per game for opponent's player 3")
    opp_p3_apg: float = Field(description="Projected assists per game for opponent's player 3")
    opp_p3_fg: str = Field(description="Projected field goal percentage for opponent's player 3")
    opp_p3_3p: str = Field(description="Projected three-point percentage for opponent's player 3")
    opp_p3_role: str = Field(description="Role description for opponent's player 3 in the game")

    opp_p4_name: str = Field(description="Name of opponent's player 4")
    opp_p4_ppg: float = Field(description="Projected points per game for opponent's player 4")
    opp_p4_rpg: float = Field(description="Projected rebounds per game for opponent's player 4")
    opp_p4_apg: float = Field(description="Projected assists per game for opponent's player 4")
    opp_p4_fg: str = Field(description="Projected field goal percentage for opponent's player 4")
    opp_p4_3p: str = Field(description="Projected three-point percentage for opponent's player 4")
    opp_p4_role: str = Field(description="Role description for opponent's player 4 in the game")

    opp_p5_name: str = Field(description="Name of opponent's player 5")
    opp_p5_ppg: float = Field(description="Projected points per game for opponent's player 5")
    opp_p5_rpg: float = Field(description="Projected rebounds per game for opponent's player 5")
    opp_p5_apg: float = Field(description="Projected assists per game for opponent's player 5")
    opp_p5_fg: str = Field(description="Projected field goal percentage for opponent's player 5")
    opp_p5_3p: str = Field(description="Projected three-point percentage for opponent's player 5")
    opp_p5_role: str = Field(description="Role description for opponent's player 5 in the game")

    opp_p6_name: str = Field(description="Name of opponent's player 6")
    opp_p6_ppg: float = Field(description="Projected points per game for opponent's player 6")
    opp_p6_rpg: float = Field(description="Projected rebounds per game for opponent's player 6")
    opp_p6_apg: float = Field(description="Projected assists per game for opponent's player 6")
    opp_p6_fg: str = Field(description="Projected field goal percentage for opponent's player 6")
    opp_p6_3p: str = Field(description="Projected three-point percentage for opponent's player 6")
    opp_p6_role: str = Field(description="Role description for opponent's player 6 in the game")
