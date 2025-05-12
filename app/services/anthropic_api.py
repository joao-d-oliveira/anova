import os
import base64
import json
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPICS_API_KEY"))

def encode_pdf_to_base64(file_path: str) -> str:
    """
    Encode a PDF file to base64
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Base64 encoded string
    """
    with open(file_path, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read()).decode("utf-8")
    return encoded_string

def save_analysis_json(analysis: Dict[str, Any], team_name: str, is_our_team: bool) -> str:
    """
    Save team analysis to a JSON file
    
    Args:
        analysis: Dictionary containing team analysis
        team_name: Name of the team
        is_our_team: Whether this is our team or opponent
        
    Returns:
        Path to the saved JSON file
    """
    # Create directory if it doesn't exist
    json_dir = "app/data/analysis_json"
    os.makedirs(json_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    team_type = "team" if is_our_team else "opponent"
    filename = f"{team_name}_{team_type}_analysis_{timestamp}.json"
    file_path = os.path.join(json_dir, filename)
    
    # Save analysis to JSON file
    with open(file_path, "w") as f:
        json.dump(analysis, f, indent=2)
    
    return file_path

def analyze_team_pdf(file_path: str, is_our_team: bool, prompt_path: str=None ) -> Dict[str, Any]:
    """
    Analyze a team's PDF using Claude 3.7 Anthropic API
    
    Args:
        file_path: Path to the PDF file
        is_our_team: Whether this is our team (True) or opponent (False)
        
    Returns:
        Dictionary containing analysis results
    """
    # Load prompt template
    if prompt_path is None:
        prompt_path = os.path.join("app/prompts", "team_analysis_prompt.txt")
    with open(prompt_path, "r") as file:
        prompt_template = file.read()
    
    # Encode PDF to base64
    pdf_base64 = encode_pdf_to_base64(file_path)
    
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=8000,
        temperature=0.0,
        system=f"You are an expert basketball analyst. You are analyzing a PDF containing basketball statistics for a {'team' if is_our_team else 'opponent team'}.",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_base64}},
                    {"type": "text", "text": prompt_template}
                ]
            }
        ]
    )
    # Create message with PDF attachment

    # Extract and parse JSON from response
    try:
        # Look for JSON in the response
        response_text = message.content[0].text
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if 0 <= json_start < json_end:
            json_str = response_text[json_start:json_end]
            analysis = json.loads(json_str)
            
            # Post-process to ensure team stats are populated
            analysis = post_process_team_stats(analysis)
            team_name = analysis.get("team_name", "Unknown Team")
            save_analysis_json(analysis, team_name, is_our_team)
            
            return analysis
        else:
            # If no JSON found, return empty dict
            return {}
    except Exception as e:
        print(f"Error parsing JSON from Claude response: {e}")
        return {}

def post_process_team_stats(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post-process team statistics to ensure all fields are populated
    
    Args:
        analysis: Dictionary containing team analysis
        
    Returns:
        Dictionary with post-processed team statistics
    """
    # Check if team_stats exists
    if "team_stats" not in analysis:
        analysis["team_stats"] = {}
    
    # Get players data
    players = analysis.get("players", [])
    
    # Calculate missing team stats from player stats if needed
    if players:
        total_FGM = sum(player.get("stats", {}).get("FGM", 0) for player in players)
        total_FGA = sum(player.get("stats", {}).get("FGA", 0) for player in players)
        total_2FGM = sum(player.get("stats", {}).get("2FGM", 0) for player in players)
        total_2FGA = sum(player.get("stats", {}).get("2FGA", 0) for player in players)
        total_3FGM = sum(player.get("stats", {}).get("3FGM", 0) for player in players)
        total_3FGA = sum(player.get("stats", {}).get("3FGA", 0) for player in players)
        total_FTM = sum(player.get("stats", {}).get("FTM", 0) for player in players)
        total_FTA = sum(player.get("stats", {}).get("FTA", 0) for player in players)
        total_AST = sum(player.get("stats", {}).get("AST", 0) for player in players)
        total_TO = sum(player.get("stats", {}).get("TO", 0) for player in players)

        total_BLK = sum(player.get("stats", {}).get("BLK", 0) / player.get("stats", {}).get("GP", 1) for player in players)
        total_REB = sum(player.get("stats", {}).get("REB", 0) / player.get("stats", {}).get("GP", 1) for player in players)
        total_OREB = sum(player.get("stats", {}).get("OREB", 0) / player.get("stats", {}).get("GP", 1) for player in players)
        total_DREB = sum(player.get("stats", {}).get("DREB", 0) / player.get("stats", {}).get("GP", 1) for player in players)
        total_AST_G = sum(player.get("stats", {}).get("AST", 0) / player.get("stats", {}).get("GP", 1) for player in players)
        total_STL = sum(player.get("stats", {}).get("STL", 0) / player.get("stats", {}).get("GP", 1) for player in players)

        if total_FGA > 0 < total_FGM:
            analysis["team_stats"]["FG%"] = f"{round((total_FGM / total_FGA) * 100, 1)}%"
        if total_2FGA > 0 < total_2FGM:
            analysis["team_stats"]["2FG%"] = f"{round((total_2FGM / total_2FGA) * 100, 1)}%"
        if total_3FGA > 0 < total_3FGM:
            analysis["team_stats"]["3FG%"] = f"{round((total_3FGM / total_3FGA) * 100, 1)}%"
        if total_FTA > 0 < total_FTM:
            analysis["team_stats"]["FT%"] = f"{round((total_FTM / total_FTA) * 100, 1)}%"

        if total_AST > 0 < total_TO:
            analysis["team_stats"]["A/TO"] = round(total_AST / total_TO, 2)

        if total_BLK > 0:
            analysis["team_stats"]["BLK"] = round(total_BLK, 1)
        if total_REB > 0:
            analysis["team_stats"]["REB"] = round(total_REB, 1)
        if total_OREB > 0:
            analysis["team_stats"]["OREB"] = round(total_OREB, 1)
        if total_DREB > 0:
            analysis["team_stats"]["DREB"] = round(total_DREB, 1)
        if total_AST_G > 0:
            analysis["team_stats"]["AST"] = round(total_AST_G, 1)
        if total_STL > 0:
            analysis["team_stats"]["STL"] = round(total_STL, 1)

        # Calculate PPG if it's 0 or missing
        if analysis["team_stats"].get("PPG", 0) == 0:
            total_ppg = sum(player.get("stats", {}).get("PPG", 0) for player in players)
            # If we have player PPG, use it as an estimate
            if total_ppg > 0:
                analysis["team_stats"]["PPG"] = round(total_ppg, 1)
        
        # Calculate REB if it's 0 or missing
        if analysis["team_stats"].get("REB", 0) == 0:
            total_rpg = sum(player.get("stats", {}).get("RPG", 0) for player in players)
            if total_rpg > 0:
                analysis["team_stats"]["REB"] = round(total_rpg, 1)
        
        # Calculate AST if it's 0 or missing
        if analysis["team_stats"].get("AST", 0) == 0:
            total_apg = sum(player.get("stats", {}).get("APG", 0) for player in players)
            if total_apg > 0:
                analysis["team_stats"]["AST"] = round(total_apg, 1)
        
        # Calculate STL if it's 0 or missing
        if analysis["team_stats"].get("STL", 0) == 0:
            total_spg = sum(player.get("stats", {}).get("SPG", 0) for player in players)
            if total_spg > 0:
                analysis["team_stats"]["STL"] = round(total_spg, 1)
        
        # Calculate BLK if it's 0 or missing
        if analysis["team_stats"].get("BLK", 0) == 0:
            total_bpg = sum(player.get("stats", {}).get("BPG", 0) for player in players)
            if total_bpg > 0:
                analysis["team_stats"]["BLK"] = round(total_bpg, 1)
        
        # Calculate TO if it's 0 or missing
        if analysis["team_stats"].get("TO", 0) == 0:
            total_topg = sum(player.get("stats", {}).get("TOPG", 0) for player in players)
            if total_topg > 0:
                analysis["team_stats"]["TO"] = round(total_topg, 1)
        
        # Estimate OREB and DREB if REB is available but they're not
        if analysis["team_stats"].get("REB", 0) > 0:
            if analysis["team_stats"].get("OREB", 0) == 0 and analysis["team_stats"].get("DREB", 0) == 0:
                # Typical split is about 30% offensive, 70% defensive
                reb = analysis["team_stats"]["REB"]
                analysis["team_stats"]["OREB"] = round(reb * 0.3, 1)
                analysis["team_stats"]["DREB"] = round(reb * 0.7, 1)
    
    return analysis

def simulate_game_locally(team_analysis: Dict[str, Any], opponent_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate a game between two teams using local statistical calculations
    
    Args:
        team_analysis: Dictionary containing our team analysis
        opponent_analysis: Dictionary containing opponent team analysis
        
    Returns:
        Dictionary containing simulation results
    """
    # Extract team stats
    team_stats = team_analysis.get("team_stats", {})
    opponent_stats = opponent_analysis.get("team_stats", {})
    
    # Helper function to convert string or number to float
    def to_float(value: Any) -> float:
        if isinstance(value, str):
            # Remove % if present and convert to float
            return float(value.rstrip('%')) if '%' in value else float(value)
        return float(value) if value is not None else 0.0

    # Map stats to simulation variables
    teamA = {
        "name": team_analysis.get("team_name", "Team A"),
        "ppg": to_float(team_stats.get("PPG", 0)),
        "rpg": to_float(team_stats.get("REB", 0)),
        "fgPct": to_float(team_stats.get("FG%", 0)) / 100,
        "threePct": to_float(team_stats.get("3P%", 0)) / 100,
        "tpg": to_float(team_stats.get("TO", 0)),
        "apg": to_float(team_stats.get("AST", 0)),
        "spg": to_float(team_stats.get("STL", 0)),
        "bpg": to_float(team_stats.get("BLK", 0))
    }
    
    teamB = {
        "name": opponent_analysis.get("team_name", "Team B"),
        "ppg": to_float(opponent_stats.get("PPG", 0)),
        "rpg": to_float(opponent_stats.get("REB", 0)),
        "fgPct": to_float(opponent_stats.get("FG%", 0)) / 100,
        "threePct": to_float(opponent_stats.get("3P%", 0)) / 100,
        "tpg": to_float(opponent_stats.get("TO", 0)),
        "apg": to_float(opponent_stats.get("AST", 0)),
        "spg": to_float(opponent_stats.get("STL", 0)),
        "bpg": to_float(opponent_stats.get("BLK", 0))
    }
    
    # Run simulations
    return runSimulations(teamA, teamB, 100)

def simulateGame(teamA: Dict[str, Any], teamB: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate a single basketball game between two teams
    
    Args:
        teamA: First team's statistics
        teamB: Second team's statistics
        
    Returns:
        Dictionary containing game result with scores, winner, margin, and statistical effects
    """
    # Start with actual scoring averages
    teamAScore = teamA["ppg"]
    teamBScore = teamB["ppg"]

    # Calculate statistical advantages and their point impacts
    # Rebounding advantage (each extra rebound = 0.7 points)
    reboundDiff = teamA["rpg"] - teamB["rpg"]
    reboundEffect = reboundDiff * 0.7

    # Shooting efficiency advantages
    fgDiff = (teamA["fgPct"] - teamB["fgPct"]) * 100  # Convert to percentage points
    fgEffect = fgDiff * 0.25  # Each percentage point = 0.25 points

    threeDiff = (teamA["threePct"] - teamB["threePct"]) * 100
    threeEffect = threeDiff * 0.15  # Each percentage point = 0.15 points

    # Turnover differential (each fewer turnover = 1 point)
    turnoverDiff = teamB["tpg"] - teamA["tpg"]
    turnoverEffect = turnoverDiff * 1.0

    # Assist differential (each extra assist = 0.5 points)
    assistDiff = teamA["apg"] - teamB["apg"]
    assistEffect = assistDiff * 0.5

    # Defensive impact from steals and blocks
    stealsDiff = teamA["spg"] - teamB["spg"]
    stealsEffect = stealsDiff * 1.0

    blocksDiff = teamA["bpg"] - teamB["bpg"]
    blocksEffect = blocksDiff * 0.8

    # Calculate total statistical effect
    totalEffect = (reboundEffect + fgEffect + threeEffect + turnoverEffect +
                  assistEffect + stealsEffect + blocksEffect)

    # Apply the statistical advantage to Team A's score
    teamAScore += totalEffect

    # Add random game variance (±12%)
    gameVarianceA = 0.88 + (random.random() * 0.24)
    gameVarianceB = 0.88 + (random.random() * 0.24)

    teamAScore = teamAScore * gameVarianceA
    teamBScore = teamBScore * gameVarianceB

    # Round to integers for final scores
    finalTeamAScore = round(teamAScore)
    finalTeamBScore = round(teamBScore)

    # Return detailed game result
    return {
        "teamAScore": finalTeamAScore,
        "teamBScore": finalTeamBScore,
        "winner": teamA["name"] if finalTeamAScore > finalTeamBScore else teamB["name"],
        "margin": abs(finalTeamAScore - finalTeamBScore),
        "effects": {
            "rebounding": round(reboundEffect * 10) / 10,
            "fieldGoal": round(fgEffect * 10) / 10,
            "threePoint": round(threeEffect * 10) / 10,
            "turnovers": round(turnoverEffect * 10) / 10,
            "assists": round(assistEffect * 10) / 10,
            "steals": round(stealsEffect * 10) / 10,
            "blocks": round(blocksEffect * 10) / 10,
            "total": round(totalEffect * 10) / 10
        }
    }

def runSimulations(teamA: Dict[str, Any], teamB: Dict[str, Any], numSimulations: int = 100) -> Dict[str, Any]:
    """
    Run multiple simulations between two teams
    
    Args:
        teamA: First team's statistics
        teamB: Second team's statistics
        numSimulations: Number of simulations to run
        
    Returns:
        Dictionary containing aggregated simulation results
    """
    results = []
    teamAWins = 0
    teamBWins = 0
    totalPointsA = 0
    totalPointsB = 0
    closestGame = {"margin": float('inf')}
    blowoutGame = {"margin": 0}

    # Effects tracking
    effectTotals = {
        "rebounding": 0,
        "fieldGoal": 0,
        "threePoint": 0,
        "turnovers": 0,
        "assists": 0,
        "steals": 0,
        "blocks": 0,
        "total": 0
    }

    # Run the specified number of simulations
    for i in range(numSimulations):
        gameResult = simulateGame(teamA, teamB)
        results.append(gameResult)

        # Track wins
        if gameResult["winner"] == teamA["name"]:
            teamAWins += 1
        else:
            teamBWins += 1

        # Track points
        totalPointsA += gameResult["teamAScore"]
        totalPointsB += gameResult["teamBScore"]

        # Track closest game
        if gameResult["margin"] < closestGame["margin"]:
            closestGame = {**gameResult, "gameNumber": i + 1}

        # Track biggest blowout
        if gameResult["margin"] > blowoutGame["margin"]:
            blowoutGame = {**gameResult, "gameNumber": i + 1}

        # Track effect contributions
        for effect in gameResult["effects"]:
            effectTotals[effect] += gameResult["effects"][effect]

    # Calculate average scores
    avgScoreA = round(totalPointsA / numSimulations * 10) / 10
    avgScoreB = round(totalPointsB / numSimulations * 10) / 10

    # Calculate win percentage
    teamAWinPct = (teamAWins / numSimulations) * 100
    teamBWinPct = (teamBWins / numSimulations) * 100

    # Calculate average effects
    avgEffects = {}
    for effect in effectTotals:
        avgEffects[effect] = round((effectTotals[effect] / numSimulations) * 10) / 10

    # Analyze the distribution of margins
    marginBuckets = {
        "1-5 points": 0,
        "6-10 points": 0,
        "11-15 points": 0,
        "16-20 points": 0,
        "21+ points": 0
    }

    for game in results:
        if game["margin"] <= 5:
            marginBuckets["1-5 points"] += 1
        elif game["margin"] <= 10:
            marginBuckets["6-10 points"] += 1
        elif game["margin"] <= 15:
            marginBuckets["11-15 points"] += 1
        elif game["margin"] <= 20:
            marginBuckets["16-20 points"] += 1
        else:
            marginBuckets["21+ points"] += 1

    # Calculate margin distribution percentages
    marginDistribution = {}
    for range_, count in marginBuckets.items():
        marginDistribution[range_] = {
            "count": count,
            "percentage": round((count / numSimulations) * 1000) / 10
        }

    # Return comprehensive simulation results
    return {
        "numSimulations": numSimulations,
        "teamAWins": teamAWins,
        "teamBWins": teamBWins,
        "teamAWinPct": round(teamAWinPct * 10) / 10,
        "teamBWinPct": round(teamBWinPct * 10) / 10,
        "avgScoreA": avgScoreA,
        "avgScoreB": avgScoreB,
        "closestGame": closestGame,
        "blowoutGame": blowoutGame,
        "marginDistribution": marginDistribution,
        "avgEffects": avgEffects
    }

def simulate_game(team_analysis: Dict[str, Any], opponent_analysis: Dict[str, Any], use_local: bool = False) -> Dict[str, Any]:
    """
    Simulate a game between two teams using either local calculations or Claude API
    
    Args:
        team_analysis: Dictionary containing our team analysis
        opponent_analysis: Dictionary containing opponent team analysis
        use_local: Whether to use local simulation instead of Claude API
        
    Returns:
        Dictionary containing simulation results
    """
    if use_local:
        return simulate_game_locally(team_analysis, opponent_analysis)
        
    # Load prompt template
    prompt_path = os.path.join("app/prompts", "game_simulation_prompt.txt")
    with open(prompt_path, "r") as file:
        prompt_template = file.read()
    
    # Create combined analysis for the prompt
    combined_analysis = {
        "team": team_analysis,
        "opponent": opponent_analysis
    }
    
    # Create message
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=4000,
        temperature=0.2,  # Slightly higher temperature for simulation variety
        system="You are an expert basketball analyst and simulator. You are simulating a game between two basketball teams based on their statistics.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_template + "\n\n" + json.dumps(combined_analysis, indent=2)
                    }
                ]
            }
        ]
    )
    
    # Extract and parse JSON from response
    try:
        # Look for JSON in the response
        response_text = message.content[0].text
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
        else:
            # If no JSON found, return empty dict
            return {}
    except Exception as e:
        print(f"Error parsing JSON from Claude response: {e}")
        return {}
